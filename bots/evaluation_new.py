from bots.evaluation import Evaluation

class EvaluationNew(Evaluation):

	def evaluate_window(self, board, window):
		score = 0
		if window.count(self.bot_piece) == 4:
			score += 100
		elif window.count(self.bot_piece) == 3 and window.count(board.EMPTY) == 1:
			score += 5
		elif window.count(self.bot_piece) == 2 and window.count(board.EMPTY) == 2:
			score += 2

		if window.count(self.opp_piece) == 4:
			score -= 100
		elif window.count(self.opp_piece) == 3 and window.count(board.EMPTY) == 1:
			score -= 5
		elif window.count(self.opp_piece) == 2 and window.count(board.EMPTY) == 2:
			score -= 2

		return score
