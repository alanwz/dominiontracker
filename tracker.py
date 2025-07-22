import sqlite3
from collections import defaultdict
from datetime import datetime

# --- Configuration ---
DB_FILE = 'dominion_stats.db'

# --- Database Functions ---

def connect_db():
    """Establishes a connection to the SQLite database."""
    return sqlite3.connect(DB_FILE)

def create_tables():
    """Creates the games and kingdom_cards tables if they don't already exist."""
    conn = connect_db()
    cursor = conn.cursor()

    # Table for game records
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

    # Table for all known Kingdom Cards
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS all_kingdom_cards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            card_name TEXT UNIQUE NOT NULL
            -- You could add more fields here like:
            -- cost INTEGER,
            -- card_type TEXT,
            -- expansion TEXT
        )
    ''')
    conn.commit()
    conn.close()

def seed_kingdom_cards():
    """Populates the all_kingdom_cards table with initial card names if it's empty."""
    # This is a sample list. YOU SHOULD EXPAND THIS with all cards you own!
    initial_cards = [
        "Cellar", "Chapel", "Moat", "Chancellor", "Village", "Woodcutter",
        "Workshop", "Bureaucrat", "Feast", "Garden", "Militia", "Moneylender",
        "Remodel", "Smithy", "Spy", "Thief", "Throne Room", "Council Room",
        "Festival", "Laboratory", "Library", "Market", "Mine", "Witch",
        "Venture", "Curse", "Estate", "Duchy", "Province", "Copper", "Silver",
        "Gold", "Platinum", "Colony", # Base set + Prosperity for example
        "Artisan", "Bandit", "Harbinger", "Merchant", "Sentry", "Vassal", # 2nd Edition Base
        "Poacher", "Guide", "Warlord", # New cards from various editions/expansions
        "Duke", "Great Hall", "Nobles", "Baron", "Harem", "King's Court", # Intrigue
        "Gardens", # Base 1st ed, same as Garden in 2nd ed, for robustness
        # Add many more cards here from your expansions!
        "Native Village", "Pearl Diver", "Fishing Village", "Lighthouse", # Seaside
        "Tactician", "Warehouse", "Embassy", "Smugglers", "Salvager", # Seaside
        "Goons", "Bank", "Loan", "Mint", "Mountebank", "Quarry", "Rabble", # Prosperity
        "Grand Market", "Count", "Dame Anna", "Sir Martin" # More diverse
    ]

    conn = connect_db()
    cursor = conn.cursor()

    # Check if the table is empty
    cursor.execute("SELECT COUNT(*) FROM all_kingdom_cards")
    if cursor.fetchone()[0] == 0:
        print("Seeding initial Kingdom Cards...")
        for card_name in sorted(initial_cards): # Sort for consistent insertion order
            try:
                cursor.execute("INSERT INTO all_kingdom_cards (card_name) VALUES (?)", (card_name,))
            except sqlite3.IntegrityError:
                # This handles cases where a card might be duplicated in initial_cards list
                pass
        conn.commit()
        print(f"Seeded {len(initial_cards)} cards.")
    else:
        print("Kingdom Cards table already populated.")
    conn.close()

def add_kingdom_card(card_name):
    """Adds a single kingdom card to the all_kingdom_cards table."""
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO all_kingdom_cards (card_name) VALUES (?)", (card_name,))
        conn.commit()
        print(f"'{card_name}' added to known Kingdom Cards. ✅")
        return True
    except sqlite3.IntegrityError:
        print(f"'{card_name}' already exists in known Kingdom Cards. ℹ️")
        return False
    except sqlite3.Error as e:
        print(f"Error adding card: {e}")
        return False
    finally:
        conn.close()

def get_all_known_kingdom_cards():
    """Retrieves all card names from the all_kingdom_cards table."""
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT card_name FROM all_kingdom_cards ORDER BY card_name")
    cards = [row[0] for row in cursor.fetchall()]
    conn.close()
    return cards

# --- Helper Functions ---

def record_game():
    """Prompts the user for game details and records them in the database."""
    print("\n--- Record New Dominion Game ---")
    
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
    
    # --- Kingdom Card Validation ---
    known_cards = get_all_known_kingdom_cards()
    print("\nAvailable Kingdom Cards:")
    print(", ".join(known_cards) if known_cards else "No cards in database. Add them using option 5.")

    kingdom_cards_input = input("Enter Kingdom Cards used (comma-separated): ")
    entered_kingdom_cards = [c.strip() for c in kingdom_cards_input.split(',') if c.strip()]
    
    validated_kingdom_cards = []
    for card in entered_kingdom_cards:
        if card in known_cards:
            validated_kingdom_cards.append(card)
        else:
            print(f"Warning: '{card}' is not a recognized Kingdom Card. Please ensure correct spelling or add it to the database via option 5.")
    
    if not validated_kingdom_cards:
        print("Error: No valid Kingdom Cards entered. Game not recorded.")
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
            ';'.join(validated_kingdom_cards), # Use validated cards
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

def manage_kingdom_cards():
    """Menu for managing known Kingdom Cards."""
    while True:
        print("\n--- Manage Kingdom Cards ---")
        print("1. View All Known Cards 📄")
        print("2. Add New Card 💪")
        print("3. Back to Main Menu 🔙")

        choice = input("Enter your choice: ")
        if choice == '1':
            cards = get_all_known_kingdom_cards()
            if cards:
                print("\n--- Known Kingdom Cards ---")
                for card in cards:
                    print(f"- {card}")
            else:
                print("No Kingdom Cards found. Add some!")
        elif choice == '2':
            new_card = input("Enter the name of the new Kingdom Card to add: ").strip()
            if new_card:
                add_kingdom_card(new_card)
            else:
                print("Card name cannot be empty.")
        elif choice == '3':
            break
        else:
            print("Invalid choice. Please try again.")

# --- Main Program Loop ---

def main():
    """Main function to run the Dominion stats tracker."""
    create_tables() # Ensure both database tables exist
    seed_kingdom_cards() # Populate initial cards if table is empty
    
    while True:
        print("\n=== Dominion Stats Tracker (SQLite) ===")
        print("1. Record New Game ✍️")
        print("2. View All Games 📖")
        print("3. View Player Statistics 🏆")
        print("4. Manage Kingdom Cards 🃏") # New menu option
        print("5. Exit 🚪")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            record_game()
        elif choice == '2':
            view_all_games()
        elif choice == '3':
            view_player_stats()
        elif choice == '4':
            manage_kingdom_cards() # Call the new management function
        elif choice == '5':
            print("Exiting Dominion Stats Tracker. Happy gaming! 👋")
            break
        else:
            print("Invalid choice. Please try again. 🤔")

if __name__ == "__main__":
    main()
