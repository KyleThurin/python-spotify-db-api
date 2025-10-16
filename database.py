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