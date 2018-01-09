'''
Conditional probability.
'''

import itertools
from fractions import Fraction

sex = 'BG'


def product(*variables):
    "The cartesian product (as a str) of the possibilities of each variable."
    return map(''.join, itertools.product(*variables))


two_kids = list(product(sex, sex))
one_boy = [s for s in two_kids if 'B' in s]

# Out of all families with two kids with at least oen boy on a Tuesday,
# what is the probability of two boys?
day = 'SMTWtFs'  # days of week
two_kids_bday = list(product(sex, day, sex, day))
boy_tuesday = [s for s in two_kids_bday if 'BT' in s]


def two_boys(s):
    return s.count('B') == 2


def condP(predicate, event):
    '''Conditional probability: P(predicate(s) | s in event).
    The proportion of states in event for which predicate is true.
    '''
    pred = [s for s in event if predicate(s)]
    return Fraction(len(pred), len(event))


boy_anyday = [s for s in two_kids_bday if 'B' in s]
month = 'JFMAmjLaSOND'
two_kids_bmonth = product(sex, month, sex, month)
boy_december = [s for s in two_kids_bmonth if 'BD' in s]


def report(verbose=False,
           predicate=two_boys,
           predname='2 boys',
           cases=[('2 kids', two_kids), ('2 kids born any day', two_kids_bday),
                  ('at least 1 boy',
                   one_boy), ('at least 1 boy born any day', boy_anyday), (
                       'at least 1 boy born on Tuesday', boy_tuesday), (
                           'at least 1 boy born in December', boy_december)]):
    import textwrap
    for name, event in cases:
        print(
            'P({} | {}) = {}'.format(predname, name, condP(predicate, event)))
        if verbose:
            print('Reason:\n"{}" has {} elements:\n{}'.format(
                name, len(event), textwrap.fill(' '.join(event), 85)))
            good = [s for s in event if predicate(s)]
            print('of those, {} are "{}":\n{}\n\n'.format(
                len(good), predname, textwrap.fill(' '.join(good), 85)))


if __name__ == '__main__':
    print(condP(two_boys, one_boy))
    print(condP(two_boys, boy_tuesday))
    report(True)
