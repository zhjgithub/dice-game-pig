'''
Dice game - Pig.
'''

import random
from decorator import memo

other = [1, 0]
goal = 40

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

        action = strategies[p](state)
        if action == 'roll':
            state = roll(state, next(dierolls))
        elif action == 'hold':
            state = hold(state)
        else:
            # illegal action, lose!
            return strategies[other[p]]


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


def max_wins(state):
    "The optimal pig strategy chooses an action with the highest win probability."
    return best_action(state, pig_actions, Q_pig, Pwin)


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


def Pwin2(state):
    """The utility of a state; here just the probability that an optimal player
   whose turn it is to move can win from the current state."""
    _, me, you, pending = state
    return Pwin3(me, you, pending)


@memo
def Pwin3(me, you, pending):
    '''
    The probability of winning for player to play with score me to you, and pending.
    '''
    if me + pending >= goal:
        return 1
    if you >= goal:
        return 0
    p_roll = (1 - Pwin3(you, me + 1, 0) + sum(
        Pwin3(me, you, pending + d) for d in (2, 3, 4, 5, 6))) / 6
    if pending:
        return max(p_roll, 1 - Pwin3(you, me + pending, 0))
    else:
        return p_roll


def best_action(state, actions, Q, U):
    "Return the optimal action for a state, given U."

    def EU(action):
        "Expected utility."
        return Q(state, action, U)

    return max(actions(state), key=EU)


@memo
def win_diff(state):
    "The utility of a state: here the winning differential (pos or neg)."
    (p, me, you, pending) = state
    if me + pending >= goal or you >= goal:
        return (me + pending - you)
    else:
        return max(
            Q_pig(state, action, win_diff) for action in pig_actions(state))


def max_diffs(state):
    """A strategy that maximizes the expected difference between my final score
    and my opponent's."""
    return best_action(state, pig_actions, Q_pig, win_diff)


def test():
    "tests."
    assert hold((1, 10, 20, 7)) == (0, 20, 17, 0)
    assert hold((0, 5, 15, 10)) == (1, 15, 15, 0)
    assert roll((1, 10, 20, 7), 1) == (0, 20, 11, 0)
    assert roll((0, 5, 15, 10), 5) == (0, 5, 15, 15)

    assert goal == 50  # hold_at tests use goal equal 50
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


def test_max_wins():
    "max wins tests"
    assert goal == 40  # max_wins tests use goal equal 50
    assert (max_wins((1, 5, 34, 4))) == "roll"
    assert (max_wins((1, 18, 27, 8))) == "roll"
    assert (max_wins((0, 23, 8, 8))) == "roll"
    assert (max_wins((0, 31, 22, 9))) == "hold"
    assert (max_wins((1, 11, 13, 21))) == "roll"
    assert (max_wins((1, 33, 16, 6))) == "roll"
    assert (max_wins((1, 12, 17, 27))) == "roll"
    assert (max_wins((1, 9, 32, 5))) == "roll"
    assert (max_wins((0, 28, 27, 5))) == "roll"
    assert (max_wins((1, 7, 26, 34))) == "hold"
    assert (max_wins((1, 20, 29, 17))) == "roll"
    assert (max_wins((0, 34, 23, 7))) == "hold"
    assert (max_wins((0, 30, 23, 11))) == "hold"
    assert (max_wins((0, 22, 36, 6))) == "roll"
    assert (max_wins((0, 21, 38, 12))) == "roll"
    assert (max_wins((0, 1, 13, 21))) == "roll"
    assert (max_wins((0, 11, 25, 14))) == "roll"
    assert (max_wins((0, 22, 4, 7))) == "roll"
    assert (max_wins((1, 28, 3, 2))) == "roll"
    assert (max_wins((0, 11, 0, 24))) == "roll"

    # The first three test cases are examples where max_wins and
    # max_diffs return the same action.
    assert (max_diffs((1, 26, 21, 15))) == "hold"
    assert (max_diffs((1, 23, 36, 7))) == "roll"
    assert (max_diffs((0, 29, 4, 3))) == "roll"
    # The remaining test cases are examples where max_wins and
    # max_diffs return different actions.
    assert (max_diffs((0, 36, 32, 5))) == "roll"
    assert (max_diffs((1, 37, 16, 3))) == "roll"
    assert (max_diffs((1, 33, 39, 7))) == "roll"
    assert (max_diffs((0, 7, 9, 18))) == "hold"
    assert (max_diffs((1, 0, 35, 35))) == "hold"
    assert (max_diffs((0, 36, 7, 4))) == "roll"
    assert (max_diffs((1, 5, 12, 21))) == "hold"
    assert (max_diffs((0, 3, 13, 27))) == "hold"
    assert (max_diffs((0, 0, 39, 37))) == "hold"

    epsilon = 0.0001  # used to make sure that floating point errors don't cause test() to fail
    assert len(Pwin3.cache) <= 50000
    assert Pwin2((0, 42, 25, 0)) == 1
    assert Pwin2((1, 12, 43, 0)) == 0
    assert Pwin2((0, 34, 42, 1)) == 0
    assert abs(Pwin2((0, 25, 32, 8)) - 0.736357188272) <= epsilon
    assert abs(Pwin2((0, 19, 35, 4)) - 0.493173612834) <= epsilon

    print('max win tests success')


if __name__ == '__main__':
    # test()
    test_pig_game()
    test_max_wins()
