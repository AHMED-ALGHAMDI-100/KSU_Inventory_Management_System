import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()  # here we load the DB URL variable

DATABASE_URL = os.getenv("DATABASE_URL")


def get_db_connection():
    if not DATABASE_URL:
        # This will happen if the .env file is missing or doesn't have the variable
        raise EnvironmentError("DATABASE_URL not found. Please check your local .env ")

    conn = None
    try:
        # Connect using the DATABASE_URL string
        conn = psycopg2.connect(DATABASE_URL)
        return conn
    except psycopg2.Error as e:
        print(f"ERROR: Could not connect to the database, Details: {e}")
        return None


#  test function
if __name__ == '__main__':
    conn = get_db_connection()
    if conn:
        print(" Database connection successful!")
        conn.close()
    else:
        print(" Database connection failed!")