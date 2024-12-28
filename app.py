import sqlite3
from database import init_db
from flask import Flask, request, jsonify
init_db()
app = Flask(__name__)

# Dynamic menu items
menu = ['Pizza', 'Pasta', 'Salad', 'Burger', 'Fries']

# Chat endpoint
@app.route('/chat', methods=['POST'])
def chat():
    # Ensure the request is JSON
    if not request.is_json:
        return jsonify({'error': 'Unsupported Media Type. Please send JSON with Content-Type header set to application/json.'}), 415

    # Get user message
    data = request.get_json()
    print("Incoming request data:", data)  # Debug: Print the received JSON data
    user_message = data.get('message', '').lower()
    
    print("User message:", user_message)  # Debug: Print the extracted message
    if 'menu' in user_message:
        return jsonify({'response': f"Our menu includes: {', '.join(menu_items)}. What would you like to order?"})
    elif 'order' in user_message:
        return jsonify({'response': 'Please provide your name, contact details, and the items you want to order.'})
    else:
        return jsonify({'response': 'Hello! I can help you place an order. Ask me about our menu or start placing an order.'})

# order endpoint
@app.route('/order', methods=['POST'])
def order():
    data = request.get_json()
    name = data.get('name', '')
    address = data.get('address', '')
    items = data.get('items', [])

    if not name or not address or not items:
        return jsonify({'error': 'Missing required fields: name, address, and items.'}), 400

    # Connect to the database
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    # Validate items
    cursor.execute('SELECT item_name FROM menu')
    menu_items = [row[0] for row in cursor.fetchall()]
    invalid_items = [item for item in items if item not in menu_items]

    if invalid_items:
        return jsonify({'error': f"The following items are not on the menu: {', '.join(invalid_items)}"}), 400

    # Save the order with status 'Pending'
    cursor.execute(
        'INSERT INTO orders (name, address, items, status) VALUES (?, ?, ?, ?)',
        (name, address, ', '.join(items), 'Pending')
    )
    conn.commit()
    conn.close()

    return jsonify({'response': f"Thank you! Your order has been placed for {', '.join(items)} to be delivered to {address}. Status: Pending"})

# get the order from database endpoint
@app.route('/orders', methods=['GET'])
def get_orders():
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    # Fetch all orders
    cursor.execute('SELECT * FROM orders')
    orders = cursor.fetchall()
    conn.close()

    # Format the data for JSON response
    order_list = [
        {'id': row[0], 'name': row[1], 'address': row[2], 'items': row[3]} for row in orders
    ]
    return jsonify({'orders': order_list})

#View Order Status endpoint
@app.route('/order/status/<int:order_id>', methods=['GET'])
def order_status(order_id):
    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    # Fetch the order by ID
    cursor.execute('SELECT id, name, address, items, status FROM orders WHERE id = ?', (order_id,))
    order = cursor.fetchone()
    conn.close()

    if not order:
        return jsonify({'error': 'Order not found.'}), 404

    # Return order status
    return jsonify({
        'id': order[0],
        'name': order[1],
        'address': order[2],
        'items': order[3],
        'status': order[4]
    })

#Endpoint to Update Order Status
@app.route('/order/status/update/<int:order_id>', methods=['PATCH'])
def update_order_status(order_id):
    data = request.get_json()
    new_status = data.get('status', '')

    if new_status not in ['Pending', 'In Progress', 'Completed']:
        return jsonify({'error': 'Invalid status. Choose from: Pending, In Progress, Completed.'}), 400

    conn = sqlite3.connect('chatbot.db')
    cursor = conn.cursor()

    # Update order status
    cursor.execute('UPDATE orders SET status = ? WHERE id = ?', (new_status, order_id))
    conn.commit()

    if cursor.rowcount == 0:
        return jsonify({'error': 'Order not found.'}), 404

    conn.close()

    return jsonify({'response': f'Order {order_id} status has been updated to {new_status}.'})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
