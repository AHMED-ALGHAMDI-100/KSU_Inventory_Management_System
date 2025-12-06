import psycopg2
from config.db_config import get_db_connection

class InventoryItem:
    """
    Represents an Item in the KSU Inventory.
    Used for displaying the Catalog in College Window and managing items in Manager Window.
    """
    def __init__(self, item_id, name, category, unit, reorder_level, quantity_central):
        self.id = item_id
        self.name = name
        self.category = category
        self.unit = unit
        self.reorder_level = reorder_level
        self.quantity_central = quantity_central

    @staticmethod
    def get_catalog():
        """
        Retrieves all items available in the central inventory.
        Used to populate the 'Select Item' dropdown in the Request Item tab.
        (Requirement: Select Item from catalog)
        """
        conn = None
        items = []
        try:
            conn = get_db_connection()
            if conn is None: return []
            cursor = conn.cursor()

            sql = "SELECT item_id, name, category, unit, reorder_level, quantity_central FROM items ORDER BY name"
            cursor.execute(sql)
            rows = cursor.fetchall()

            for row in rows:
                # Create an object for each row
                # row order matches SQL: 0=id, 1=name, 2=cat, 3=unit, 4=reorder, 5=qty
                item = InventoryItem(row[0], row[1], row[2], row[3], row[4], row[5])
                items.append(item)

            return items

        except psycopg2.Error as e:
            print(f"Error fetching catalog: {e}")
            return []
        finally:
            if conn: conn.close()

    def __str__(self):
        # Useful for debugging or display
        return f"{self.name} ({self.unit}) - Available: {self.quantity_central}"