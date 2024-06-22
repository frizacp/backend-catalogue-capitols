from flask import Flask, request, jsonify
import mysql.connector
from flask_cors import CORS
import os

os.environ['OPENBLAS_NUM_THREADS'] = '1'
app = Flask(__name__)
CORS(app)
app.config.from_object('config.Config')
app.config['CORS_HEADERS'] = 'Content-Type'

# AMBIL DATA DARI FILE CONFIG
DB_CONFIG = app.config['DB_CONFIG']
DB_CONFIG2 = app.config['DB_CONFIG_DEV']
PW_LIST = app.config['PW_DATA']

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    password = data.get('password')

    # Check if the password is in any of the dictionaries in the list
    for entry in PW_LIST:
        if entry["pass"] == password:
            return jsonify({"success": True, "idtype": entry["id_type"]}), 200
    
    # If no match is found
    return jsonify({"success": False}), 200
        


@app.route('/products', methods=['GET'])
def get_products():
    id_category = request.args.get('id_category', 2)
    id_type = str(request.args.get('id_type', 11))
    # Koneksi ke database
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    
    # Query untuk mengambil semua produk

    if id_type == "11":
        query = """ SELECT p.id, p.id_category, p.code, p.article, p.size, p.qty, c.price_1 AS price, c.thumbnail FROM product p LEFT JOIN catalogue c ON p.article = c.article WHERE p.id_category = %s AND p.qty > 0"""
    elif id_type == "21":
        query = """ SELECT p.id, p.id_category, p.code, p.article, p.size, p.qty, c.price_2 AS price, c.thumbnail FROM product p LEFT JOIN catalogue c ON p.article = c.article WHERE p.id_category = %s AND p.qty > 0"""
    cursor.execute(query, (id_category,))
    products = cursor.fetchall()
    
    # Menutup koneksi database
    cursor.close()
    conn.close()
    
  # Mengelompokkan produk berdasarkan artikel
    grouped_data = {}
    for product in products:
        article = product['article']
        if article not in grouped_data:
            grouped_data[article] = {
                'article': article,
                'price': product['price'],
                'thumbnail': product['thumbnail'],
                'detail': []
            }
        grouped_data[article]['detail'].append({
            'id': product['id'],
            'code': product['code'],
            'size': product['size'],
            'qty': product['qty']
        })
    
    # Mengonversi hasil ke format yang diinginkan
    response_data = {'data': list(grouped_data.values())}
    return jsonify(response_data)

@app.route('/search', methods=['GET'])
def search_product():
    article = request.args.get('article')
    id_category = request.args.get('id_category', 2)
    id_type = request.args.get('id_type')
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor(dictionary=True)
    if id_type == "11":
        query = """ SELECT p.id, p.id_category, p.code, p.article, p.size, p.qty, c.price_1 AS price, c.thumbnail FROM product p LEFT JOIN catalogue c ON p.article = c.article WHERE p.article LIKE %s AND p.id_category = %s """
    elif id_type == "21":
        query = """ SELECT p.id, p.id_category, p.code, p.article, p.size, p.qty, c.price_2 AS price, c.thumbnail FROM product p LEFT JOIN catalogue c ON p.article = c.article WHERE p.article LIKE %s AND p.id_category = %s """
    cursor.execute(query, (f"%{article}%", id_category))
    products = cursor.fetchall()
    cursor.close()

    print(products)

      # Mengelompokkan produk berdasarkan artikel
    grouped_data = {}
    for product in products:
        article = product['article']
        if article not in grouped_data:
            grouped_data[article] = {
                'article': article,
                'price': product['price'],
                'thumbnail': product['thumbnail'],
                'detail': []
            }
        grouped_data[article]['detail'].append({
            'id': product['id'],
            'code': product['code'],
            'size': product['size'],
            'qty': product['qty']
        })

    # Mengonversi hasil ke format yang diinginkan
    response_data = {'data': list(grouped_data.values())}
    return jsonify(response_data)

if __name__ == '__main__':
    app.run(debug=True)