'''
Dice game - Pig.
'''

import random

other = [1, 0]
goal = 50

# States are represented as a tuple of (p, me, you, pending) where
# p:       an int, 0 or 1, indicating which player's turn it is.
# me:      an int, the player-to-move's current score
# you:     an int, the other player's current score.
# pending: an int, the number of points accumulated on current turn, not yet scored


def play_pig(A, B):
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
            state = roll(state, random.randint(1, 6))
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
    print('pig game tests pass')


if __name__ == '__main__':
    test()
    test_pig_game()
