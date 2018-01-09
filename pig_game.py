'''
Dice game - Pig.
'''

from collections import namedtuple

other = [1, 0]
State = namedtuple('State', 'p me you pending')

# States are represented as a tuple of (p, me, you, pending) where
# p:       an int, 0 or 1, indicating which player's turn it is.
# me:      an int, the player-to-move's current score
# you:     an int, the other player's current score.
# pending: an int, the number of points accumulated on current turn, not yet scored


def hold(state):
    """Apply the hold action to a state to yield a new state:
    Reap the 'pending' points and it becomes the other player's turn."""
    return other[state.p], state.you, state.me + state.pending, 0


def roll(state, d):
    """Apply the roll action to a state (and a die roll d) to yield a new state:
    If d is 1, get 1 point (losing any accumulated 'pending' points),
    and it is the other player's turn. If d > 1, add d to 'pending' points."""
    return (other[state.p], state.you, state.me + d, 0) if d == 1 else (state.p, state.me, state.you, state.pending + d)


def test():
    "tests."
    assert hold(State(1, 10, 20, 7)) == State(0, 20, 17, 0)
    assert hold(State(0, 5, 15, 10)) == State(1, 15, 15, 0)
    assert roll(State(1, 10, 20, 7), 1) == State(0, 20, 11, 0)
    assert roll(State(0, 5, 15, 10), 5) == State(0, 5, 15, 15)
    print('tests pass')


if __name__ == '__main__':
    test()
