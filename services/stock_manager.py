import psycopg2
import csv
from config.db_config import get_db_connection


class StockManager:
    """
    Handles Inventory Management:
    1. Item Master CRUD (Create, Read, Update, Delete).
    2. Stock Dashboard (Central Inventory & College Custody).
    3. Database Backup.
    """

    # ---------------------------------------------------------
    # PART 1: ITEM MASTER MANAGEMENT (CRUD)
    # ---------------------------------------------------------

    @staticmethod
    def add_item(name, category, unit, initial_quantity, reorder_level):
        """
        Adds a new item to the central inventory catalog.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            sql = """
                INSERT INTO items (name, category, unit, quantity_central, reorder_level)
                VALUES (%s, %s, %s, %s, %s)
            """
            cursor.execute(sql, (name, category, unit, initial_quantity, reorder_level))
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error adding item: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_all_items(filter_category=None):
        """
        Retrieves items for the list or dashboard.
        Supports filtering by category[cite: 57].
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            if filter_category:
                sql = "SELECT * FROM items WHERE category = %s"
                cursor.execute(sql, (filter_category,))
            else:
                sql = "SELECT * FROM items"
                cursor.execute(sql)

            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"DB Error fetching items: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def delete_item(item_id):
        """
        Deletes an item from the master list.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            cursor.execute("DELETE FROM items WHERE id = %s", (item_id,))
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error deleting item: {e}")
            return False
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # PART 2: STOCK MOVEMENT & DASHBOARD [cite: 56]
    # ---------------------------------------------------------

    @staticmethod
    def adjust_central_stock(item_id, quantity_change):
        """
        Updates the quantity in the central warehouse.
        - Negative quantity_change for Approved Requests (Reservation).
        - Positive quantity_change for Received Returns.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # Update quantity
            sql = "UPDATE items SET quantity_central = quantity_central + %s WHERE id = %s"
            cursor.execute(sql, (quantity_change, item_id))
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error adjusting central stock: {e}")
            return False
        finally:
            if conn: conn.close()

    @staticmethod
    def get_low_stock_alerts():
        """
        Returns items where current quantity is below reorder level.
        (Requirement: Low-stock alerts based on Reorder Level [cite: 56])
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            sql = "SELECT name, quantity_central, reorder_level FROM items WHERE quantity_central <= reorder_level"
            cursor.execute(sql)
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"DB Error fetching alerts: {e}")
            return []
        finally:
            if conn: conn.close()

    @staticmethod
    def get_college_custody(college_id):
        """
        Shows quantities currently held by a specific college.
        (Requirement: per-college custody balances [cite: 56])
        Assuming a table 'college_stock' exists.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            sql = """
                SELECT i.name, cs.quantity
                FROM college_stock cs
                JOIN items i ON cs.item_id = i.id
                WHERE cs.college_id = %s
            """
            cursor.execute(sql, (college_id,))
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"DB Error fetching college custody: {e}")
            return []
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # PART 3: BACKUP
    # ---------------------------------------------------------

    @staticmethod
    def backup_database():
        """
        Exports the entire central DB tables to CSV.
        (Requirement: Export the entire central DB to CSV (backup.csv))
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False, "Connection Failed"
            cursor = conn.cursor()

            # We will dump the 'items' table as the main example,
            # but ideally, you loop through all tables (users, requests, etc.)
            tables = ['users', 'items', 'requests', 'college_stock']

            with open('backup.csv', 'w', newline='') as f:
                writer = csv.writer(f)

                for table in tables:
                    try:
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        col_names = [desc[0] for desc in cursor.description]

                        # Write a header indicating the table name
                        writer.writerow([f"--- TABLE: {table} ---"])
                        writer.writerow(col_names)
                        writer.writerows(rows)
                        writer.writerow([])  # Empty line between tables
                    except psycopg2.Error:
                        continue  # Skip if table doesn't exist yet

            return True, "Backup created successfully as backup.csv"

        except Exception as e:
            return False, f"Backup Error: {e}"
        finally:
            if conn: conn.close()