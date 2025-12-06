import psycopg2
from config.db_config import get_db_connection
from services.request_manager import RequestManager  # To use the logging helper


class CourierManager:
    """
    Handles Courier tasks: Pickup and Delivery for both Requests and Returns.
    [cite_start](Requirement: Courier Window tabs and actions [cite: 76])
    """

    @staticmethod
    def pickup_request(request_id, courier_id):
        """
        Courier picks up items from KSU Inventory.
        Status changes from 'Approved - Ready for Pickup' -> 'In Transit to College'
        [cite_start](Requirement: [cite: 80])
        """
        return CourierManager._update_workflow_status(
            request_id,
            courier_id,
            required_current_status='Approved - Ready for Pickup',
            new_status='In Transit to College',
            action_name='Pick Up Request'
        )

    @staticmethod
    def deliver_request(request_id, courier_id):
        """
        Courier delivers items to College.
        Status changes -> 'Delivered to College'
        [cite_start](Requirement: [cite: 81])
        """
        return CourierManager._update_workflow_status(
            request_id,
            courier_id,
            required_current_status='In Transit to College',
            new_status='Delivered to College',
            action_name='Deliver Request'
        )

    @staticmethod
    def pickup_return(request_id, courier_id):
        """
        Courier picks up return items from College.
        Status changes -> 'In Transit to Inventory'
        [cite_start](Requirement: [cite: 82])
        """
        return CourierManager._update_workflow_status(
            request_id,
            courier_id,
            required_current_status='Approved - Ready for Pickup (Return)',
            new_status='In Transit to Inventory',
            action_name='Pick Up Return'
        )

    @staticmethod
    def deliver_return(request_id, courier_id):
        """
        Courier delivers return items to KSU Inventory.
        Status changes -> 'Received at Inventory'
        [cite_start](Requirement: [cite: 83])
        Note: This should ideally triggers a stock increase in StockManager.
        """
        return CourierManager._update_workflow_status(
            request_id,
            courier_id,
            required_current_status='In Transit to Inventory',
            new_status='Received at Inventory',
            action_name='Deliver Return'
        )

    @staticmethod
    def _update_workflow_status(req_id, courier_id, required_current_status, new_status, action_name):
        """
        Generic helper method to handle status transitions safely.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False, "DB Connection Failed"
            cursor = conn.cursor()

            # 1. Verify the current status allows this action
            cursor.execute("SELECT status FROM requests WHERE request_no = %s", (req_id,))
            result = cursor.fetchone()

            if not result:
                return False, "Request ID not found."

            current_status = result[0]
            if current_status != required_current_status:
                return False, f"Invalid Action. Current status is '{current_status}', but needed '{required_current_status}'."

            # 2. Update the status
            sql = "UPDATE requests SET status = %s WHERE request_no = %s"
            cursor.execute(sql, (new_status, req_id))
            conn.commit()

            # 3. Log the transaction using the helper from RequestManager or locally
            # We use a simple local log line here matching the requirement style
            RequestManager._log_transaction(courier_id, action_name, req_id, "N/A")

            return True, f"Success: {new_status}"

        except psycopg2.Error as e:
            return False, f"Database Error: {e}"
        finally:
            if conn: conn.close()