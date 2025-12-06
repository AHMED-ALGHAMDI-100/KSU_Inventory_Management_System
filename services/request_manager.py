import psycopg2
import datetime
from config.db_config import get_db_connection


class RequestManager:
    """
    Handles the lifecycle of Item Requests and Returns.
    """

    @staticmethod
    def create_request(college_id, item_id, quantity, purpose, request_type='Request'):
        """
        Creates a new request or return in the database.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # Status logic: New requests start as 'Pending'
            initial_status = 'Pending'

            # FIX: Used 'purpose_notes' and 'request_type' to match DB schema
            sql = """
                INSERT INTO requests (college_id, item_id, quantity, purpose_notes, status, request_type, request_date)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            # Create a timestamp
            now = datetime.datetime.now()

            cursor.execute(sql, (college_id, item_id, quantity, purpose, initial_status, request_type, now))
            conn.commit()

            # Log transaction
            RequestManager._log_transaction(college_id, "Create " + request_type, item_id, quantity)

            return True
        except psycopg2.Error as e:
            print(f"DB Error creating request: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_pending_requests():
        """
        Retrieves all pending requests for the Manager to review.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # FIX: Updated column names (request_no, purpose_notes, request_type, item_id)
            sql = """
                SELECT r.request_no, u.first_name, i.name, r.quantity, r.purpose_notes, r.request_type
                FROM requests r
                JOIN users u ON r.college_id = u.id
                JOIN items i ON r.item_id = i.item_id
                WHERE r.status = 'Pending'
            """
            cursor.execute(sql)
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"DB Error fetching pending: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def update_request_status(request_id, new_status, reason=None, manager_id=None):
        """
        Manager approves or rejects a request.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # FIX: Changed 'WHERE id =' to 'WHERE request_no ='
            sql = "UPDATE requests SET status = %s, rejection_reason = %s WHERE request_no = %s"
            cursor.execute(sql, (new_status, reason, request_id))
            conn.commit()

            # Log transaction
            if manager_id:
                RequestManager._log_transaction(manager_id, f"Set Status: {new_status}", request_id, 0)

            return True
        except psycopg2.Error as e:
            print(f"DB Error updating status: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def process_approval(request_id, new_status, manager_id):
        """
        Processes approval for requests (reserves stock) and returns.
        """
        from services.stock_manager import StockManager

        # 1. Update status
        if not RequestManager.update_request_status(request_id, new_status, manager_id=manager_id):
            return False

        # 2. Check if it's an outgoing REQUEST (requires stock adjustment)
        if 'Ready for Pickup' in new_status and 'Return' not in new_status:
            # Placeholder for stock adjustment logic
            pass

        return True

    @staticmethod
    def _log_transaction(actor_id, action, item_ref, quantity):
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Actor: {actor_id} | Action: {action} | Item/Req: {item_ref} | Qty: {quantity}\n"
            with open("transactions.log", "a") as f:
                f.write(log_entry)
        except Exception as e:
            print(f"Logging Error: {e}")