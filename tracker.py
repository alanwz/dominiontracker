import csv
from collections import defaultdict

# --- Configuration ---
DATA_FILE = 'dominion_stats.csv'
HEADERS = [
    'Game ID', 'Date', 'Players', 'Winner', 'Scores', 'Kingdom Cards', 'Expansions Used', 'Notes'
]

# --- Helper Functions ---

def ensure_data_file_exists():
    """Checks if the CSV file exists and creates it with headers if not."""
    try:
        with open(DATA_FILE, 'x', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(HEADERS)
    except FileExistsError:
        pass # File already exists

def get_next_game_id():
    """Generates the next sequential Game ID."""
    ensure_data_file_exists()
    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.reader(f)
        header = next(reader) # Skip header
        game_ids = [int(row[0]) for row in reader if row] # Get existing game IDs
        return max(game_ids) + 1 if game_ids else 1

def record_game():
    """Prompts the user for game details and records them."""
    ensure_data_file_exists()
    game_id = get_next_game_id()
    
    print("\n--- Record New Dominion Game ---")
    print(f"Game ID: {game_id}")
    
    date = input("Date (YYYY-MM-DD): ")
    
    players_input = input("Enter player names (comma-separated): ")
    players = [p.strip() for p in players_input.split(',')]
    
    winner = input("Enter the winner's name: ")
    
    scores_input = input("Enter scores for each player (e.g., 'Player1:30,Player2:25'): ")
    scores = {s.split(':')[0].strip(): int(s.split(':')[1].strip()) for s in scores_input.split(',')}
    
    kingdom_cards_input = input("Enter Kingdom Cards used (comma-separated): ")
    kingdom_cards = [c.strip() for c in kingdom_cards_input.split(',')]
    
    expansions_input = input("Enter Expansions used (comma-separated, leave blank if none): ")
    expansions = [e.strip() for e in expansions_input.split(',')] if expansions_input else []
    
    notes = input("Any additional notes? ")

    new_game = {
        'Game ID': game_id,
        'Date': date,
        'Players': ';'.join(players), # Store as semi-colon separated string
        'Winner': winner,
        'Scores': ';'.join([f"{k}:{v}" for k, v in scores.items()]), # Store as key:value;key:value string
        'Kingdom Cards': ';'.join(kingdom_cards),
        'Expansions Used': ';'.join(expansions),
        'Notes': notes
    }

    with open(DATA_FILE, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS)
        writer.writerow(new_game)
    print("Game recorded successfully! ✅")

def load_game_data():
    """Loads all game data from the CSV file."""
    ensure_data_file_exists()
    games = []
    with open(DATA_FILE, 'r', newline='') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert string representations back to lists/dicts
            row['Players'] = row['Players'].split(';')
            row['Scores'] = {s.split(':')[0].strip(): int(s.split(':')[1].strip()) for s in row['Scores'].split(';')}
            row['Kingdom Cards'] = row['Kingdom Cards'].split(';')
            row['Expansions Used'] = row['Expansions Used'].split(';') if row['Expansions Used'] else []
            games.append(row)
    return games

def view_all_games():
    """Displays all recorded games."""
    games = load_game_data()
    if not games:
        print("No games recorded yet. Start by recording a new game! 🎲")
        return
    
    print("\n--- All Recorded Dominion Games ---")
    for game in games:
        print(f"Game ID: {game['Game ID']}")
        print(f"  Date: {game['Date']}")
        print(f"  Players: {', '.join(game['Players'])}")
        print(f"  Winner: {game['Winner']}")
        print("  Scores:")
        for player, score in game['Scores'].items():
            print(f"    - {player}: {score}")
        print(f"  Kingdom Cards: {', '.join(game['Kingdom Cards'])}")
        print(f"  Expansions: {', '.join(game['Expansions Used']) if game['Expansions Used'] else 'None'}")
        print(f"  Notes: {game['Notes']}")
        print("-" * 30)

def view_player_stats():
    """Calculates and displays statistics for each player."""
    games = load_game_data()
    if not games:
        print("No games recorded yet. Start by recording a new game! 🎲")
        return

    player_wins = defaultdict(int)
    player_games = defaultdict(int)
    player_total_score = defaultdict(int)
    player_max_score = defaultdict(int)
    
    for game in games:
        winner = game['Winner']
        scores = game['Scores']
        
        for player, score in scores.items():
            player_games[player] += 1
            player_total_score[player] += score
            if score > player_max_score[player]:
                player_max_score[player] = score
        
        player_wins[winner] += 1
            
    print("\n--- Player Statistics ---")
    if not player_games:
        print("No player data found.")
        return

    for player in sorted(player_games.keys()):
        total_games = player_games[player]
        wins = player_wins[player]
        win_percentage = (wins / total_games) * 100 if total_games > 0 else 0
        avg_score = player_total_score[player] / total_games if total_games > 0 else 0
        
        print(f"Player: {player}")
        print(f"  Games Played: {total_games}")
        print(f"  Wins: {wins}")
        print(f"  Win Rate: {win_percentage:.2f}%")
        print(f"  Average Score: {avg_score:.2f}")
        print(f"  Highest Score: {player_max_score[player]}")
        print("-" * 30)

# --- Main Program Loop ---

def main():
    """Main function to run the Dominion stats tracker."""
    while True:
        print("\n=== Dominion Stats Tracker ===")
        print("1. Record New Game ✍️")
        print("2. View All Games 📖")
        print("3. View Player Statistics 🏆")
        print("4. Exit 🚪")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            record_game()
        elif choice == '2':
            view_all_games()
        elif choice == '3':
            view_player_stats()
        elif choice == '4':
            print("Exiting Dominion Stats Tracker. Happy gaming! 👋")
            break
        else:
            print("Invalid choice. Please try again. 🤔")

if __name__ == "__main__":
    main()
