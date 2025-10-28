import sys
import os
import time
import csv
import re
import random
import argparse
import subprocess

# ensure we run relative to repository root (file located at repo root)
ROOT = os.path.dirname(os.path.abspath(__file__))

# Path to the game script
GAME_PY = os.path.join(ROOT, 'game.py')

# Regex helpers to parse game output
RE_TIME = re.compile(r"TIME:\s*([0-9]+\.?[0-9]*)\s*seconds", re.IGNORECASE)
RE_MOVES = re.compile(r"MOVES:\s*([0-9]+)", re.IGNORECASE)
RE_WIN = re.compile(r"PLAYER\s*([12])\s*WINS!", re.IGNORECASE)
RE_TIE = re.compile(r"IT'S A TIE!", re.IGNORECASE)


def get_available_bots():
    """Import `game` to get the bot_map and return a list of bot keys excluding 'human'.
    We import lazily to avoid side-effects in the runner's top-level code.
    """
    # modify sys.path to include ROOT so imports inside game work correctly
    if ROOT not in sys.path:
        sys.path.insert(0, ROOT)

    import game
    bots = [k for k in game.bot_map.keys() if k.lower() != 'human']
    return bots


def run_match(bot1, bot2, per_match_timeout=120):
    """Runs a match by invoking `game.py --p1 bot1 --p2 bot2 --ui False`.
    Returns a dict with parsed results and raw stdout/stderr.
    """
    cmd = [sys.executable, GAME_PY, '--p1', bot1, '--p2', bot2, '--ui', 'False']
    try:
        proc = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=per_match_timeout)
    except subprocess.TimeoutExpired:
        return {
            'bot1': bot1,
            'bot2': bot2,
            'error': 'timeout',
            'stdout': '',
            'stderr': ''
        }

    out = proc.stdout or ''
    err = proc.stderr or ''

    # parse times and moves for both players
    times = RE_TIME.findall(out)
    moves = RE_MOVES.findall(out)

    time_p1 = float(times[0]) if len(times) >= 1 else None
    time_p2 = float(times[1]) if len(times) >= 2 else None
    moves_p1 = int(moves[0]) if len(moves) >= 1 else None
    moves_p2 = int(moves[1]) if len(moves) >= 2 else None

    winner = None
    if RE_TIE.search(out):
        winner = 'tie'
    else:
        w = RE_WIN.search(out)
        if w:
            winner = 'player' + w.group(1)

    return {
        'bot1': bot1,
        'bot2': bot2,
        'time_p1': time_p1,
        'time_p2': time_p2,
        'moves_p1': moves_p1,
        'moves_p2': moves_p2,
        'winner': winner,
        'stdout': out,
        'stderr': err,
        'returncode': proc.returncode
    }


def main(duration_per_game, outfile):
    bots = get_available_bots()
    if not bots:
        print('No bots found in game.bot_map (excluding human). Exiting.')
        return

    matchups = [(bots[i], bots[j]) for i in range(len(bots)) for j in range(i + 1, len(bots))]

    results = []
    match_count = 0
    
    duration_total = len(matchups) * duration_per_game
    start_time = time.time()
    end_time = start_time + duration_total

    idx = 0
    while time.time() < end_time and idx < len(matchups):
        bot1, bot2 = matchups[idx % len(matchups)]
        idx += 1
        match_count += 1
        wall_start = time.time()
        print(f'GAME #{match_count}: {bot1} vs {bot2} ...')

        res = run_match(bot1, bot2)
        wall_end = time.time()

        # attach metadata
        res['match_number'] = match_count
        res['wall_time_seconds'] = round(wall_end - wall_start, 3)
        res['timestamp'] = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(wall_end))

        results.append(res)

        if time.time() + 1.0 >= end_time:
            break

    # write CSV
    fieldnames = ['match_number', 'bot1', 'bot2', 'winner', 'time_p1', 'moves_p1', 'time_p2', 'moves_p2', 'wall_time_seconds']
    with open(outfile, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in results:
            row = {k: r.get(k) for k in fieldnames}
            writer.writerow(row)

    with open(outfile, 'r', encoding='utf-8') as f:
        print(f.read())

    print('Summary: ran %d matches in %.1f seconds' % (len(results), time.time() - start_time))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Run bot-vs-bot matches for a time budget and collect stats.')
    parser.add_argument('--duration', type=float, default=60.0, help='Total duration in seconds to run matches (default: 60)')
    parser.add_argument('--outfile', type=str, default=os.path.join(ROOT, 'results.csv'), help='CSV output file path (default: results.csv in repo root)')
    args = parser.parse_args()

    main(args.duration, args.outfile)
