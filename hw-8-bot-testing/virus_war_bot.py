import argparse
import random
import sys
import numpy as np
from numpy import r_, ix_, roll


class VirusWarGame:
    def __init__(self, field, player, size=10):
        self.field = np.array([np.array(list(line.strip()), dtype=int) for line in field.splitlines()])
        self.possible_move = np.zeros((size, size), dtype=bool)
        self.in_killed_chain = np.zeros((size, size), dtype=bool)
        self.has_access_to_enemy = np.zeros((size, size), dtype=bool)
        self.player = player
        self.size = size

    def go(self):
        moves_success = True
        initial_field = self._field_to_str()
        for i in range(0, 3):
            if self.player == 1:
                moves_success = self._make_move([self.size - 1, 0], 1, 4, 2)
            else:
                moves_success = self._make_move([0, self.size - 1], 2, 3, 1)
        if moves_success:
            return self._field_to_str()
        else:
            return initial_field

    def _field_to_str(self):
        return '\n'.join([''.join([str(item) for item in row]) for row in self.field])

    def _make_move(self, start, me, killed, enemy):
        if self.field[start[0], start[1]] == 0:
            self.field[start[0], start[1]] = me
            return True
        self._find_possible_moves(me, killed, enemy)
        self._check_access(me, killed)
        return self._choose_move(me, killed, enemy)

    def _check_near(self, arr, val):
        indx = r_[0:self.size]
        up = roll(indx, -1)
        down = roll(indx, 1)

        def pad(init_arr, padding):
            return np.pad(init_arr, padding, mode='constant', constant_values=False)

        return np.logical_or.reduce((pad(arr[up, :][:-1] == val, [(0, 1), (0, 0)]),
                                    pad(arr[down, :][1:] == val, [(1, 0), (0, 0)]),
                                    pad(arr[:, up][:, :-1] == val, [(0, 0), (0, 1)]),
                                    pad(arr[:, down][:, 1:] == val, [(0, 0), (1, 0)]),
                                    pad(arr[ix_(up, up)][:-1, :-1] == val, [(0, 1), (0, 1)]),
                                    pad(arr[ix_(up, down)][:-1, 1:] == val, [(0, 1), (1, 0)]),
                                    pad(arr[ix_(down, up)][1:, :-1] == val, [(1, 0), (0, 1)]),
                                    pad(arr[ix_(down, down)][1:, 1:] == val, [(1, 0), (1, 0)])))

    def _find_possible_moves(self, me, killed, enemy):
        in_killed_chain = np.logical_and(self.field == killed, self._check_near(self.field, me))
        while not (in_killed_chain == self.in_killed_chain).all():
            self.in_killed_chain = in_killed_chain
            in_killed_chain = np.logical_or(np.logical_and(self.field == killed, self._check_near(in_killed_chain, True)), in_killed_chain)
        me_or_killed_chain = np.logical_or(self.field == me, self.in_killed_chain)
        empty_near_me = np.logical_and(self.field == 0, self._check_near(me_or_killed_chain, True))
        enemy_near_me = np.logical_and(self.field == enemy, self._check_near(me_or_killed_chain, True))
        self.possible_move = np.logical_or(empty_near_me, enemy_near_me)

    def _check_access(self, me, killed):
        has_access = np.logical_and(self.field != killed, self._check_near(self.field, me))
        while not (self.has_access_to_enemy == has_access).all():
            self.has_access_to_enemy = has_access
            has_access = np.logical_or(np.logical_and(self.field != killed, self._check_near(has_access, True)), has_access)

    def _choose_and_make_move(self, moves, value):
        ind = random.choice(np.argwhere(moves))
        self.field[ind[0], ind[1]] = value

    def _choose_move(self, me, killed, enemy):
        generate_moves = np.logical_and(self.possible_move, self.field == 0)
        kill_moves_with_access = np.logical_and(self.has_access_to_enemy, np.logical_and(self.possible_move, self.field == enemy))
        kill_moves = np.logical_and(self.possible_move, self.field == enemy)
        self.possible_move = False
        self.has_access_to_enemy = False
        if np.any(kill_moves_with_access):
            self._choose_and_make_move(kill_moves_with_access, killed)
        elif np.any(generate_moves):
            self._choose_and_make_move(generate_moves, me)
        elif np.any(kill_moves):
            self._choose_and_make_move(kill_moves, killed)
        else:
            return False
        return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', dest='print_name', action='store_true', required=False)
    args = parser.parse_args()

    if args.print_name:
        print('bot_by_kalina')
    else:
        field = ''
        field_size = 10
        for _ in range(0, field_size):
            field += sys.stdin.readline()
        game = VirusWarGame(field, int(sys.stdin.readline().strip()), field_size)
        result_field = game.go()
        print(result_field)
