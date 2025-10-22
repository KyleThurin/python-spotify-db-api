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
    username         = input("Enter a new username: ")
    password         = getpass.getpass("Enter a password: ")
    confirm_password = getpass.getpass("Confirm password: ")

    if not username:
        print("Error: Username cannot be empty.")
        return

    # If 'password' does NOT match 'confirm_password'
    if password != confirm_password:
        print("Error: Passwords do not match.")
        return

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    # If the 'username' and hashed password are inserted into the database
    if database.insert_user(username, hashed_password.decode('utf-8')):
        print(f"User '{username}' registered successfully!")
    else:
        print(f"Registration failed. Username '{username}' may already exist.")

def logged_in_menu(user_id):
    while True:
        # Displays menu text
        print("\n--- Logged In Menu ---")
        print("1. Tell me a Joke")
        print("2. List all my favorite Jokes")
        print("3. Search Spotify music by artist name")
        print("4. List all my favorite artists")
        print("5. Return to main menu")

        choice = input("Enter your choice (1 - 5): ")
        if choice == '1':
            call_dad_joke(user_id)
        elif choice == '2':
            get_all_dad_jokes(user_id)
        elif choice == '3':
            get_spotify_music (user_id)
        elif choice == '4':
            list_favorite_artists(user_id)
        elif choice == '5':
            print("Returning to main menu")
            break
        else:
            print("***Invalid Entry***")
            print("Please enter 1 - 5")

def call_dad_joke(user_id):

    print("\nLet me tell you something... 'punny'!")
    joke = dad_joke_service.getDadJoke()
    if joke:
        print(joke)
        user_input = input("Do you wish to save the joke? (y/n) ")

        # If the user input is equal to 'y'
        if user_input.startswith('y'):
            print("Saving the joke to database")
            if database.insert_joke(user_id, joke):
                print("The joke was saved successfully!")
            else:
                print("Failed to save the joke.")

def get_all_dad_jokes(user_id):
    print("\n--- Your Favorite Dad Jokes ---")
    jokes = database.get_all_dad_jokes(user_id)

    if jokes:
        # Loop through the list of jokes saved
        for idx, joke_tuple in enumerate(jokes):
            # Accessing the joke text (the first element of the tuple)
            print(f"{idx + 1}. {joke_tuple[0]}")
    else:
        print("You haven't saved any jokes yet!")

def get_spotify_music(user_id):
    print("\n--- Spotify Artist Search ---")
    token       = spotify_service.get_token()
    if not token:
        print("Could not retrieve Spotify token.")
        return
    artist_name = input('Enter the artist to search for: ')
    result      = spotify_service.search_for_artist(token, artist_name)
    # Error Handling for Artist Search (Exit the function if artist not found)
    if not result:
        print(f"No results found for '{artist_name}'.")
        print("\nExiting.")
        return
    artist_id   = result["id"]
    tracks      = spotify_service.get_songs_by_artist(token, artist_id)

    if tracks:
        print(f"\nTop Tracks for {result.get('name')}:")
        for idx, song in enumerate(tracks):
            print(f"{idx+1}. {song['name']}")
    else:
        print("\nNo tracks found for this artist.")

    user_input = input("Wish to save artist to favorites? (y/n) ")

    # If the user input is equal to 'y'
    if user_input.startswith('y'):
        print("Saving the artist to database")
        # Pass the full result dictionary to the database function
        if database.insert_artist(result, user_id):
            print("Artist saved successfully!")
        else:
            print("Failed to save artist.")

def list_favorite_artists(user_id):
    print("\n--- Your Favorite Artists ---")
    artists = database.get_favorite_artists(user_id)

    if artists:
        for idx, (name, followers) in enumerate(artists):
            followers_formatted = f"{followers:,}"
            print(f"{idx + 1}. {name} (Followers: {followers_formatted})")
    else:
        print("You haven't saved any favorite artists yet!")

def login_user():
    """
    Prompts the user for a username and password, then verifies the credentials
    against the database.
    """
    print("\n--- User Login ---")
    username = input("Enter your username: ")
    password = getpass.getpass("Enter your password: ")

    user_data = database.find_user_by_username(username)

    # If there is a user account indexed
    if user_data:
        user_id, hashed_password = user_data

        # If the user password matches the password entered by the user
        if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
            print(f"\nWelcome back, {username}! You are logged in.")
            logged_in_menu(user_id)
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
