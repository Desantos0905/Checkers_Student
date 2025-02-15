from random import randint
import time
import copy
from BoardClasses import Move
from BoardClasses import Board
import math


class StudentAI():
    def __init__(self,col,row,p):
        self.col = col
        self.row = row
        self.p = p
        self.board = Board(col,row,p)
        self.board.initialize_game()
        self.color = ''
        self.opponent = {1:2,2:1}
        self.color = 2

    def get_move(self,move, remaining_time = 480):
        #not first move, opponent is making move 
        if len(move) != 0 and not (len(move) == 1 and move[0] == (-1, -1)):
            self.board.make_move(move, self.opponent[self.color])
        #first move indicator, update color to be 1 
        else:
            self.color = 1


        mcts = MCTS(copy.deepcopy(self.board), self.color, self.opponent)
        best_move = mcts.get_best_move()

        #if not enough time left, pick random moves 
        if remaining_time < 3:
            possible_moves = self.board.get_all_possible_moves(self.color)
            if possible_moves:
                random_group = possible_moves[randint(0, len(possible_moves) - 1)]
                best_move = random_group[randint(0, len(random_group) - 1)]
            else:
                best_move = Move([])
            self.board.make_move(best_move, self.color)
            return best_move
        
        #maintain a buffer of time before we need to start making random moves 
        simulation_time = remaining_time - 3 
        mcts = MCTS(copy.deepcopy(self.board), self.color, self.opponent)
        best_move = mcts.get_best_move(simulation_time=simulation_time, max_iterations=1000)

        self.board.make_move(best_move, self.color)
        return best_move

class Node:
    def __init__(self, board_state, parent=None, move=None, player_color=None):
        self.board_state = board_state
        self.parent = parent
        self.move = move
        self.children = []
        self.wins = 0
        self.visits = 0
        self.player_color = player_color

        # Flatten the nested move list structure
        self.untried_moves = []
        moves_list = board_state.get_all_possible_moves(player_color)
        for move_group in moves_list:
            for move in move_group:
                self.untried_moves.append(move)

    def uct_value(self, exploration_constant=1.414):
        if self.visits == 0:
            return float('inf')
        return (self.wins / self.visits) + exploration_constant * math.sqrt(math.log(self.parent.visits) / self.visits)

class MCTS:
    def __init__(self, board, player_color, opponent_map):
        self.root = Node(board, player_color=player_color)
        self.opponent_map = opponent_map

    def select_node(self):
        current = self.root
        
        #nothing to explore, have children with diff UCT values, pick child with max UCT value
        while current.untried_moves == [] and current.children != []:
            current = max(current.children, key=lambda n: n.uct_value())
        return current

    def expand_node(self, node):
        if node.untried_moves:
            move = node.untried_moves.pop()
            #make a copy of the board state and try out a random move 
            new_board = copy.deepcopy(node.board_state)
            new_board.make_move(move, node.player_color)
            #find out color of the next player to keep track of turns in the child node
            next_color = self.opponent_map[node.player_color] if isinstance(node.player_color, int) else node.player_color
            child = Node(new_board, parent=node, move=move, player_color=next_color)
            node.children.append(child)
            #keep building the tree
            return child
        return node

    def simulate(self, node):
        sim_board = copy.deepcopy(node.board_state)
        current_color = node.player_color
        move_count = 0
        start_time = time.time() 
        max_moves = 1000

        while move_count < max_moves and (time.time() - start_time) < 20:
            winner = sim_board.is_win(current_color)
            if winner != 0:
                return winner

            possible_moves = sim_board.get_all_possible_moves(current_color)
            if not possible_moves:
                break

            move_group = possible_moves[randint(0, len(possible_moves)-1)]
            move = move_group[randint(0, len(move_group)-1)]
            sim_board.make_move(move, current_color)
            current_color = self.opponent_map[current_color] if isinstance(current_color, int) else current_color
            move_count += 1

        return 0

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            if result == -1 or (node.player_color == 'B' and result == 1) or (node.player_color == 'W' and result == 2):
                # Treat a tie as a win.
                node.wins += 1
            node = node.parent

    def get_best_move(self, simulation_time=1.0, max_iterations=1000):
        start_time = time.time()
        iterations = 0

        while (time.time() - start_time < simulation_time) and (iterations < max_iterations):
            selected_node = self.select_node()
            expanded_node = self.expand_node(selected_node)
            simulation_result = self.simulate(expanded_node)
            self.backpropagate(expanded_node, simulation_result)
            iterations += 1

        if self.root.children:
            best_child = max(self.root.children, key=lambda c: c.visits)
            return best_child.move
        else:
            #no child nodes, choose a random move 
            legal_moves = []
            moves_list = self.root.board_state.get_all_possible_moves(self.root.player_color)
            for group in moves_list:
                for m in group:
                    legal_moves.append(m)
            return legal_moves[randint(0, len(legal_moves) - 1)] if legal_moves else Move([])