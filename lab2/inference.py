import json
import codecs
import sys
from collections import namedtuple

Fact = namedtuple('Fact', 'attr value')
Rule = namedtuple('Rule', 'r cond')


def load_db(filename):
    with codecs.open(filename, encoding='utf-8') as f:
        db = json.load(f)
    db['rules'] = [Rule(Fact(*i[0].split('=')), [Fact(*j.split('=')) for j in i[1]]) for i in db['rules']]
    db['rules_attr'] = {rule.r.attr for rule in db['rules']}
    db['facts'] = []
    return db


def get_rules(db, goal):
    return [rule for rule in db['rules'] if goal.attr == rule.r.attr]


def is_rule(db, fact):
    if fact.attr in db['rules_attr']:
        return True
    return False


def get_help(db, goal):
    options = db['options'][goal.attr] + [u'выход']
    prompt = u'%s? (%s): ' % (goal.attr.capitalize(), ', '.join(options))
    try:
        reply = input(prompt)
        while(reply not in options):
            print('Этот вариант ответа не предусмотрен.')
            reply = input(prompt)
        if reply == u'выход':
            raise KeyboardInterrupt
    except KeyboardInterrupt:
        sys.exit()
    db['facts'].append(Fact(goal.attr, reply))
    if goal.value == reply:
        return True
    return False


def prove_the_fact(db, fact):
    if fact in db['facts']:
        return True
    for dbfact in db['facts']:
        if fact.attr == dbfact.attr:
            return False
    return get_help(db, fact)


def prove_the_goal(db, goal):
    for rule in get_rules(db, goal):
        truthness = True
        for cond in rule.cond:
            if is_rule(db, cond):
                if not prove_the_goal(db, cond):
                    truthness = False
                    break
            elif not prove_the_fact(db, cond):
                truthness = False
                break
        if truthness:
            if not goal.value:
                return rule.r
            else:
                return True
    return False


if __name__ == '__main__':
    goal = prove_the_goal(load_db('rules1.json'), Fact(u'время года', ''))
    if goal:
        print(goal.attr.capitalize() + ' ' + goal.value + '.')
    else:
        print('Я не могу Вам помочь.')