import random
import numpy as np
import itertools
import re
from collections import Counter
from termcolor import colored, cprint

COLORS = ["Y", "C", "B", "G", "P", "R", "W"]
COLOR_DICT = {
    'Y': 'yellow',
    'C': 'cyan',
    'B': 'blue',
    'G': 'green',
    'P': 'magenta',
    'R': 'red',
    'W': 'grey'
}
COLOR_NUMBER = len(COLORS)
SIZE = 9


class Board:
    size = 0
    colors = None
    color_number = 0
    board = None
    binary_board = None
    legal_positions = None
    empty = None
    next_colors = None
    turn_no = 0
    score = 0
    clear_count = None
    visited = None
    input_mode = False
    board_states = None
    scores = None
    next_colors_list = None
    constants = [1, 2, 40, 120, 1000000]
    generated = 3

    def __init__(self, size, colors, color_number, board, score, constants):

        self.scores = []
        self.board_states = []
        self.next_colors_list = []

        if board is None:
            self.size = size
            self.colors = colors
            self.color_number = color_number
            self.clear_count = [0, 0, 0]
            self.turn_no = 0
            self.score = 0
            self.board = []
            self.binary_board = []
            self.visited = []
            self.legal_positions = []
            self.constants = constants
            for i in range(size):
                row = []
                binary_row = []
                visited_row = []
                for j in range(size):
                    row.append(str(i) + str(j) + ' ')
                    binary_row.append(0)
                    visited_row = False
                self.board.append(row)
                self.binary_board.append(binary_row)
                self.visited.append(visited_row)
            self.initialize_game_state()
        else:
            self.board = []
            self.score = score
            self.size = size
            self.colors = colors
            self.color_number = color_number
            self.visited = []
            self.binary_board = []
            for i in range(size):
                row = []
                binary_row = []
                visited_row = []
                for j in range(size):
                    row.append(board[i][j])
                    binary_row.append(0)
                    visited_row = False
                self.board.append(row)
                self.binary_board.append(binary_row)
                self.visited.append(visited_row)

        self.special_expressions = {}

        for color in self.colors:
            self.special_expressions["\s" + color + "{4}"] = 0
            self.special_expressions[color + "\s" + color + "{3}"] = 1
            self.special_expressions[color + "{2}" + "\s" + color + "{2}"] = 2
            self.special_expressions[color + "{3}" + "\s" + color + "{1}"] = 3
            self.special_expressions[color + "{4}" + "\s"] = 4

        self.regular_expressions = {}

        for color in self.colors:
            self.regular_expressions[color + "{2}"] = 2 ** self.constants[1]
            self.regular_expressions[color + "{3}"] = 6 ** self.constants[1]
            self.regular_expressions[color + "{4}"] = 12 ** self.constants[1]
            self.regular_expressions[color + "{5}"] = 1000000

    def initialize_game_state(self):
        for i in range(5):
            position = self.generate_position()
            color = self.generate_color()
            self.create_ball(position, color)

    def generate_position(self):
        self.get_empty()
        if len(self.empty) == 0:
            err = (-1, -1)
            return err
        else:
            return random.choice(self.empty)

    def generate_color(self):
        return random.choice(self.colors)

    def create_ball(self, position, color):
        self.board[position[0]][position[1]] = str(position[0]) + str(position[1]) + color

    def get_empty(self):
        self.empty = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j][2] == ' ':
                    self.empty.append((i, j))

    def get_non_empty(self, colors):
        non_empty = []
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j][2] in colors:
                    non_empty.append((i, j))
        return non_empty

    def get_binary_board(self):
        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j][2] != ' ':
                    self.binary_board[i][j] = 1
                else:
                    self.binary_board[i][j] = 0

    def dfs_get_positions(self, position):
        if not self.visited[position[0]][position[1]]:
            self.legal_positions.append(position)
            self.visited[position[0]][position[1]] = True
            neighbours = [
                (position[0] - 1, position[1]),
                (position[0] + 1, position[1]),
                (position[0], position[1] - 1),
                (position[0], position[1] + 1)
            ]

            legal_neighbours = []
            for neighbour in neighbours:
                if 0 <= neighbour[0] < self.size and 0 <= neighbour[1] < self.size:
                    if self.binary_board[neighbour[0]][neighbour[1]] == 0:
                        legal_neighbours.append(neighbour)
            for neighbour in legal_neighbours:
                self.dfs_get_positions(neighbour)

    def get_legal_positions(self, position):
        self.legal_positions = []
        self.visited = []
        self.get_binary_board()
        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(False)
            self.visited.append(row)
        self.dfs_get_positions(position)
        self.legal_positions.remove(position)
        return len(self.legal_positions)

    def generate_next_colors(self):
        return [self.generate_color() for i in range(self.generated)]

    def generate_next_positions(self):
        return [self.generate_position() for i in range(self.generated)]

    def print(self):
        print(' 1●2●3●4●5●6●7●8●9●')
        for i, row in enumerate(self.board):
            print(i + 1, end= ' ')
            for element in row:
                if element[2] == ' ':
                    text = colored('● ', 'white', 'on_white')
                    print(text, end='')
                else:
                    color = COLOR_DICT[element[2]]
                    text = colored('● ', color, 'on_white')
                    print(text, end='')
            print('')

    def get_columns(self):
        columns = []
        matrix = np.array(self.board)
        for i in range(self.size):
            columns.append(matrix[:, i])
        return columns

    def get_diagonals(self):
        matrix = np.array(self.board)

        diagonals = [matrix[::-1, :].diagonal(i) for i in range(-(self.size - 1), self.size)]
        diagonals.extend(matrix.diagonal(i) for i in range(self.size - 1, - self.size, -1))
        d = []
        for n in diagonals:
            diagonal_list = n.tolist()
            if len(diagonal_list) >= 5:
                d.append(diagonal_list)
        return d

    def check_for_fives(self):
        found = False
        for column in self.get_columns():
            max_column = self.find_fives(column)
            if max_column > 0:
                found = True
                self.score += max_column
        for row in self.board:
            max_row = self.find_fives(row)
            if max_row > 0:
                found = True
                self.score += max_row
        for diagonal in self.get_diagonals():
            max_diagonal = self.find_fives(diagonal)
            if max_diagonal > 0:
                found = True
                self.score += max_diagonal
        return found

    def print_next_colors(self, next_colors):
        for next_color in next_colors:
            color = COLOR_DICT[next_color]
            text = colored('●', color)
            print(text, end=' ')
        print('')

    def automatic_turn(self, debug):
        self.turn_no += 1

        board_copy = []

        for i in range(self.size):
            row = []
            for j in range(self.size):
                row.append(self.board[i][j])
            board_copy.append(row)

        self.board_states.append(board_copy)
        self.scores.append(self.score)

        if debug:
            print("Score: " + str(self.score) + " / " + str(len(self.get_non_empty(self.colors))))
            print("Turn " + str(self.turn_no))
            print("Fitness: " + str(self.connected_fitness()))

        if self.next_colors is None:
            self.next_colors = self.generate_next_colors()

        next_colors_copy = []
        for i in range(self.generated):
            next_colors_copy.append(self.next_colors[i])

        self.next_colors_list.append(next_colors_copy)

        if debug:
            self.print()
            self.print_next_colors(self.next_colors)

        non_empty = self.get_non_empty(self.colors)
        choice_data = []
        legal_moves = 0
        for start_position in non_empty:
            color = self.board[start_position[0]][start_position[1]][2]
            legal_moves += self.get_legal_positions(start_position)
            for end_position in self.legal_positions:
                test_board = Board(self.size, self.colors, self.color_number, self.board, self.score, self.constants)
                final_score = test_board.test_turn(start_position, end_position, color)
                choice_data.append([(start_position, end_position), final_score])
                # test_board.print()
                # print(final_score)
        if debug:
            print("Moves: " + str(legal_moves))

        if legal_moves == 0:
            return self.score

        choice_data.sort(key=lambda x: x[1])
        choice_data.reverse()
        best_score = choice_data[0][1]
        best_choices = list(filter(lambda x: x[1] == best_score, choice_data))

        choice = random.choice(best_choices)
        self.create_ball(choice[0][1], self.board[choice[0][0][0]][choice[0][0][1]][2])
        self.create_ball(choice[0][0], ' ')

        found_fives = self.check_for_fives()

        if not found_fives:
            next_positions = self.generate_next_positions()

            for i in range(self.generated):
                if next_positions[i] != (-1, -1):
                    self.create_ball(next_positions[i], self.next_colors[i])
            self.next_colors = None
        return self.automatic_turn(debug)

    def test_turn(self, start_position, end_position, color):
        self.create_ball(end_position, color)
        self.create_ball(start_position, ' ')
        fitness = self.connected_fitness()
        self.check_for_fives()
        return fitness

    def manual_turn(self):
        self.turn_no += 1
        print("Turn " + str(self.turn_no))

        self.check_for_fives()

        print("Score: " + str(self.score))

        fitness = self.connected_fitness()
        print("Fitness: " + str(fitness))
        next_colors = self.generate_next_colors()
        self.print()
        self.print_next_colors(next_colors)

        row = -1
        column = -1
        target_row = -1
        target_column = -1

        while True:
            print("Enter the position of the ball: ", end='')
            string = input()
            if string == "auto":
                score = self.automatic_turn(True)
                print(score)
                return -1
            row = int(string[0]) - 1
            column = int(string[2]) - 1
            try:
                if self.board[row][column][2] != ' ':
                    break
                else:
                    print("Your choice is invalid, please try again")
            except:
                print("Index out of bounds")

        color = self.board[row][column][2]
        self.get_legal_positions((row, column))
        print(self.legal_positions)

        while True:
            print("Enter the target position: ", end='')
            string = input()
            target_row = int(string[0]) - 1
            target_column = int(string[2]) - 1
            try:
                if self.board[target_row][target_column][2] == ' ' and (target_row, target_column) in self.legal_positions:
                    break
                else:
                    print("Your choice is invalid, please try again")
            except:
                print("Index out of bounds")

        self.create_ball((target_row, target_column), color)
        self.create_ball((row, column), ' ')

        next_positions = self.generate_next_positions()

        if next_positions == [(-1, -1), (-1, -1), (-1, -1)]:
            return self.score

        for i in range(3):
            if next_positions[i] != (-1, -1):
                self.create_ball(next_positions[i], next_colors[i])

        if self.turn_no > 23:
            return self.score
        else:
            return self.manual_turn()

    def find_fives(self, input_list):   # Works only for sizes <= 9
        colors = [element[2] for element in input_list]
        occ_count = Counter(colors)
        most_common = occ_count.most_common(1)[0][0]
        if most_common != ' ':
            if occ_count.most_common(1)[0][1] > 4:
                max_index = -1
                index = 0
                max_length = -1
                length = 0
                for it in range(len(input_list)):
                    if length == 0:
                        if colors[it] == most_common:
                            length = 1
                            index = it
                    else:
                        if colors[it] == most_common:
                            length += 1
                        else:
                            length = 0

                    if max_length < length:
                        max_length = length
                        max_index = index

                if max_length >= 5:
                    for coord in range(max_index, max_index + max_length):
                        coords = input_list[coord][:2]
                        row = int(coords[0])
                        column = int(coords[1])
                        self.create_ball((row, column), ' ')
                    return max_length
                else:
                    return 0
            else:
                return 0
        else:
            return 0

    # FITNESS TESTS:
    def find_connected(self, input_list):
        if len(input_list) > 4:
            colors = [element[2] for element in input_list]
            color = ''
            sequences = [colors[0]]
            for it in range(1, len(colors)):
                color = colors[it]
                if color == sequences[-1][-1]:
                    sequences[-1] += color
                else:
                    sequences.append(color)
            fitness = 0

            for i, sequence in enumerate(sequences):
                if sequence[0] != ' ':
                    if len(sequence) > 4:
                        fitness += self.constants[4]
                    else:
                        fitness += self.constants[0] * ((len(sequence) - 1) * len(sequence)) ** self.constants[1]
                    if len(sequence) == 4:
                        special_case_color = sequence[0]
                        special_case_fields = []
                        start_point = 0
                        for j in range(i):
                            start_point += len(sequences[j])
                        end_point = start_point + 3

                        four_position = [
                            (int(input_list[i][0]), int(input_list[i][1])) for i in range(start_point, start_point + 4)
                        ]

                        if start_point != 0:
                            special_case_fields.append(input_list[start_point - 1])
                        if end_point != len(input_list) - 1:
                            special_case_fields.append(input_list[end_point + 1])
                        for field in special_case_fields:
                            if field[2] == ' ':
                                self.legal_positions = []
                                self.visited = []
                                self.get_binary_board()
                                for it_1 in range(self.size):
                                    row = []
                                    for it_2 in range(self.size):
                                        row.append(False)
                                    self.visited.append(row)
                                self.special_field_dfs((int(field[0]), int(field[1])))
                                self.legal_positions.remove((int(field[0]), int(field[1])))
                                neighbours = set()
                                for position in self.legal_positions:
                                    position_neighbours = [
                                        (position[0] - 1, position[1]),
                                        (position[0] + 1, position[1]),
                                        (position[0], position[1] - 1),
                                        (position[0], position[1] + 1)
                                    ]
                                    for neighbour in position_neighbours:
                                        if self.special_is_legal(neighbour):
                                            neighbours.add(neighbour)
                                for element in four_position:
                                    if element in neighbours:
                                        neighbours.remove(element)
                                reachable_from = []
                                for neighbour in list(neighbours):
                                    neighbour_color = self.board[neighbour[0]][neighbour[1]][2]
                                    if neighbour_color == special_case_color:
                                        fitness += self.constants[3]
                                        break
                    if len(sequence) == 3:
                        special_case_color = sequence[0]
                        special_case_fields = []
                        start_point = 0
                        for j in range(i):
                            start_point += len(sequences[j])
                        end_point = start_point + 2

                        three_position = [
                            (int(input_list[i][0]), int(input_list[i][1])) for i in range(start_point, start_point + 3)
                        ]

                        if start_point != 0:
                            special_case_fields.append(input_list[start_point - 1])
                        if end_point != len(input_list) - 1:
                            special_case_fields.append(input_list[end_point + 1])
                        for field in special_case_fields:
                            if field[2] == ' ':
                                self.legal_positions = []
                                self.visited = []
                                self.get_binary_board()
                                for it_1 in range(self.size):
                                    row = []
                                    for it_2 in range(self.size):
                                        row.append(False)
                                    self.visited.append(row)
                                self.special_field_dfs((int(field[0]), int(field[1])))
                                self.legal_positions.remove((int(field[0]), int(field[1])))
                                neighbours = set()
                                for position in self.legal_positions:
                                    position_neighbours = [
                                        (position[0] - 1, position[1]),
                                        (position[0] + 1, position[1]),
                                        (position[0], position[1] - 1),
                                        (position[0], position[1] + 1)
                                    ]
                                    for neighbour in position_neighbours:
                                        if self.special_is_legal(neighbour):
                                            neighbours.add(neighbour)
                                for element in three_position:
                                    if element in neighbours:
                                        neighbours.remove(element)
                                reachable_from = []
                                for neighbour in list(neighbours):
                                    neighbour_color = self.board[neighbour[0]][neighbour[1]][2]
                                    if neighbour_color == special_case_color:
                                        fitness += self.constants[2]
                                        break
        return fitness

    def special_is_legal(self, neighbour):
        if 0 <= neighbour[0] < self.size and 0 <= neighbour[1] < self.size:
            return True

    def special_field_dfs(self, position):
        if not self.visited[position[0]][position[1]]:
            self.legal_positions.append(position)
            self.visited[position[0]][position[1]] = True
            neighbours = [
                (position[0] - 1, position[1]),
                (position[0] + 1, position[1]),
                (position[0], position[1] - 1),
                (position[0], position[1] + 1)
            ]
            legal_neighbours = []
            for neighbour in neighbours:
                if 0 <= neighbour[0] < self.size and 0 <= neighbour[1] < self.size:
                    if self.binary_board[neighbour[0]][neighbour[1]] == 0:
                        legal_neighbours.append(neighbour)
            for neighbour in legal_neighbours:
                self.dfs_get_positions(neighbour)

    def connected_fitness(self):
        fitness = 0
        for column in self.get_columns():
            fitness += self.find_connected(column)
        for row in self.board:
            fitness += self.find_connected(row)
        for diagonal in self.get_diagonals():
            fitness += self.find_connected(diagonal)
        return fitness

    def print_states(self):
        for j in range(len(self.board_states)):
            board = self.board_states[j]
            print("Turn: " + str(j))
            print("Score: " + str(self.scores[j]))
            for i, row in enumerate(board):
                print(i + 1, end=' ')
                for element in row:
                    if element[2] == ' ':
                        text = colored('● ', 'white', 'on_white')
                        print(text, end='')
                    else:
                        color = COLOR_DICT[element[2]]
                        text = colored('● ', color, 'on_white')
                        print(text, end='')
                print('')
            self.print_next_colors(self.next_colors_list[j])
            print('')


CONST_ONE = [1, 5, 10]
CONST_TWO = [1, 2]
CONST_THREE = [10, 20, 40]
CONST_FOUR = [10, 40, 120, 1000]
CONST_FIVE = [1000000]
TESTS = 10

combinations = list(itertools.product(CONST_ONE, CONST_TWO, CONST_THREE, CONST_FOUR, CONST_FIVE))

COMBINATION = [1, 2, 25, 1000, 1000000]

for _ in range(TESTS):
    b = Board(SIZE, COLORS, COLOR_NUMBER, None, None, [1, 2, 40, 120, 1000000])
    count = b.automatic_turn(True)
    print(count)
    if count > 300:
        b.print_states()
    elif count >= 400:
        break
    del b
