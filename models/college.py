import psycopg2
from config.db_config import get_db_connection

class College:
    """
    Represents a College User entity.
    Handles data retrieval for the College Window tabs:
    - My Requests
    - My Returns
    - Current Custody (Stock held by the college)
    """

    def __init__(self, user_id):
        self.college_id = user_id

    def get_my_requests(self):
        """
        Fetches history of requests (Type='Request').
        (Requirement: My Requests: list all requests with Status)
        """
        return self._get_transactions_by_type('Request')

    def get_my_returns(self):
        """
        Fetches history of returns (Type='Return').
        (Requirement: My Returns: list return requests with Status)
        """
        return self._get_transactions_by_type('Return')

    def get_current_custody(self):
        """
        Fetches items currently held by this college.
        Crucial for the 'Return Item' tab validation.
        (Requirement: Initiate Return for items currently in the college's custody)
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # Join college_stock with items to get the Item Name
            sql = """
                SELECT i.id, i.name, cs.quantity, i.unit
                FROM college_stock cs
                JOIN items i ON cs.item_id = i.item_id
                WHERE cs.college_id = %s AND cs.quantity > 0
            """
            cursor.execute(sql, (self.college_id,))
            return cursor.fetchall() # Returns list of tuples: (item_id, name, quantity, unit)

        except psycopg2.Error as e:
            print(f"Error fetching custody: {e}")
            return []
        finally:
            if conn: conn.close()

    def _get_transactions_by_type(self, trans_type):
        """
        Helper method to avoid code repetition for Requests and Returns logic.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # FIX:
            # 1. Changed 'r.id' to 'r.request_no'
            # 2. Changed 'r.type' to 'r.request_type'
            # 3. Changed 'i.id' to 'i.item_id' (just in case)
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