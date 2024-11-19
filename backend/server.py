import numpy as np
from flask import Flask, request, jsonify, render_template
import pickle
from sklearn.preprocessing import LabelEncoder
import mysql.connector
import requests

# create flask app
app = Flask(__name__)

#db configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Butterflies@99',
    'database': 'supplychaindata'
}

connection = mysql.connector.connect(**db_config)

class userIdManagement:
    def __init__(self,userId = 0) :
        self._userId = userId

    def get_userId(self):
        return self._userId
    
    def set_userId(self, id):
        self._userId = id

user_id = userIdManagement()

#Add user data to the database
@app.route('/add_user_data', methods=['POST'])
def add_user_data():
    data = request.get_json()
    print(data)
    features = list(data['features'].values())
    print(features)

    first_name = features[0]
    last_name = features[1]
    email = features[2]
    username = features[3]
    password = features[4]

    cursor = connection.cursor()

    query = "SELECT EXISTS(SELECT id FROM users WHERE username = %s)"
    cursor.execute(query, (username,))
    exists = cursor.fetchone()[0]

    if (exists) :
        return jsonify({'message':'This username exists.Try something else!'})
    else :
        query1 = "INSERT INTO users (first_name, last_name, email, username, password_hash) VALUES(%s,%s,%s,%s,%s)"
        cursor.execute(query1, (first_name, last_name, email, username, password) )
        connection.commit()

        query2 = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query2, (username,))
        id = cursor.fetchall()
        print(id)
        user_id.set_userId(id[0][0])
        print(user_id.get_userId())


        cursor.close()
        return jsonify({'message':'Signed Up Successfully'})
    
    

#Get user login data from the database
@app.route('/user_data', methods=['GET'])
def user_data(data):
    username = data["username"]
    password = data["password"]

    cursor = connection.cursor()

    query = "SELECT EXISTS(SELECT id FROM users WHERE username = %s AND password_hash = %s )"
    cursor.execute(query, (username,password,))
    exists = cursor.fetchone()[0]  
    print(exists)

    if (exists):
        query = "SELECT id FROM users WHERE username = %s"
        cursor.execute(query, (username,))
        id = cursor.fetchall()  
        id = id[0][0]
        print(id)
        user_id.set_userId(id)
        print(user_id.get_userId())

        cursor.close()
        return jsonify({'exists':'exists'})
    
    else:
        cursor.close()
        return jsonify({'message': 'Please check the username or password again.'})

@app.route('/login_user', methods=['POST'])
def login_user():    
    data = request.get_json()
    print(data)
    response = user_data(data)
    return response

#Get Coordinates
@app.route('/get_coordinates', methods=['POST'])
def get_coordinates(location):
    location = location
    api_key = 'AIzaSyDeHr2FSo1LjzLrunLPWTE93JQ5zL7TNfY'

    url = f'https://maps.googleapis.com/maps/api/geocode/json?address={location}&key=AIzaSyAO2xk4_v7YfoqREfW5qQt7Fhzp2yoAv24'

    response = requests.get(url)
    print(response)
    
    if response.status_code == 200:
        data = response.json()
        print(data)
        if data['status'] == 'OK':
            result = data['results'][0]
            coordinates = result['geometry']['location']
            latitude = coordinates['lat']
            longitude = coordinates['lng']
            return ({'latitude': latitude, 'longitude': longitude})
        else:
            return ({'error': 'Location not found'})
    
    else:
        return jsonify({'error': 'Failed to get coordinates'}), 500

#Add data to the database
@app.route('/add_data', methods=['POST'])
def add_data():
    data = request.get_json()
    print(data)
    features = list(data['features'].values())

    customer_city = features[0]
    customer_country = features[1]
    order_city = features[2]

    coord = get_coordinates(order_city)

    print(coord)
    order_country = features[3]
    latitude = features[4]
    longitude = features[5]
    order_date = features[6]
    order_item_quantity = features[7]
    shipping_mode = features[8]

    userId = user_id.get_userId()
    print(user_id._userId)

    cursor = connection.cursor()
    query = "INSERT INTO sc_data (customer_city,customer_country,order_city, order_country, latitude, longitude, order_date, order_item_quantity, shipping_mode, user_id) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
    cursor.execute(query, (customer_city,customer_country,order_city, order_country, latitude, longitude, order_date, order_item_quantity, shipping_mode, userId,) )
    connection.commit()

    cursor.close()
    return jsonify({'message':'Data saved successfully'})
    
#Check if an order exists
def check_order_exists(order_id):
    cursor = connection.cursor()
    userId = user_id.get_userId()
    query = "SELECT EXISTS(SELECT 1 FROM sc_data WHERE order_id = %s AND user_id = %s)"
    cursor.execute(query, (order_id,userId,))
    exists = cursor.fetchone()[0]  # Get the first element from the single-row result

    cursor.close()

    return exists

#Fetch all the data to display
@app.route('/fetch_data', methods=['POST'])
def fetch_data():
    data = get_data()
    keys = ['order_id','customer_city','customer_country','order_city', 'order_country', 'latitude', 'longitude', 'order_date', 'order_item_quantity', 'shipping_mode']
    jsonDataList = []
    for row in data:
        jsonDataList.append(dict(zip(keys,row)))
    print(jsonDataList)
    return jsonify({'orderDetails':jsonDataList})

@app.route('/get_data', methods=['GET'])
def get_data():
    userId = user_id.get_userId()
    print(user_id._userId)
    cursor = connection.cursor()
    query = "SELECT * FROM sc_data WHERE user_id = %s"
    cursor.execute(query, (userId,))
    data = cursor.fetchall()
    cursor.close()

    return data

#Get data from the database
@app.route('/retrieve_data', methods=['GET'])
def retrieve_data(data):

    orderId = int(data["features"]["order_id"])
    exists = check_order_exists(orderId)
    if exists:
        userId = user_id.get_userId()
        print(user_id._userId)
        cursor = connection.cursor()
        query = "SELECT * FROM sc_data WHERE order_id = %s AND user_id = %s"
        cursor.execute(query,(orderId, userId,))
        data = cursor.fetchall()
        print(data)
        data_list = list(data[0])
        data_list.pop(0)

        keys = ['customer_city','customer_country','order_city', 'order_country', 'latitude', 'longitude', 'order_date', 'order_item_quantity', 'shipping_mode']
        jsonifyDataList = dict(zip(keys,data_list))

        cursor.close()
        return jsonifyDataList
    else:
        return ({'message': 'Order ID was not found'})

#Retrieve one order details
@app.route('/retrieve_order', methods = ['POST'])
def retrieve_order():
    data = request.get_json()
    features = retrieve_data(data)
    print(features)
    featuresList = list(features.values())
    if len(featuresList)>1:
        return jsonify({'orderDetails':features})
    
    else:
        message = features.get('message')
        return jsonify({'message':message})
    
#Remove data from the table
@app.route("/delete_data", methods = ['POST'])
def delete_row():
    data = request.get_json()
    orderId = int(data["features"]["order_id"])
    cursor = connection.cursor()
    query = "DELETE FROM sc_data WHERE order_id = %s"
    cursor.execute(query,(orderId,))
    connection.commit()

    cursor.close()

    return jsonify({'message':'Order deleted successfully!'}),200  # Return success message with status code

#Load the pickle model  
model = pickle.load(open("model.pkl", "rb"))

@app.route('/predict', methods = ['POST'])
def predict():
    data = request.get_json()
    features = retrieve_data(data)
    featuresList = list(features.values())
    if len(featuresList)>1:
        le = LabelEncoder()
        encodedFeatures = le.fit_transform(featuresList) #extract and transform the request
        processedFeatures = [np.array(encodedFeatures)]
        prediction = model.predict(processedFeatures) #make prediction using the model
        if(prediction[0] == 1):
            predicitonResult = "Late"
        else:
            predicitonResult = "Not Late"
        return jsonify({'orderDetails':features ,'prediction': predicitonResult})
    
    else:
        message = features.get('message')
        return jsonify({'message':message})

if __name__ == "__main__":
    app.run(debug=True)


