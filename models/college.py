import psycopg2
from config.db_config import get_db_connection

class College:
    """
    Represents a College entity.
    Handles:
    1. Registry Management (for Inventory Manager)
    2. User Data Retrieval (for College User)
    """
    def __init__(self, user_id=None):
        self.college_id = user_id

    # ---------------------------------------------------------
    # PART 1: REGISTRY MANAGEMENT (For Manager Window)
    # ---------------------------------------------------------
    @staticmethod
    def add_college(name):
        """Adds a new college to the registry."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO colleges (college_name) VALUES (%s)", (name,))
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"Error adding college: {e}")
            return False
        finally:
            conn.close()

    @staticmethod
    def get_all_colleges():
        """Retrieves all colleges for the Manager's list."""
        conn = get_db_connection()
        if not conn: return []
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT college_id, college_name FROM colleges ORDER BY college_id")
            return cursor.fetchall()
        finally:
            conn.close()

    @staticmethod
    def delete_college(college_id):
        """Deletes a college from the registry."""
        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM colleges WHERE college_id = %s", (college_id,))
            conn.commit()
            return True
        except psycopg2.Error:
            return False
        finally:
            conn.close()

    # ---------------------------------------------------------
    # PART 2: COLLEGE USER FUNCTIONS (For College Window)
    # ---------------------------------------------------------
    def get_my_requests(self):
        return self._get_transactions_by_type('Request')

    def get_my_returns(self):
        return self._get_transactions_by_type('Return')

    def get_current_custody(self):
        """
        Fetches items currently held by this college from inventory_stock.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # Joined with inventory_stock and used correct item_id
            sql = """
                SELECT i.item_id, i.name, s.quantity, i.unit
                FROM inventory_stock s
                JOIN items i ON s.item_id = i.item_id
                WHERE s.college_id = %s AND s.quantity > 0
            """
            cursor.execute(sql, (self.college_id,))
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching custody: {e}")
            return []
        finally:
            if conn: conn.close()

    def _get_transactions_by_type(self, trans_type):
        """Helper to fetch requests/returns with correct schema."""
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # Using correct columns: request_no, request_type, item_id
            sql = """
                SELECT r.request_no, i.name, r.quantity, r.status, r.request_date, r.rejection_reason
                FROM requests r
                JOIN items i ON r.item_id = i.item_id
                WHERE r.college_id = %s AND r.request_type = %s
                ORDER BY r.request_date DESC
            """
            cursor.execute(sql, (self.college_id, trans_type))
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"Error fetching {trans_type}s: {e}")
            return []
        finally:
            if conn: conn.close()