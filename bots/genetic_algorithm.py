import random
import math
from bots.evaluation import Evaluation

class GeneticAlgorithmBot(Evaluation) :
    """
    Genetic Algorithm for Connect 4
    Note :
    GA is not suited for adversary tasks. 
    It is more suited for single-agent path-irrelevant optimization problems.
    
    Adjustments made to adapt GA for Connect 4:
    Fixed number of moves ahead to consider.
    
    Idea for a gene representation:
    Each individual in the population represents a sequence of moves.    
    
    Adversary model :
    The adversary is modeled as taking a move that maximize its own fitness.
    
    """
    
    def __init__(self, 
                 piece, 
                 population_size=20, 
                 generations=50, 
                 mutation_rate=0.1,
                 sequence_length=6):
        """
        Args:
            piece: The player's piece (1 or 2)
            population_size: Number of individuals in each generation
            generations: Number of loop
            mutation_rate: Probability of gene mutation
            sequence_length: Number of moves to look ahead
        """
        super().__init__(piece)
        self.piece = piece
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.sequence_length = sequence_length
        self.opponent_piece = 2 if piece == 1 else 1
    
    def get_move(self, board):
        """
        Main GA Loop
        """
        # Initialize random population of move sequences
        population = self.initialize_population(board)
        
        # Evolve population over generations
        for generation in range(self.generations):
            fitness_scores = self.evaluate_population(board, population)
            population = self.select_and_breed(population, fitness_scores)
            self.mutate_population(population)
        
        # Return first move of the best sequence
        best_move = self.get_best_move(board, population)
        return best_move
        
    def initialize_population(self, board):
        """
        Create initial population of random move sequences
        Only includes valid moves (columns that aren't full)
        """
        population = []
        valid_moves = board.get_valid_locations()
        
        for _ in range(self.population_size):
            # Each individual is a sequence of moves
            individual = [random.choice(valid_moves) for _ in range(self.sequence_length)]
            population.append(individual)
        return population
    
    def evaluate_population(self, board, population):
        """
        Calculate fitness score for each individual in population
        """
        fitness_scores = []
        for individual in population:
            score = self.calculate_fitness(board, individual)
            fitness_scores.append(score)
        return fitness_scores
    
    def calculate_fitness(self, board, individual):
        """
        Fitness function that evaluates a sequence of moves
        """
        temp_board = board.copy_board()
        for move in individual:
            if temp_board.is_valid_location(move):
                temp_board.drop_piece(move, self.piece)
                
                # Opponent's turn - assume opponent plays optimally
                opponent_moves = temp_board.get_valid_locations()
                if opponent_moves:
                    best_opp_move = None
                    best_opp_score = -math.inf
                    for opp_move in opponent_moves:
                        test_board = temp_board.copy_board()
                        test_board.drop_piece(opp_move, self.opponent_piece)
                        score = self.score_position(test_board)
                        if score > best_opp_score:
                            best_opp_score = score
                            best_opp_move = opp_move
                    if best_opp_move is not None:
                        temp_board.drop_piece(best_opp_move, self.opponent_piece)
            else:
                # Invalid move penalization
                return -1000
        score = self.score_position(temp_board)
        return score
    
    def has_m1_state(self, board, piece):
        """
        Check if board has M-1 state: two or more connect-3s
        At this state, player is guaranteed to win
        """
        connect_3_count = 0
        
        # Check all possible windows for connect-3 with one empty space
        for row in range(board.ROW_COUNT):
            for col in range(board.COLUMN_COUNT):
                # Check horizontal, vertical, and diagonal directions
                if self.count_connect_3(board, row, col, piece):
                    connect_3_count += 1
                    if connect_3_count >= 2:
                        return True
        return False
    
    
    def select_and_breed(self, population, fitness_scores):
        """
        Selection and crossover:
        - Use fitness-proportionate selection (roulette wheel)
        - Perform single-point crossover between pairs
        """
        # Handle negative fitness scores by shifting all scores to positive
        min_fitness = min(fitness_scores)
        adjusted_scores = [score - min_fitness + 0.1 for score in fitness_scores]
        
        # Select parents based on fitness
        selected = random.choices(
            population, weights=adjusted_scores, k=self.population_size)
        
        next_generation = []
        
        # Create offspring through crossover
        for i in range(0, self.population_size, 2):
            parent1 = selected[i]
            parent2 = selected[i+1] if i+1 < len(selected) else selected[0]
            
            # Single-point crossover
            crossover_point = random.randint(1, len(parent1)-1)
            child1 = parent1[:crossover_point] + parent2[crossover_point:]
            child2 = parent2[:crossover_point] + parent1[crossover_point:]
            
            next_generation.extend([child1, child2])
        
        return next_generation[:self.population_size]
    
    def mutate_population(self, population):
        """
        Apply mutation to population
        Each gene has mutation_rate chance to change to a random valid column
        """
        for individual in population:
            for i in range(len(individual)):
                if random.random() < self.mutation_rate:
                    # Mutate to a random column (0-6 for Connect 4)
                    individual[i] = random.randint(0, 6)
                    
    def get_best_move(self, board, population):
        """
        Return the first move of the individual with highest fitness
        """
        fitness_scores = self.evaluate_population(board, population)
        best_index = fitness_scores.index(max(fitness_scores))
        best_individual = population[best_index]
        
        # Return first move, ensure it's valid
        first_move = best_individual[0]
        valid_moves = board.get_valid_locations()
        
        if first_move in valid_moves:
            return first_move
        else:
            # Fallback to any valid move
            return random.choice(valid_moves)
    
    
    