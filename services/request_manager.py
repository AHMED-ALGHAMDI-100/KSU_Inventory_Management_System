import psycopg2
import datetime
from config.db_config import get_db_connection


class RequestManager:
    @staticmethod
    def create_request(college_id, item_id, quantity, purpose, request_type='Request'):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            initial_status = 'Pending'
            sql = """
                  INSERT INTO requests (college_id, item_id, quantity, purpose_notes, status, request_type, \
                                        request_date)
                  VALUES (%s, %s, %s, %s, %s, %s, %s) \
                  """
            now = datetime.datetime.now()
            cursor.execute(sql, (college_id, item_id, quantity, purpose, initial_status, request_type, now))
            conn.commit()
            RequestManager._log_transaction(college_id, "Create " + request_type, item_id, quantity)
            return True
        except psycopg2.Error as e:
            print(f"DB Error creating request: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_pending_requests():
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()
            sql = """
                  SELECT r.request_no, u.first_name, i.name, r.quantity, r.purpose_notes, r.request_type
                  FROM requests r
                           JOIN users u ON r.college_id = u.id
                           JOIN items i ON r.item_id = i.item_id
                  WHERE r.status = 'Pending' \
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
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()
            sql = "UPDATE requests SET status = %s, rejection_reason = %s WHERE request_no = %s"
            cursor.execute(sql, (new_status, reason, request_id))
            conn.commit()
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
        from services.stock_manager import StockManager

        conn = get_db_connection()
        if not conn: return False
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT item_id, quantity, request_type FROM requests WHERE request_no = %s", (request_id,))
            result = cursor.fetchone()
            if not result: return False
            item_id, qty, req_type = result

            # Decrease Central Stock for Requests
            if req_type == 'Request' and 'Approved' in new_status:
                if not StockManager.adjust_central_stock(item_id, -qty):
                    return False

            # Update Status
            if not RequestManager.update_request_status(request_id, new_status, manager_id=manager_id):
                return False
            return True
        finally:
            conn.close()

    @staticmethod
    def adjust_college_custody(college_id, item_id, quantity_change):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # FIX: Changed 'quantity_custody' to 'quantity'
            sql_update = """
                         UPDATE inventory_stock
                         SET quantity = quantity + %s
                         WHERE college_id = %s \
                           AND item_id = %s \
                         """
            cursor.execute(sql_update, (quantity_change, college_id, item_id))

            if cursor.rowcount == 0:
                # FIX: Changed 'quantity_custody' to 'quantity' AND added 'location_type'
                sql_insert = """
                             INSERT INTO inventory_stock (college_id, item_id, quantity, location_type)
                             VALUES (%s, %s, %s, 'College') \
                             """
                cursor.execute(sql_insert, (college_id, item_id, quantity_change))

            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error adjusting college custody: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def _log_transaction(actor_id, action, item_ref, quantity):
        """
        Helper to append to transactions.log
        """
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"[{timestamp}] Actor: {actor_id} | Action: {action} | Item/Req: {item_ref} | Qty: {quantity}\n"

            # Using 'utf-8' encoding is safer across different OSs
            with open("transactions.log", "a", encoding="utf-8") as f:
                f.write(log_entry)

        except Exception as e:
            # Print the error instead of silently passing
            print(f"CRITICAL ERROR: Failed to write to transaction log! Reason: {e}")