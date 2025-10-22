from dotenv import load_dotenv
import psycopg2
import os

# Load environment variables from a .env file
load_dotenv()

def get_db_connection():
    """
    Establishes and returns a connection to the PostgreSQL database.
    """
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        return conn
    except psycopg2.Error as e:
        print(f"Database connection error: {e}")
        return None

def create_users_table():
    """
    Creates the 'users' table if it doesn't already exist.
    """
    conn = get_db_connection()
    if conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(50) UNIQUE NOT NULL,
                    hashed_password VARCHAR(100) NOT NULL
                );
            """)
            conn.commit()
            print("Users table created or already exists.")
        conn.close()

def insert_user(username, hashed_password):
    """
    Inserts a new user into the 'users' table.
    Returns True on success, False on failure (e.g., username already exists).
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s)",
                    (username, hashed_password)
                )
                conn.commit()
                return True
        except psycopg2.IntegrityError:
            print(f"Error: Username '{username}' already exists.")
            conn.rollback()
            return False
        except psycopg2.Error as e:
            print(f"Failed to register user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def find_user_by_username(username):
    """
    Finds a user by their username and returns their ID and hashed password.
    Returns a tuple (user_id, hashed_password) on success, None on failure.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT id, hashed_password FROM users WHERE username = %s", (username,))
                user_data = cur.fetchone()
                return user_data
        except psycopg2.Error as e:
            print(f"Error finding user: {e}")
            return None
        finally:
            conn.close()
    return None

def get_all_dad_jokes(user_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute("SELECT joke FROM joke WHERE user_id = %s", (user_id,))
                joke_data = cur.fetchall()
                return joke_data
        except psycopg2.Error as e:
            print(f"Error finding user: {e}")
            return None
        finally:
            conn.close()
    return None

def insert_joke(user_id, joke):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO joke (user_id, joke) VALUES (%s, %s)",
                    (user_id, joke)
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Failed to register user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False

def get_artist_by_spotify_id(artist_spotify_id):
    """
    Retrieves an artist's internal ID if they exist in the database.
    """
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT artist_id FROM artist WHERE artist_spotify_id = %s",
                    (artist_spotify_id,)
                )
                result = cur.fetchone()
                return result[0] if result else None
        except psycopg2.Error as e:
            print(f"Error fetching artist by Spotify ID: {e}")
            return None
        finally:
            conn.close()
    return None


def link_artist_to_user(artist_id, user_id, cur):
    """
    Links an existing artist to a user in the artist_users table.
    """
    try:
        cur.execute(
            "INSERT INTO artist_users (artist_id, user_id) VALUES (%s, %s)",
            (artist_id, user_id)
        )
        return True
    except psycopg2.IntegrityError:
        # This means the user already has this artist as a favorite, which is fine.
        print("Artist is already a favorite for this user.")
        return True
    except psycopg2.Error as e:
        print(f"Failed to link artist to user: {e}")
        return False

"""
def insert_artist(result, user_id):

    artist_name         = result['name']
    followers           = result['followers']['total']
    artist_spotify_id   = result['id']
    conn                = get_db_connection()

    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO artist (artist_name, followers, artist_spotify_id) VALUES (%s, %s, %s)",
                    (artist_name, followers, artist_spotify_id)
                )
                conn.commit()
                cur.execute(
                    "SELECT artist_id FROM artist WHERE artist_spotify_id = %s",
                    (artist_spotify_id, )
                )
                conn.commit()
                artist_id = cur.fetchone()

                cur.execute(
                    "INSERT INTO artist_users (artist_id, user_id) VALUES (%s, %s)",
                    (artist_id, user_id)
                )
                conn.commit()
                return True
        except psycopg2.Error as e:
            print(f"Failed to register user: {e}")
            conn.rollback()
            return False
        finally:
            conn.close()
    return False
"""

def insert_artist(result, user_id):
    artist_name         = result['name']
    followers           = result['followers']['total']
    artist_spotify_id   = result['id']

    # Checks if the artist already exists in the 'artist' table
    existing_artist_id = get_artist_by_spotify_id(artist_spotify_id)
    # If the artist already exists
    if existing_artist_id:
        print(f"Artist '{artist_name}' already exists in the database. Linking to user.")
        # Link them to the user.
        artist_id = existing_artist_id

        conn = get_db_connection()
        if not conn:
            return False

        try:
            with conn.cursor() as cur:
                if link_artist_to_user(artist_id, user_id, conn, cur):
                    conn.commit()
                    return True
                else:
                    conn.rollback()
                    return False
        finally:
            conn.close()

    # If the artist does not exist, insert them and link to user in one transaction
    conn = get_db_connection()
    if not conn:
        return False

    try:
        with conn.cursor() as cur:
            # Insert into 'artist' and retrieve the 'artist_id'
            cur.execute(
                "INSERT INTO artist (artist_name, followers, artist_spotify_id) VALUES (%s, %s, %s) RETURNING artist_id",
                (artist_name, followers, artist_spotify_id)
            )
            artist_id = cur.fetchone()[0] # Only necessary if the 'insert' was successful

            # Link the new artist to the user
            if link_artist_to_user(artist_id, user_id, conn, cur):
                conn.commit()  # Commit both the artist insert and the linking
                return True
            else:
                conn.rollback()
                return False

    except psycopg2.IntegrityError:
        # Catching this is a fallback in case of a race condition, though the check above should prevent it
        print(f"Error: Artist with Spotify ID {artist_spotify_id} was inserted just now by another process.")
        conn.rollback()
        return False
    except psycopg2.Error as e:
        print(f"Failed to insert new artist and link to user: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()
    return False

def get_favorite_artists(user_id):
    conn = get_db_connection()
    if conn:
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    SELECT a.artist_name, a.followers
                    FROM artist a
                    JOIN artist_users au ON a.artist_id = au.artist_id
                    WHERE au.user_id = %s
                    ORDER BY a.artist_name
                    """,
                    (user_id,)
                )
                return cur.fetchall()
        except psycopg2.Error as e:
            print(f"Error retrieving favorite artists: {e}")
            return []
        finally:
            conn.close()
    return []