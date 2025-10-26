import random
import math
from bots.evaluation import Evaluation

class SimulatedAnnealingBot(Evaluation):
	ACCEPTANCE_PROBABILITY_TRESHOLD = 0.3
	LIMIT_CONSIDERABLE_SLOT_PERCENTAGE = 0.7
	WINNING_POINT = 100000000000000
	LOSING_POINT = -10000000000000
	K = 10
	def __init__(self, piece, depth=5):
		super().__init__(piece)
		self.depth = depth

	def simulated_annealing(self, board, depth, alpha, beta, maximizingPlayer):
		valid_locations = board.get_valid_locations()
		is_terminal = super().is_terminal_node(board)
		slots_filled = board.get_num_slots_filled()
		temperature = self.K * ((board.ROW_COUNT * board.COLUMN_COUNT) * self.LIMIT_CONSIDERABLE_SLOT_PERCENTAGE - slots_filled) / (board.ROW_COUNT * board.COLUMN_COUNT)
		

		if depth == 0 or is_terminal:
			if is_terminal:
				if board.winning_move(self.bot_piece):
					return (None, self.WINNING_POINT)
				elif board.winning_move(self.opp_piece):
					return (None, self.LOSING_POINT)
				else: # Game is over, no more valid moves
					return (None, 0)
			else: # Depth is zero
				return (None, super().score_position(board))

		if maximizingPlayer:
			value = self.LOSING_POINT
			column = random.choice(valid_locations)
			for col in valid_locations:
				b_copy = board.copy_board()
				b_copy.drop_piece(col, self.bot_piece)
				new_score = self.simulated_annealing(b_copy, depth-1, alpha, beta, False)[1]

				if new_score >= value:
					value = new_score
					column = col
				else:
					acceptance_prob = math.exp((new_score - value) / temperature)
					print("temperature:", temperature)
					print("acceptance_prob:", acceptance_prob)
					if self.ACCEPTANCE_PROBABILITY_TRESHOLD < acceptance_prob:
						value = new_score
						column = col

				alpha = max(alpha, value)
				if alpha >= beta:
					break
			return column, value
		else: # Minimizing player
			value = self.WINNING_POINT
			column = random.choice(valid_locations)
			for col in valid_locations:
				b_copy = board.copy_board()
				b_copy.drop_piece(col, self.opp_piece)
				new_score = self.simulated_annealing(b_copy, depth-1, alpha, beta, True)[1]

				if new_score <= value:
					value = new_score
					column = col
				else:
					print("value:", value)
					print("new_score:", new_score)
					acceptance_prob = math.exp((value - new_score) / temperature)
					print("temperature:", temperature)
					print("acceptance_prob:", acceptance_prob)
					if self.ACCEPTANCE_PROBABILITY_TRESHOLD < acceptance_prob:
						value = new_score
						column = col

				beta = min(beta, value)
				if alpha >= beta:
					break
			return column, value

	def get_move(self, board):
		col, simulated_annealing_score = self.simulated_annealing(board, self.depth, -math.inf, math.inf, True)
		return col