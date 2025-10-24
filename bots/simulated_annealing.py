import random
import math
from bots.evaluation import Evaluation

class SimulatedAnnealingBot(Evaluation):
	def __init__(self, piece, depth=5):
		super().__init__(piece)
		self.depth = depth

	def simulated_annealing(self, board, depth, alpha, beta, maximizingPlayer):
		

	def get_move(self, board):
		col, simulated_annealing_score = self.simulated_annealing(board, self.depth, -math.inf, math.inf, True)
		return col
