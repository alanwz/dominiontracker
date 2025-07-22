import sqlite3
from collections import defaultdict
from datetime import datetime

# --- Configuration ---
DB_FILE = 'dominion_stats.db'

# --- Database Functions ---

def connect_db():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def create_table():
    """Creates the games table if it doesn't already exist."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            game_date TEXT NOT NULL,
            players TEXT NOT NULL,
            winners TEXT NOT NULL,
            scores TEXT NOT NULL,
            kingdom_cards TEXT NOT NULL,
            expansions_used TEXT NOT NULL,
            notes TEXT
        )
    ''')
    conn.commit()
    conn.close()

# --- Helper Functions ---

def record_game():
    """Prompts the user for game details and records them in the database."""
    print("\n--- Record New Dominion Game ---")
    
    # Auto-generate date
    game_date = datetime.now().strftime("%Y-%m-%d")
    print(f"Date: {game_date}")
    
    players_input = input("Enter player names (comma-separated): ")
    players = [p.strip() for p in players_input.split(',') if p.strip()]
    if not players:
        print("Error: At least one player name is required.")
        return
    
    winner_input = input("Enter the winner(s) name(s) (comma-separated if tied): ")
    winners = [w.strip() for w in winner_input.split(',') if w.strip()]
    if not winners:
        print("Error: At least one winner name is required.")
        return
    
    scores_input = input("Enter scores for each player (e.g., 'Player1:30,Player2:25'): ")
    scores_dict = {}
    try:
        score_pairs = [s.strip() for s in scores_input.split(',') if s.strip()]
        for sp in score_pairs:
            parts = sp.split(':')
            if len(parts) == 2:
                player_name = parts[0].strip()
                score_val = int(parts[1].strip())
                scores_dict[player_name] = score_val
            else:
                print(f"Warning: Skipping malformed score entry '{sp}'. Please use 'Player:Score' format.")
        if not scores_dict:
            print("Error: No valid scores entered.")
            return
    except ValueError:
        print("Error: Invalid score format. Please ensure scores are integers.")
        return
    
    kingdom_cards_input = input("Enter Kingdom Cards used (comma-separated): ")
    kingdom_cards = [c.strip() for c in kingdom_cards_input.split(',') if c.strip()]
    if not kingdom_cards:
        print("Error: At least one Kingdom Card is required.")
        return
    
    expansions_input = input("Enter Expansions used (comma-separated, leave blank if none): ")
    expansions = [e.strip() for e in expansions_input.split(',') if e.strip()] if expansions_input else []
    
    notes = input("Any additional notes? ")

    conn = connect_db()
    cursor = conn.cursor()
    
    try:
        cursor.execute('''
            INSERT INTO games (game_date, players, winners, scores, kingdom_cards, expansions_used, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            game_date,
            ';'.join(players),
            ';'.join(winners),
            ';'.join([f"{k}:{v}" for k, v in scores_dict.items()]),
            ';'.join(kingdom_cards),
            ';'.join(expansions),
            notes
        ))
        conn.commit()
        print("Game recorded successfully! ✅")
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()

def load_game_data():
    """Loads all game data from the database."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, game_date, players, winners, scores, kingdom_cards, expansions_used, notes FROM games")
    rows = cursor.fetchall()
    conn.close()

    games = []
    for row in rows:
        game_id, game_date, players_str, winners_str, scores_str, kingdom_cards_str, expansions_str, notes = row
        
        # Convert string representations back to lists/dicts
        players = players_str.split(';') if players_str else []
        winners = winners_str.split(';') if winners_str else []
        
        scores_dict = {}
        if scores_str:
            for s in scores_str.split(';'):
                parts = s.split(':')
                if len(parts) == 2:
                    try:
                        scores_dict[parts[0].strip()] = int(parts[1].strip())
                    except ValueError:
                        print(f"Warning: Could not parse score '{s}' for Game ID {game_id}. Skipping.")
        
        kingdom_cards = kingdom_cards_str.split(';') if kingdom_cards_str else []
        expansions_used = expansions_str.split(';') if expansions_str else []

        games.append({
            'Game ID': game_id,
            'Date': game_date,
            'Players': players,
            'Winner(s)': winners,
            'Scores': scores_dict,
            'Kingdom Cards': kingdom_cards,
            'Expansions Used': expansions_used,
            'Notes': notes
        })
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
        print(f"  Winner(s): {', '.join(game['Winner(s)'])}")
        print("  Scores:")
        for player, score in game['Scores'].items():
            print(f"    - {player}: {score}")
        print(f"  Kingdom Cards: {', '.join(game['Kingdom Cards'])}")
        print(f"  Expansions: {', '.join(game['Expansions Used']) if game['Expansions Used'] else 'None'}")
        print(f"  Notes: {game['Notes'] if game['Notes'] else 'None'}")
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
        winners = game['Winner(s)']
        scores = game['Scores']
        
        for player, score in scores.items():
            player_games[player] += 1
            player_total_score[player] += score
            if score > player_max_score[player]:
                player_max_score[player] = score
        
        for winner in winners:
            if winner in player_games:
                player_wins[winner] += 1
            else:
                print(f"Warning: Winner '{winner}' for Game ID {game['Game ID']} not found in players list for that game.")
            
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
    create_table() # Ensure the database table exists when the script starts
    
    while True:
        print("\n=== Dominion Stats Tracker (SQLite) ===")
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
