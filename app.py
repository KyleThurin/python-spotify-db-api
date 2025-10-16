from services import dad_joke_service
from services import spotify_service
import database
import getpass
import bcrypt

def register_user():
    """
    Prompts the user for a username and password, hashes the password, and
    stores the new user in the database.
    """
    print("\n--- User Registration ---")
    username         = input("Enter a new username: ")      # Indexes the user input
    password         = getpass.getpass("Enter a password: ")# Indexes the password entered
    confirm_password = getpass.getpass("Confirm password: ")# Indexes the password entered

    # If 'password' does NOT match 'confirm_password'
    if password != confirm_password:
        # Displays text
        print("Error: Passwords do not match.")
        return

    # bcrypt.gensalt() generates a new salt each time.
    # The salt is automatically included in the resulting hash string,
    # which is the standard and most secure way to use bcrypt.
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # If the 'username' and hashed password are inserted into the database
    if database.insert_user(username, hashed_password.decode('utf-8')):
        # Displays "success" text
        print(f"User '{username}' registered successfully!")
    else:
        print(f"Registration failed. Username '{username}' may already exist.")

def logged_in_menu(user_id):
    while True:
        # Displays menu text
        print("--- Logged In Menu ---")
        print("1. Tell me a Joke")
        print("2. List all my favorite Jokes")
        print("3. Search Spotify music by artist name")
        print("4. Return to main menu")

        choice = input("Enter your choice (1 - 4): ") # Indexes the user input
        # If the user input equal 1
        if choice == '1':
            call_dad_joke(user_id)
        elif choice == '2':
            get_all_dad_jokes(user_id)
        elif choice == '3':
            get_spotify_music (user_id)
        elif choice == '4':
            print("Returning to main menu")
            break
        else:
            print("***Invalid Entry***")
            print("Please enter 1 - 4")

def call_dad_joke(user_id):

    print("Let me tell you something 'punny'!")
    joke = dad_joke_service.getDadJoke()# Indexes a dad joke
    print(joke)                         # Displays the joke

    user_input = input("Do you wish to save the joke? (y/n) ") # Indexes the user input
    # If the user input is equal to 'y'
    if user_input.startswith('y'):
        # Displays text
        print("Saving the joke to database")
        database.insert_joke(user_id, joke)

def get_all_dad_jokes(user_id):
    print("getting all dad jokes")
    jokes = database.get_all_dad_jokes(user_id) # Indexes the jokes saved by the current user
    # Loop through the list of jokes saved
    for joke in jokes:
        # Displays the current joke
        print(joke[0])

def get_spotify_music(user_id):
    print("Spotify music by artist: ")

    token       = spotify_service.get_token()                           # Indexes the token
    artist_name = input('Enter the artist to search for: ')             # Indexes the user input
    result      = spotify_service.search_for_artist(token, artist_name) # Searches for the artest using the user input
    artist_id   = result["id"]                                          # Indexes the 'id' of the result

    tracks      = spotify_service.get_songs_by_artist(token, artist_id) # Searches for the songs for the artest

    print("For artist: " + artist_name)

    # Loops through 'tracks'
    for idx, song in enumerate(tracks):
        # Displays the current 'song' and index value
        print(f"{idx+1}. {song['name']}")

    user_input = input("Wish to save artist to favorites? (y/n) ") # Indexes the user input
    # If the user input is equal to 'y'
    if user_input.startswith('y'):
        print("Saving the artist to database")
        database.insert_artist(result, user_id) # Adds the artist's ID to the database

def login_user():
    """
    Prompts the user for a username and password, then verifies the credentials
    against the database.
    """
    print("\n--- User Login ---")
    username = input("Enter your username: ")           # Indexes the username
    password = getpass.getpass("Enter your password: ") # Indexes the password

    user_data = database.find_user_by_username(username)# Indexes the user account

    # If there is a user account indexed
    if user_data:
        user_id, hashed_password = user_data # Indexes the 'user_id' and 'hashed_password'

        # If the user password matches the password entered by the user
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            print(f"\nWelcome back, {username}! You are logged in.")
        else:
            print("\nError: Invalid password.")
    else:
        print("\nError: User not found.")

def main():
    """
    Main function to display the menu and handle user input.
    """

    database.create_users_table() # Creates a database
    # - Ensures the database exists before running the app

    while True:
        print("\n--- Main Menu ---")
        print("1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice (1-3): ")

        if choice == '1':
            register_user()
        elif choice == '2':
            login_user()
        elif choice == '3':
            print("Exiting application. Goodbye!")
            break
        else:
            print("Invalid choice. Please enter 1, 2, or 3.")

if __name__ == "__main__":
    main()
