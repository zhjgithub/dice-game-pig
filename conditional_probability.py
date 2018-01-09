'''
Conditional probability.
'''

import itertools
from fractions import Fraction

sex = 'BG'


def product(*variables):
    "The cartesian product (as a str) of the possibilities of each variable."
    return map(''.join, itertools.product(*variables))


two_kids = product(sex, sex)
one_boy = [s for s in two_kids if 'B' in s]

# Out of all families with two kids with at least oen boy on a Tuesday,
# what is the probability of two boys?
day = 'SMTWtFs'  # days of week
two_kids_bday = product(sex, day, sex, day)
boy_tuesday = [s for s in two_kids_bday if 'BT' in s]


def two_boys(s):
    return s.count('B') == 2


def condP(predicate, event):
    '''Conditional probability: P(predicate(s) | s in event).
    The proportion of states in event for which predicate is true.
    '''
    pred = [s for s in event if predicate(s)]
    return Fraction(len(pred), len(event))


if __name__ == '__main__':
    print(condP(two_boys, one_boy))
    print(condP(two_boys, boy_tuesday))
