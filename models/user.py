import psycopg2
import bcrypt  # For secure password hashing
from config.db_config import get_db_connection


class User:
    """
    Handles all interactions with the 'users' table in the Central DB (Railway).
    Implements security and authentication logic.
    """

    @staticmethod
    def check_if_registered(user_id):
        """
        Checks the Railway database to see if a user ID is already in use.
        (Requirement: Display error if user is already registered)
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None:
                return True  # Treat connection failure as "registered" to block sign-up

            cursor = conn.cursor()

            # Execute SQL query to check for the ID
            cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))

            # Check if a row was found
            if cursor.fetchone():
                return True  # User ID found

            return False  # User ID not found

        except psycopg2.Error as e:
            print(f"Database error during registration check: {e}")
            return True  # Fail safe: assume registered on error

        finally:
            if conn:
                conn.close()

    @staticmethod
    def create_user(data):
        """
        Hashes the password and inserts a new user record into the database.
        (Requirement: System sends user info to central DB; only hash is stored)
        """
        conn = None

        # 1. Generate Password Hash
        plain_password = data['password']
        hashed_password = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

        try:
            conn = get_db_connection()
            if conn is None:
                return False

            cursor = conn.cursor()

            # 2. SQL to insert user data and the HASH
            sql = """
                  INSERT INTO users (id, first_name, last_name, user_class, password_hash, email, phone_number)
                  VALUES (%s, %s, %s, %s, %s, %s, %s) \
                  """

            values = (
                data['id'], data['first_name'], data['last_name'],
                data['user_class'], hashed_password,
                data['email'], data['phone_number']
            )

            cursor.execute(sql, values)
            conn.commit()
            return True

        except psycopg2.IntegrityError as e:
            print(f"Error: Integrity constraint violation (Duplicate data): {e}")
            return False
        except psycopg2.Error as e:
            print(f"Database error during user creation: {e}")
            return False
        finally:
            if conn:
                conn.close()

    @staticmethod
    def authenticate_user(user_id, entered_password):
        """
        Checks the entered password against the stored hash in the database.
        (Requirement: Check hash against stored hash, and forward based on user class)
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None:
                return None

            cursor = conn.cursor()

            # 1. Retrieve the stored hash and user class
            sql = "SELECT password_hash, user_class FROM users WHERE id = %s"
            cursor.execute(sql, (user_id,))

            result = cursor.fetchone()

            if result:
                stored_hash = result[0].encode('utf-8')
                user_class = result[1]

                # 2. Verify Hash
                # bcrypt.checkpw automatically handles salt extraction and hashing for comparison.
                if bcrypt.checkpw(entered_password.encode('utf-8'), stored_hash):
                    return user_class  # Success: return the class for forwarding

            # Failure
            return None

        except psycopg2.Error as e:
            print(f"Database error during authentication: {e}")
            return None

        finally:
            if conn:
                conn.close()