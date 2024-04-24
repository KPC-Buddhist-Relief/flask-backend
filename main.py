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
        print(response.headers)
        return response
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



if __name__ == "__main__":
    app.run(debug=True)
    