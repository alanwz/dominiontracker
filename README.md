This Python script provides a command-line interface for tracking Dominion board game statistics, using an SQLite database for data storage. It allows users to record game details, view comprehensive game logs, calculate player statistics (including win rates), and manage a standardized list of Kingdom Cards.

Core Components and Functionality 🎮
The script is structured around several key functions and a persistent SQLite database (dominion_stats.db) to store information across sessions:

Database Management (connect_db, create_tables, seed_kingdom_cards):

connect_db() establishes a connection to the SQLite database file.

create_tables() sets up two tables:

games: Stores individual game records, including date, players, winners (handling ties), scores, kingdom cards used, expansions, and notes. Each game gets an auto-incrementing id.

all_kingdom_cards: A supplementary table that stores a unique list of all known Dominion Kingdom Card names. This standardizes card names and prevents typos.

seed_kingdom_cards() populates the all_kingdom_cards table with an initial list of card names the first time the script is run or if the table is empty.

Game Recording (record_game):

Prompts the user for all relevant game details, such as players, winners (comma-separated for ties), individual scores, and expansions.

Automates the game date to the current date.

Validates Kingdom Cards: When the user enters Kingdom Cards, the script checks them against the all_kingdom_cards table. Only recognized cards are saved, and a warning is issued for unrecognized ones, enforcing data consistency.

Stores the game data as a new row in the games table, converting lists (like players or winners) and dictionaries (scores) into semi-colon-separated strings for storage within SQLite's text fields.

Data Retrieval (load_game_data):

Connects to the database and fetches all game records from the games table.

Converts the semi-colon-separated strings back into Python lists and dictionaries, making the data easily usable for display and analysis within the script.

Data Display and Analysis (view_all_games, view_player_stats):

view_all_games() fetches all game data and presents it in a human-readable format, detailing each game's specifics.

view_player_stats() processes all loaded game data to calculate and display:

Games Played: Total number of games a player participated in.

Wins: Total wins for each player (correctly accounting for tied winners).

Win Rate: The percentage of games won by each player.

Average Score: A player's average score across all their games.

Highest Score: A player's personal best score.

Kingdom Card Management (manage_kingdom_cards, add_kingdom_card, get_all_known_kingdom_cards):

manage_kingdom_cards() provides a sub-menu to interact with the all_kingdom_cards table.

Users can view all known cards to see the standardized list.

They can add new cards to expand the master list of available Kingdom Cards, with checks to prevent adding duplicate entries.

Main Application Loop (main):

The main function serves as the central control for the application.

It ensures the database tables are created and initially seeded when the script starts.

It presents a menu-driven interface, allowing users to choose between recording games, viewing stats, managing cards, or exiting.
