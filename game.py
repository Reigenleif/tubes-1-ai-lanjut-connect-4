import argparse
import sys
import random

#pygame version number and welcome message hidden.
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"

import pygame
from bots import *
from board import *
from connect4 import connect4

bot_map = {
    'human': Human,
    'random': RandomBot,
    'onestep': OneStepLookAheadBot,
    'minimax': MiniMaxBot,
    'minimaxneweval': MiniMaxBotNewEval,
    'expectimax': ExpectiMaxBot,
    'montecarlo': MonteCarloBot,
    'genetic': GeneticAlgorithmBot,
    'simulated_annealing': SimulatedAnnealingBot
}

name_map = {
    'human': 'Human',
    'random': 'Random Bot',
    'onestep': 'One Step Look Ahead Bot',
    'minimax': 'MiniMax Bot',
    'minimaxneweval': 'MiniMax Bot with new evaluation function',
    'expectimax': 'ExpectiMax Bot',
    'montecarlo': 'Monte Carlo Tree Search Bot',
    'genetic': 'Genetic Algorithm Bot',
    'simulated_annealing': 'Simulated Annealing Bot'
}

board = Board(1)
TOTAL_GAMES = 10  # Number of games each pair of bots will play in competition mode

def str2bool(v):
    if isinstance(v, bool):
       return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')

def main(first_player = None, second_player = None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--p1', help='Player 1 type (default Human)', type=str)
    parser.add_argument('--p2', help='Player 2 type (default Human)', type=str)
    parser.add_argument('--ui', help='turn UI off in case of a bot vs bot match', type=str2bool, nargs='?', const=True, default=True)
    parser.add_argument('--bots', help='Lists the Bots available to play with', type=str2bool, nargs='?', const=True, default=False)

    parser.add_argument('--competition', help='Sets the competition mode where multiple bots can play against each other in a league style', type=str2bool, nargs='?', const=True, default=False)
    args = parser.parse_args()

    if args.competition:
        bot_list = list(bot_map.values())[2:]
        bot_names = list(bot_map.keys())[2:]
        scores = {name: 0 for name in bot_names}

        match_matrix = [[0 for _ in range(len(bot_list))] for _ in range(len(bot_list))]
        move_matrix = [[[] for _ in range(len(bot_list))] for _ in range(len(bot_list))]
        time_matrix = [[[] for _ in range(len(bot_list))] for _ in range(len(bot_list))]
        
        for i in range(len(bot_list)):
            for j in range(i + 1, len(bot_list)):
                bot1_class = bot_list[i]
                bot2_class = bot_list[j]
                bot1_name = bot_names[i]
                bot2_name = bot_names[j]

                print(f"\nStarting matches between {bot1_name} and {bot2_name}...\n")

                for game_num in range(TOTAL_GAMES):

                    print(f"Game {game_num + 1} of {TOTAL_GAMES}")
                    p1 = bot1_class(Board.PLAYER1_PIECE) if game_num % 2 == 0 else bot2_class(Board.PLAYER1_PIECE)
                    p2 = bot2_class(Board.PLAYER2_PIECE) if game_num % 2 == 0 else bot1_class(Board.PLAYER2_PIECE)
                    winner, stats = connect4(p1, p2, ui=False, show_board=False)

                    if winner == Board.PLAYER1_PIECE:
                        if game_num % 2 == 0:
                            scores[bot1_name] += 1
                            print(f"{bot1_name} wins this game!\n")
                            match_matrix[i][j] += 1
                            move_matrix, time_matrix = assign_stats(move_matrix, time_matrix, stats, i, j)
                        else:
                            scores[bot2_name] += 1
                            print(f"{bot2_name} wins this game!\n")
                            match_matrix[j][i] += 1
                            move_matrix, time_matrix = assign_stats(move_matrix, time_matrix, stats, j, i)
                            
                    elif winner == Board.PLAYER2_PIECE:
                        if game_num % 2 == 0:
                            scores[bot2_name] += 1
                            print(f"{bot2_name} wins this game!\n")
                            match_matrix[j][i] += 1
                            move_matrix, time_matrix = assign_stats(move_matrix, time_matrix, stats, i, j)
                        else:
                            scores[bot1_name] += 1
                            print(f"{bot1_name} wins this game!\n")
                            match_matrix[i][j] += 1
                            move_matrix, time_matrix = assign_stats(move_matrix, time_matrix, stats, j, i)
                    else:
                        scores[bot1_name] += 0.5
                        scores[bot2_name] += 0.5
                        print("This game is a draw!\n")

        print("\nFinal Scores:")
        for bot_name, score in scores.items():
            print(f"{bot_name}: {score} points")


        print_match_results(match_matrix, bot_names)
        print_move_results(move_matrix, bot_names)
        print_time_results(time_matrix, bot_names)

        return
    
    
    if args.p1 is None and args.p2 is None and args.ui and first_player is None:
        main_screen()

    print("\n")
    if args.bots:
        print('The available bots to play with are:')
        for bot in bot_map:
            if bot != 'human':
                print(f'- {name_map[bot]} ({bot})')
        print()
        print('Use the string in the brackets to pass as argument to p1 and p2')
        exit(1)

    p1 = p2 = None
    
    if first_player != None:
        args.p1 = first_player
        args.p2 = second_player

    if args.p1 is None or args.p2 is None:
        print('Set both p1 and p2 args')
        sys.exit()

    if args.p1 is None or args.p1 == "human":
        print("Player 1 is set as a Human")
        p1 = Human(Board.PLAYER1_PIECE)
    else:
        for bot in bot_map:
            if bot == args.p1:
                p1 = bot_map[args.p1](Board.PLAYER1_PIECE)
        if p1 is None:
            print("oops! you have entered a wrong bot name for p1")
            exit(1)
        print("Player 1 is set as a " + name_map[args.p1])

    if args.p2 is None or args.p2 == "human":
        print("Player 2 is set as a Human")
        p2 = Human(Board.PLAYER2_PIECE)
    else:
        for bot in bot_map:
            if bot == args.p2:
                p2 = bot_map[args.p2](Board.PLAYER2_PIECE)
        if p2 is None:
            print("oops! you have entered a wrong bot name for p2")
            exit(1)
        print("Player 2 is set as a " + name_map[args.p2])

    print("\n")

    if args.ui == False and (Human == type(p1) or Human == type(p2)):
        print("Can not play game as Human without UI!")
        exit(1)

    connect4(p1, p2, args.ui)

def print_match_results(match_matrix, bot_names):
    print("\nMatch Results Matrix:")
    print(" " * 15, end="")
    for name in bot_names:
        print(f"{name:15}", end="")
    print()
    for i in range(len(bot_names)):
        print(f"{bot_names[i]:15}", end="")
        for j in range(len(bot_names)):
            print(f"{match_matrix[i][j]:15}", end="")
        print()

def print_move_results(move_matrix, bot_names):
    print("\nAverage Moves Matrix:")
    print(" " * 15, end="")
    for name in bot_names:
        print(f"{name:15}", end="")
    print()
    for i in range(len(bot_names)):
        print(f"{bot_names[i]:15}", end="")
        for j in range(len(bot_names)):
            if move_matrix[i][j]:
                avg_moves = sum(move_matrix[i][j]) / len(move_matrix[i][j])
                print(f"{avg_moves:<15.2f}", end="")
            else:
                print(f"{0:<15}", end="")
        print()

def print_time_results(time_matrix=None, bot_names=None):   
    print("\nAverage Time Matrix:")
    print(" " * 15, end="")
    for name in bot_names:
        print(f"{name:15}", end="")
    print()
    for i in range(len(bot_names)):
        print(f"{bot_names[i]:15}", end="")
        for j in range(len(bot_names)):
            if time_matrix[i][j]:
                avg_time = sum(time_matrix[i][j]) / len(time_matrix[i][j])
                print(f"{avg_time:<15.2f}", end="")
            else:
                print(f"{0:<15}", end="")
        print()     

def assign_stats(move_matrix, time_matrix, stats, i, j):
    move_matrix[i][j].append(stats[0]["moves_count"])
    time_matrix[i][j].append(stats[0]["time"])
    move_matrix[j][i].append(stats[1]["moves_count"])
    time_matrix[j][i].append(stats[1]["time"])
    return move_matrix, time_matrix

def main_screen():
    pygame.init()
    pygame.display.set_caption("Connect Four | AI Project")
    # board = Board(1)
    graphics_board = GBoard(board)

    def human_vs_human():
        main("human", "human")

    player_vs_player_button = graphics_board.create_button(60, 220, 300, 40, '1. PLAYER VS PLAYER', human_vs_human)
    player_vs_bot_button = graphics_board.create_button(60, 280, 300, 40, '2. PLAYER VS BOT', bot_vs_human_screen)
    bot_vs_bot_button = graphics_board.create_button(60, 340, 300, 40, '3. BOT VS BOT', bot_vs_bot_screen)
    quit_button = graphics_board.create_button(60, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [player_vs_player_button, player_vs_bot_button, bot_vs_bot_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE ONE OF THE OPTIONS TO PLAY", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def bot_vs_human_screen():
    pygame.init()
    # board = Board(1)
    graphics_board = GBoard(board)

    def human_vs_minimax():
        main("human", "minimax")

    def human_vs_expectimax():
        main("human", "expectimax")
    
    def human_vs_montecarlo():
        main("human", "montecarlo")

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT', human_vs_minimax)
    expectimax_button = graphics_board.create_button(60, 280, 400, 40, '2. EXPECTIMAX BOT', human_vs_expectimax)
    montecarlo_button = graphics_board.create_button(60, 340, 400, 40, '3. MONTECARLO SEARCH BOT', human_vs_montecarlo)
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', main_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, expectimax_button, montecarlo_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE THE BOT TO PLAY AGAINST", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE

        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

def bot_vs_bot_screen():
    pygame.init()
    # board = Board(1)
    graphics_board = GBoard(board)

    first_bot = second_bot = None

    def bots_to_play_against(bot_to_play):
        nonlocal first_bot, second_bot

        if first_bot == None:
            first_bot = bot_to_play
        elif second_bot == None and first_bot != None:
            second_bot= bot_to_play

        if first_bot != None and second_bot != None:
            main(first_bot, second_bot)

    minimax_button = graphics_board.create_button(60, 220, 400, 40, '1. MINIMAX BOT',  bots_to_play_against, ("minimax"))
    expectimax_button = graphics_board.create_button(60, 280, 400, 40, '2. EXPECTIMAX BOT', bots_to_play_against, ("expectimax"))
    montecarlo_button = graphics_board.create_button(60, 340, 400, 40, '3. MONTECARLO SEARCH BOT', bots_to_play_against, ("montecarlo"))
    
    back_button = graphics_board.create_button(60, 600, 100, 40, 'BACK', main_screen)
    quit_button = graphics_board.create_button(180, 600, 100, 40, 'QUIT', sys.exit)

    button_list = [minimax_button, expectimax_button, montecarlo_button, back_button, quit_button]

    while True:
        graphics_board.write_on_board("CONNECT 4 GAME", graphics_board.RED , 350 , 100, 60, True)
        graphics_board.write_on_board("CHOOSE ANY TWO BOT(S) TO PLAY", graphics_board.YELLOW , 350 , 175, 30, True)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    for button in button_list:
                        if button['button position'].collidepoint(event.pos):
                            if(button['args'] != None):
                                button['callback'](button['args'])
                            else:
                                button['callback']()
            
            elif event.type == pygame.MOUSEMOTION:
                for button in button_list:
                    if button['button position'].collidepoint(event.pos):
                        button['color'] = graphics_board.RED
                    else:
                        button['color'] = graphics_board.WHITE                
        
        for button in button_list:
            graphics_board.draw_button(button, graphics_board.screen)

        pygame.display.update()

if __name__ == '__main__':
    main()
