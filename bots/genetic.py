import random
from bots.evaluation import Evaluation

class GeneticBot(Evaluation):
    def __init__(self, piece, pop_size=40, gene_len=6, generations=30, mutation_rate=0.1):
        super().__init__(piece)
        self.pop_size = pop_size
        self.gene_len = gene_len
        self.generations = generations
        self.mutation_rate = mutation_rate

    def get_move(self, board):
        valid = board.get_valid_locations()
        if not valid:
            return None

        # === INITIAL POPULATION ===
        population = [self._random_individual(board) for _ in range(self.pop_size)]

        # === REPEAT until done ===
        for _ in range(self.generations):
            fitness = [self._fitness(board, ind) for ind in population]
            new_population = []

            # === The pseudocode in your slide ===
            for _ in range(self.pop_size):
                # selection (roulette)
                x = self._random_selection(population, fitness)
                y = self._random_selection(population, fitness)

                # reproduce (one-point crossover)
                child = self._reproduce(x, y)

                # mutation
                if random.random() < self.mutation_rate:
                    child = self._mutate(child, board)

                new_population.append(child)

            population = new_population

        # return best individual
        fitness = [self._fitness(board, ind) for ind in population]
        best = population[fitness.index(max(fitness))]
        move = best[0] if best[0] in valid else random.choice(valid)
        return move

    def _random_individual(self, board):
        return [random.randrange(board.COLUMN_COUNT) for _ in range(self.gene_len)]

    def _fitness(self, board, chrom):
        WIN   = 1_000_000_000
        DECAY = 100_000_000 
        b = board.copy_board()
        
        for step_index, g in enumerate(chrom):
            valids = b.get_valid_locations()
            if not valids:
                break
            col = g if g in valids else random.choice(valids)
            b.drop_piece(col, self.bot_piece)
            if b.winning_move(self.bot_piece):
                return WIN - DECAY * step_index 
            
        return super().score_position(b)

    def _random_selection(self, population, fitness):
        # shift so non negative
        min_f = min(fitness)
        shift = (-min_f + 1) if min_f <= 0 else 0
        weights = [f + shift for f in fitness]
        total = sum(weights)
        
        if total <= 0:
            return random.choice(population)
        pick = random.uniform(0, total)
        current = 0
        for ind, fit in zip(population, fitness):
            current += fit
            if current >= pick:
                return ind
        return population[-1]

    def _reproduce(self, x, y):
        cut = random.randint(1, len(x) - 1)
        return x[:cut] + y[cut:]

    def _mutate(self, child, board):
        idx = random.randrange(len(child))
        child[idx] = random.randrange(board.COLUMN_COUNT)
        return child
