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

            # Note: Using 'quantity_central' based on your DB screenshot
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
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # FIX: Explicitly selecting columns to match Manager Window treeview order
            # (ID, Name, Cat, Unit, Lvl, Qty)
            if filter_category:
                sql = "SELECT item_id, name, category, unit, reorder_level, quantity_central FROM items WHERE category = %s"
                cursor.execute(sql, (filter_category,))
            else:
                sql = "SELECT item_id, name, category, unit, reorder_level, quantity_central FROM items ORDER BY item_id"
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

            # FIX: Changed 'id' to 'item_id'
            cursor.execute("DELETE FROM items WHERE item_id = %s", (item_id,))
            conn.commit()
            return True
        except psycopg2.Error as e:
            print(f"DB Error deleting item: {e}")
            return False
        finally:
            if conn: conn.close()

    # ---------------------------------------------------------
    # PART 2: STOCK MOVEMENT & DASHBOARD
    # ---------------------------------------------------------

    @staticmethod
    def adjust_central_stock(item_id, quantity_change):
        """
        Updates the quantity in the central warehouse.
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False
            cursor = conn.cursor()

            # FIX: Changed 'id' to 'item_id'
            sql = "UPDATE items SET quantity_central = quantity_central + %s WHERE item_id = %s"
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
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # FIX: Joined with inventory_stock and used 'item_id'
            sql = """
                SELECT i.name, s.quantity
                FROM inventory_stock s
                JOIN items i ON s.item_id = i.item_id
                WHERE s.college_id = %s
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
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return False, "Connection Failed"
            cursor = conn.cursor()

            tables = ['users', 'items', 'requests', 'inventory_stock']

            with open('backup.csv', 'w', newline='') as f:
                writer = csv.writer(f)

                for table in tables:
                    try:
                        cursor.execute(f"SELECT * FROM {table}")
                        rows = cursor.fetchall()
                        if cursor.description:
                            col_names = [desc[0] for desc in cursor.description]
                            writer.writerow([f"--- TABLE: {table} ---"])
                            writer.writerow(col_names)
                            writer.writerows(rows)
                            writer.writerow([])
                    except psycopg2.Error:
                        continue

            return True, "Backup created successfully as backup.csv"

        except Exception as e:
            return False, f"Backup Error: {e}"
        finally:
            if conn: conn.close()

    @staticmethod
    def get_all_college_custody():
        """
        Retrieves custody balances for all colleges.
        (Requirement: per-college custody balances [cite: 56])
        """
        conn = None
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            # Join to get College Name (from users) and Item Name
            sql = """
                  SELECT u.first_name, i.name, s.quantity
                  FROM inventory_stock s
                           JOIN users u ON s.college_id = u.id
                           JOIN items i ON s.item_id = i.item_id
                  WHERE s.quantity > 0
                  ORDER BY u.first_name \
                  """
            cursor.execute(sql)
            return cursor.fetchall()
        except psycopg2.Error as e:
            print(f"DB Error fetching all custody: {e}")
            return []
        finally:
            if conn: conn.close()