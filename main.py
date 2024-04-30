from flask import Flask, jsonify, request
from flask_mysqldb import MySQL
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv
import os


load_dotenv()

app = Flask(__name__)
CORS(app, support_credentials=True)

app.config['MYSQL_HOST'] = os.getenv('MYSQL_DATABASE_HOST')
app.config['MYSQL_PORT'] = int(os.getenv('MYSQL_DATABASE_PORT'))  # Convert port to int
app.config['MYSQL_USER'] = os.getenv('MYSQL_DATABASE_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_DATABASE_PASSWORD')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DATABASE_DB')
app.config["MYSQL_CURSORCLASS"] = "DictCursor"

mysql = MySQL(app)

@app.route('/stores')
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def get_stores():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM stores""")
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
#get categories
@app.route('/categories')
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def get_categories():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM categories""")
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
@app.route('/store-add', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def post_new_store():
    try:
        print(request.form)
        store_name = request.json.get('store_name')
        
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO stores (store_name) VALUES (%s)", (store_name,))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'New partner added successfully'})
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})

@app.route('/category-add', methods=['POST'])
@cross_origin(origin='localhost',headers=['Content- Type','Authorization'])
def post_new_category():
    try:
        print(request.form)
        category_name = request.json.get('category_name')
        
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO categories (category_name) VALUES (%s)", (category_name,))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'New partner added successfully'})
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})

#get partners
@app.route('/partners')
@cross_origin(supports_credentials=True)
def get_partners():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT * FROM partners""")
        data = cursor.fetchall()
        cursor.close()
        response = jsonify(data)
        response.headers['Content-Type'] = 'application/json'
        print(response.headers)
        return response
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})

@app.route('/partner-latest-needs')
def get_partner_latest_need():
    try:
        partner_name = request.args.get('partner')
        conn = mysql.connection
        cursor = conn.cursor()
        print(partner_name)
        cursor.execute("SELECT partner_id FROM partners WHERE partner_name = %s",(partner_name,))
        existing_partner = cursor.fetchone()    
        print(existing_partner)
        partner_id = existing_partner["partner_id"]
        cursor.execute("""SELECT partner_name, item_name, quantity, units, date FROM partner_needs
                        JOIN partners USING(partner_id)
                        WHERE partner_id = %s
                        ORDER BY date DESC
                        LIMIT 10;
                        """,(partner_id,))
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
@app.route('/partner-count-series')
def get_partner_time_series_data():
    try:
        partner_name = request.args.get('partner')
        conn = mysql.connection
        cursor = conn.cursor()
        print(partner_name)
        cursor.execute("SELECT partner_id FROM partners WHERE partner_name = %s",(partner_name,))
        existing_partner = cursor.fetchone()    
        print(existing_partner)
        partner_id = existing_partner["partner_id"]
        cursor.execute("""SELECT date, COUNT(partner_needs_id) as partner_count FROM partner_needs
                            JOIN partners USING(partner_id)
                            WHERE partner_id = %s
                            GROUP BY date
                            ORDER BY date ASC;
                        """,(partner_id,))
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})


#get average spending at stores
@app.route('/avg-price')
def get_avg_price_from_stores():
    try:
        limit = request.args.get('limit', 10, type=int)
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT store_name, ROUND(AVG(total_price),2) as avg_price FROM stores 
                        JOIN purchases USING (stores_id)
                        GROUP BY store_name
                        ORDER BY avg_price DESC
                        LIMIT %s;
                        """,(limit,))
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
#get average spending at stores
@app.route('/avg-category')
def get_avg_price_from_categories():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT category_name, ROUND(AVG(price_per_unit),2) as avg_price FROM categories
                        JOIN items USING (category_id)
                        GROUP BY category_name
                        ORDER BY avg_price DESC
                        LIMIT 5;
                        """)
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
    
@app.route('/count-category')
def get_count_from_categories():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT category_name, COUNT(item_id) as category_count FROM categories
                            JOIN items USING (category_id)
                            GROUP BY category_name
                            ORDER BY category_count DESC
                            LIMIT 5;
                        """)
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
    
#get average spending at stores
@app.route('/partner-giving')
def get_avg_partner_giving():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT partner_name, COUNT(partner_needs_id) as partner_count FROM partners
                        JOIN partner_needs USING (partner_id)
                        GROUP BY partner_name
                        ORDER BY partner_count DESC;
                        """)
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})

@app.route('/partner-trends')
def get_avg_partner_trends():
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("""SELECT date, COUNT(partner_needs_id) as partner_count FROM
                        partners
                        JOIN partner_needs USING (partner_id)
                        GROUP BY date
                        ORDER BY date ASC;
                        """)
        data = cursor.fetchall()
        cursor.close()
        return jsonify(data)
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
@app.route('/partner-add', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_new_partner():
    try:
        print(request.form)
        partner_name = request.json.get('partner_name')
        
        conn = mysql.connection
        cursor = conn.cursor()
        cursor.execute("INSERT INTO partners (partner_name) VALUES (%s)", (partner_name,))
        conn.commit()
        cursor.close()
        return jsonify({'message': 'New partner added successfully'})
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})

@app.route('/partner-request', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_new_partner_request():
    try:
        post_data = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        print(post_data)
        for item in post_data:
            # Check if the partner name already exists in the database
            cursor.execute("SELECT partner_id FROM partners WHERE partner_name = %s", (item["partner_name"],))
            existing_partner = cursor.fetchone()
            if existing_partner:
                partner_id = existing_partner["partner_id"]
            else:
                continue
            name = item["itemName"]
            quantity = item["quantity"]
            units = item["units"]
            date = item["date"]
            cursor.execute("INSERT INTO partner_needs (partner_id, item_name, quantity, units, `date`) VALUES (%s, %s, %s, %s, %s)", (partner_id, name, quantity, units, date)) 
            # Here you can use the partner_id as needed
            
        conn.commit()
        print("did we get an error afte commit?")
        cursor.close()
        
        return jsonify({'message': 'New partners added successfully'})
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    
@app.route('/transaction-add', methods=['POST'])
@cross_origin(supports_credentials=True)
def post_new_transactions():
    try:
        post_data = request.json
        conn = mysql.connection
        cursor = conn.cursor()
        print(post_data)
        for item in post_data:
            # Check if the partner name already exists in the database
            cursor.execute("SELECT category_id FROM categories WHERE category_name = %s", (item["category"],))
            existing_category = cursor.fetchone()
            if existing_category:
                category_id = existing_category["category_id"]
            else:
                continue
            
            cursor.execute("SELECT stores_id FROM stores WHERE store_name = %s", (item["store"],))
            existing_store = cursor.fetchone()
            if existing_store:
               store_id = existing_store["stores_id"]
            else:
                continue
            
            name = item["item_name"]
            quantity = item["quantity"]
            units = item["unit"]
            price_per_unit = item["price_per_unit"]
            location_stored = item["location_stored"]
            date = item["date"]
            total_price = item["total_price"]
            cursor.execute("INSERT INTO items (item_name, category_id, quantity, unit, price_per_unit, location_stored) VALUES (%s, %s, %s, %s, %s, %s)", (name, category_id, quantity, units, price_per_unit, location_stored)) 
            item_id = str(cursor.lastrowid)
            cursor.execute("INSERT INTO purchases (item_id, stores_id, quantity, purchase_date, total_price) VALUES (%s, %s, %s, %s, %s)", (item_id, store_id, quantity, date, total_price)) 
            # Here you can use the partner_id as needed
            
        conn.commit()
        cursor.close()
        return jsonify({'message': 'New Transactions added successfully'})
    except Exception as e:
        print("An error occurred:", str(e))
        return jsonify({'error': str(e)})
    



if __name__ == "__main__":
    app.run(debug=True)
    