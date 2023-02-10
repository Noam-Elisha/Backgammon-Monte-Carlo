import random as r
import numpy as np

from sklearn import random_projection

def uniform():
    return r.randint(0,5)

class Board:

    def __init__(self, random_function = uniform):
        self.state = [0,0,0,0,0,0]
        self.remaining = 15
        for i in range(self.remaining):
            self.state[random_function()] += 1
    
    def move(self, start, n):
        assert 1 <= n <= 6, f"Invalid number of spaces (got {n})"
        assert self.state[start] >= 0, f"No pieces to move from there (space {start})"

        self.state[start] -= 1
        if start + n > 5:
            self.remaining -= 1
        else:
            self.state[start + n] += 1
        
    def reset(self):
        self.__init__()
    
    def __repr__(self):
        return str(self.state)
    
    def __str__(self):
        return str(self.state)

def simulate_endgame(board, policy):
    num_turns = 0
    states = []
    while board.remaining > 0:
        num_turns += 1
        dice = (r.randint(1, 6), r.randint(1, 6))
        moves = policy(board.state, dice)
        states.append({"states": board.state[:], "dice": dice, "moves": moves, "remaining": 15 - board.remaining})
        for move in moves:
            board.move(*move)
    
    return num_turns, states

def simulate_move(state, start, n):
    assert 1 <= n <= 6, f"Invalid number of spaces (got {n})"
    assert state[start] >= 0, f"No pieces to move from there (space {start})"

    rstate = state[:]
    rstate[start] -= 1
    if start + n > 5:
        pass
    else:
        rstate[start + n] += 1
    return rstate

def get_available_indices(state):
    return [i for i in range(len(state)) if state[i] > 0]

def random_policy(state, dice):
    indices = get_available_indices(state)
    move1 = (r.choice(indices), dice[0])
    state2 = simulate_move(state, *move1)
    indices = get_available_indices(state2)
    if len(indices) == 0:
        return [move1]
    move2 = (r.choice(indices), dice[1])
    movelist = [move1, move2]
    if dice[0] == dice[1]:
        state3 = simulate_move(state2, *move2)
        indices = get_available_indices(state3)
        if len(indices) == 0:
            return movelist
        move3 = (r.choice(indices), dice[0])
        state4 = simulate_move(state3, *move3)
        indices = get_available_indices(state4)
        if len(indices) == 0:
            return movelist + [move3]
        move4 = (r.choice(indices), dice[1])
        movelist += [move3, move4]
    return movelist

def last_first_policy(state, dice):
    indices = get_available_indices(state)
    move1 = (indices[0], dice[0])
    state2 = simulate_move(state, *move1)
    indices = get_available_indices(state2)
    if len(indices) == 0:
        return [move1]
    move2 = (indices[0], dice[1])
    movelist = [move1, move2]
    if dice[0] == dice[1]:
        state3 = simulate_move(state2, *move2)
        indices = get_available_indices(state3)
        if len(indices) == 0:
            return movelist
        move3 = (indices[0], dice[0])
        state4 = simulate_move(state3, *move3)
        indices = get_available_indices(state4)
        if len(indices) == 0:
            return movelist + [move3]
        move4 = (indices[0], dice[1])
        movelist += [move3, move4]
    return movelist

def equal_num_first_policy(state, dice):
    dice = sorted(dice)
    indices = get_available_indices(state)
    if 6 - dice[1] in indices:
        move1 = (6 - dice[1], dice[1])
        state2 = simulate_move(state, *move1)
    else:
        move1 = (get_available_indices(state)[0], dice[0])
        state2 = simulate_move(state, *move1)
    indices = get_available_indices(state2)
    if len(indices) == 0:
        return [move1]
    if 6 - dice[0] in indices:
        move2 = (6 - dice[0], dice[0])
        state3 = simulate_move(state2, *move2)
    else:
        move2 = (get_available_indices(state)[0], dice[0])
        state3 = simulate_move(state2, *move2)
    movelist = [move1, move2]

    if dice[0] == dice[1]:
        indices = get_available_indices(state3)
        if len(indices) == 0:
            return movelist
        if 6 - dice[1] in indices:
            move3 = (6 - dice[1], dice[1])
            state4 = simulate_move(state3, *move3)
        else:
            move3 = (get_available_indices(state3)[0], dice[0])
            state4 = simulate_move(state3, *move3)
        indices = get_available_indices(state4)
        if len(indices) == 0:
            return movelist + [move3]
        if 6 - dice[0] in indices:
            move4 = (6 - dice[0], dice[0])
        else:
            move4 = (get_available_indices(state4)[0], dice[0])
        movelist += [move3, move4]
    return movelist

def run_monte_carlo(num_iterations, policy):
    results = []
    logs = []
    board = Board()
    for i in range(num_iterations):
        board.reset()
        num_turns, log = simulate_endgame(board, policy)
        results.append(num_turns)
        logs.append(log)
    
    return results, logs


if __name__ == "__main__":
    r.seed(0)
    results, logs = run_monte_carlo(100000, random_policy)
    print("Random Policy:")
    print(f"mean: {np.mean(results)}")
    print(f"std: {np.std(results)}")

    results, logs = run_monte_carlo(100000, last_first_policy)
    print("Furthest Pieces First Policy:")
    print(f"mean: {np.mean(results)}")
    print(f"std: {np.std(results)}")

    results, logs = run_monte_carlo(100000, equal_num_first_policy)
    print("First Out Policy:")
    print(f"mean: {np.mean(results)}")
    print(f"std: {np.std(results)}")
