import psycopg2
import pytest
from os import environ

def test_database_connection():
    try:
        conn = psycopg2.connect(
            dbname="test_db",
            user="test_user",
            password="test_password",
            host="localhost",
            port="5432"
        )
        assert conn is not None

        cur = conn.cursor()

        # Vérifier l'existence des tables
        cur.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
        """)
        tables = [table[0] for table in cur.fetchall()]
        assert 'movies' in tables
        assert 'ratings' in tables
        assert 'links' in tables
        assert 'users' in tables

        conn.close()

    except Exception as e:
        pytest.fail(f"Test failed: {str(e)}")

if __name__ == "__main__":
    test_database_connection()