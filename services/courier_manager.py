import psycopg2
from config.db_config import get_db_connection
from services.request_manager import RequestManager
from services.stock_manager import StockManager  # Needed for deliver_return


class CourierManager:
    # --- 1. PICKUP REQUEST (Inventory -> Courier) ---
    @staticmethod
    def get_requests_for_pickup():
        return CourierManager._fetch_requests_by_status('Approved - Ready for Pickup', 'Request')

    @staticmethod
    def pickup_request(request_id, courier_id):
        return CourierManager._update_status_and_courier(request_id, courier_id,
                                                         'Approved - Ready for Pickup', 'Picked Up by Courier')

    # --- 2. DELIVER REQUEST (Courier -> College) ---
    @staticmethod
    def get_requests_for_delivery():
        """Get items currently with the courier, heading to college."""
        return CourierManager._fetch_requests_by_status('Picked Up by Courier', 'Request')

    @staticmethod
    def deliver_request(request_id):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # Fetch details to update custody
            cursor.execute("SELECT item_id, quantity, college_id FROM requests WHERE request_no = %s", (request_id,))
            req_data = cursor.fetchone()
            if not req_data: return False
            item_id, quantity, college_id = req_data

            # Update Status
            sql_status = "UPDATE requests SET status = 'Delivered to College' WHERE request_no = %s AND status = 'Picked Up by Courier'"
            cursor.execute(sql_status, (request_id,))
            if cursor.rowcount == 0: return False

            # Increase College Custody
            RequestManager.adjust_college_custody(college_id, item_id, quantity)
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error delivering request: {e}")
            return False
        finally:
            if conn: conn.close()

    # --- 3. PICKUP RETURN (College -> Courier) ---
    @staticmethod
    def get_returns_for_pickup():
        return CourierManager._fetch_requests_by_status('Approved - Ready for Pickup (Return)', 'Return')

    @staticmethod
    def pickup_return(request_id, courier_id):
        return CourierManager._update_status_and_courier(request_id, courier_id,
                                                         'Approved - Ready for Pickup (Return)',
                                                         'In Transit to Inventory')

    # --- 4. DELIVER RETURN (Courier -> Inventory) ---
    @staticmethod
    def get_returns_for_delivery():
        return CourierManager._fetch_requests_by_status('In Transit to Inventory', 'Return')

    @staticmethod
    def deliver_return(request_id):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # Fetch details
            cursor.execute("SELECT item_id, quantity FROM requests WHERE request_no = %s", (request_id,))
            req_data = cursor.fetchone()
            if not req_data: return False
            item_id, quantity = req_data

            # Update Status
            sql = "UPDATE requests SET status = 'Received at Inventory' WHERE request_no = %s AND status = 'In Transit to Inventory'"
            cursor.execute(sql, (request_id,))
            if cursor.rowcount == 0: return False

            # Increase Central Stock
            StockManager.adjust_central_stock(item_id, quantity)

            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error delivering return: {e}")
            return False
        finally:
            if conn: conn.close()

    # --- HELPER FUNCTIONS ---
    @staticmethod
    def _fetch_requests_by_status(status, req_type):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()
            sql = """
                  SELECT r.request_no, u.first_name, i.name, r.quantity, r.request_type, r.purpose_notes
                  FROM requests r
                           JOIN users u ON r.college_id = u.id
                           JOIN items i ON r.item_id = i.item_id
                  WHERE r.status = %s \
                    AND r.request_type = %s
                  ORDER BY r.request_no \
                  """
            cursor.execute(sql, (status, req_type))
            return cursor.fetchall()
        except psycopg2.Error:
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def _update_status_and_courier(request_id, courier_id, current_status, new_status):
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()
            sql = "UPDATE requests SET status = %s, courier_id = %s WHERE request_no = %s AND status = %s"
            cursor.execute(sql, (new_status, courier_id, request_id, current_status))
            if cursor.rowcount == 0: return False
            conn.commit()
            return True
        except psycopg2.Error:
            return False
        finally:
            if conn: conn.close()