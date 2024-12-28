import sqlite3

def init_db():
    conn = sqlite3.connect('chatbot.db')  # Creates a database file named chatbot.db
    cursor = conn.cursor()

   
    # Create the orders table with a new 'status' column
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            items TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'Pending'
        )
    ''')
    
    # Create the menu table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS menu (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_name TEXT NOT NULL UNIQUE
        )
    ''')

     # Add menu items
    items = ['Pizza', 'Pasta', 'Salads', 'Burgers']
    for item in items:
        try:
            cursor.execute('INSERT INTO menu (item_name) VALUES (?)', (item,))
        except sqlite3.IntegrityError:
            pass  # Skip if item already exists

    conn.commit()
    conn.close()

# Initialize the database when the script runs
if __name__ == '__main__':
    init_db()
