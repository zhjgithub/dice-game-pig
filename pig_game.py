'''
Dice game - Pig.
'''

import random
from decorator import memo

other = [1, 0]
goal = 50

# States are represented as a tuple of (p, me, you, pending) where
# p:       an int, 0 or 1, indicating which player's turn it is.
# me:      an int, the player-to-move's current score
# you:     an int, the other player's current score.
# pending: an int, the number of points accumulated on current turn, not yet scored


def die_rolls():
    "Generate die rolls"
    while True:
        yield random.randint(1, 6)


def play_pig(A, B, dierolls=die_rolls()):
    """Play a game of pig between two players, represented by their strategies.
    Each time through the main loop we ask the current player for one decision,
    which must be 'hold' or 'roll', and we update the state accordingly.
    When one player's score exceeds the goal, return that player."""
    strategies = [A, B]
    state = (0, 0, 0, 0)

    while True:
        p, me, you, _ = state

        if me >= goal:
            return strategies[p]
        if you >= goal:
            return strategies[other[p]]

        if strategies[p](state) == 'roll':
            state = roll(state, next(dierolls))
        else:
            state = hold(state)


def hold(state):
    """Apply the hold action to a state to yield a new state:
    Reap the 'pending' points and it becomes the other player's turn."""
    p, me, you, pending = state
    return other[p], you, me + pending, 0


def roll(state, d):
    """Apply the roll action to a state (and a die roll d) to yield a new state:
    If d is 1, get 1 point (losing any accumulated 'pending' points),
    and it is the other player's turn. If d > 1, add d to 'pending' points."""
    p, me, you, pending = state
    return (other[p], you, me + d, 0) if d == 1 else (p, me, you, pending + d)


def hold_at(x):
    """Return a strategy that holds if and only if
    pending >= x or player reaches goal."""

    def strategy(state):
        _, me, _, pending = state
        return 'hold' if pending >= x or me + pending >= goal else 'roll'

    strategy.__name__ = 'hold_at(%d)' % x
    return strategy


def Q_pig(state, action, Pwin):
    "The expected value of choosing action in state."
    if action == 'hold':
        return 1 - Pwin(hold(state))
    if action == 'roll':
        return (1 - Pwin(roll(state, 1)) + sum(
            Pwin(roll(state, d)) for d in (2, 3, 4, 5, 6))) / 6
    raise ValueError


def pig_actions(state):
    "The legal actions from a state."
    _, _, _, pending = state
    return ['roll', 'hold'] if pending else ['roll']


@memo
def Pwin(state):
    '''
    The utility of a state; here just the probability that an optimal player
    whose turn it is to move can win from the current state.
    '''
    # Assumes opponent also plays with optimal strategy.
    p, me, you, pending = state
    if me + pending >= goal:
        return 1
    if you >= goal:
        return 0
    return max(Q_pig(state, action, Pwin) for action in pig_actions(state))


def best_action(state, actions, Q, U):
    "Return the optimal action for a state, given U."

    def EU(action):
        "Expected utility."
        return Q(state, action, U)

    return max(actions(state), key=EU)


def test():
    "tests."
    assert hold((1, 10, 20, 7)) == (0, 20, 17, 0)
    assert hold((0, 5, 15, 10)) == (1, 15, 15, 0)
    assert roll((1, 10, 20, 7), 1) == (0, 20, 11, 0)
    assert roll((0, 5, 15, 10), 5) == (0, 5, 15, 15)

    assert hold_at(30)((1, 29, 15, 20)) == 'roll'
    assert hold_at(30)((1, 29, 15, 21)) == 'hold'
    assert hold_at(15)((0, 2, 30, 10)) == 'roll'
    assert hold_at(15)((0, 2, 30, 15)) == 'hold'

    print('tests pass')


def test_pig_game():
    "Pig game tests."

    def always_roll(state):
        return 'roll'

    def always_hold(state):
        return 'hold'

    for _ in range(10):
        winner = play_pig(always_hold, always_roll)
        assert winner.__name__ == 'always_roll'

    def clueless(state):
        "A strategy that ignores the state and chooses at random from possible moves."
        return random.choice(['roll', 'hold'])

    A, B = hold_at(50), clueless
    rolls = iter([6] * 9)
    assert play_pig(A, B, rolls) == A

    print('pig game tests pass')


if __name__ == '__main__':
    test()
    test_pig_game()
