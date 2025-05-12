import subprocess
import csv
import re
from datetime import datetime

# === CONFIGURATION ===
AGENT1 = "mcts"  # Your MCTS agent
AGENT2 = "randomAgent"  # Opponent agent
NUM_GAMES = 10
CSV_FILENAME = "mctsVSrandomAgent.csv"

# === INITIALIZE CSV ===
with open(CSV_FILENAME, mode="w", newline="") as file:
    writer = csv.writer(file)
    writer.writerow(
        ["Game", "Winner", "Agent1_Color", "Agent2_Color", "Final_Turn", "Timestamp"]
    )

results = {"Agent1": 0, "Agent2": 0, "Draws": 0}

# === GAME LOOP ===
for i in range(NUM_GAMES):
    game_num = i + 1
    timestamp = datetime.now().isoformat()

    # Alternate color assignments
    if i % 2 == 0:
        cmd = ["python", "-m", "referee", AGENT1, AGENT2]
        agent1_color, agent2_color = "RED", "BLUE"
        player1_name, player2_name = "Agent1", "Agent2"
    else:
        cmd = ["python", "-m", "referee", AGENT2, AGENT1]
        agent1_color, agent2_color = "BLUE", "RED"
        player1_name, player2_name = "Agent2", "Agent1"

    print(f"Running game {game_num}/{NUM_GAMES} ({agent1_color} vs {agent2_color})...")

    result = subprocess.run(cmd, capture_output=True, text=True)
    output = result.stdout

    # Determine winner from referee output
    if "referee @ result: player 1" in output:
        winner = player1_name
        results[player1_name] += 1
    elif "referee @ result: player 2" in output:
        winner = player2_name
        results[player2_name] += 1
    else:
        winner = "Draw"
        results["Draws"] += 1
        print("⚠️ Could not determine winner.")

    # Extract final turn number using pattern: (turn N)
    turn_matches = re.findall(r"\\(turn (\\d+)\\)", output)
    final_turn = int(turn_matches[-1]) if turn_matches else "N/A"

    # Log result to CSV
    with open(CSV_FILENAME, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [game_num, winner, agent1_color, agent2_color, final_turn, timestamp]
        )

# === SUMMARY ===
print("=== Final Results ===")
print(f"{AGENT1} total wins: {results['Agent1']}")
print(f"{AGENT2} total wins: {results['Agent2']}")
print("Draws/unresolved: {results['Draws']}")
print(f"Win rate for {AGENT1}: {(results['Agent1'] / NUM_GAMES) * 100:.2f}%")
print(f"CSV log saved to: {CSV_FILENAME}")
