from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import pymysql

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/lenovo/Documents/dj'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL connection settings
host = 'localhost'
port = 3306
user = 'root'
password = '123Aa'
database = 'userdb'

conn = pymysql.connect(
    host=host,
    port=port,
    user=user,
    password=password,
    database=database
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']

    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Read Excel data using pandas
        df = pd.read_excel(file_path)

        # Insert data into MySQL table
        insert_data_to_mysql(df)

        return jsonify({'message': 'File uploaded and data inserted into MySQL successfully'})
    else:
        return jsonify({'error': 'No file provided'})

def insert_data_to_mysql(df):
    cursor = conn.cursor()

    # Assuming 'employees' table exists in your MySQL database
    table_name = 'employees'

    # Construct SQL INSERT statement
    insert_sql = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s' for _ in df.columns])})"

    # Insert each row of data into the MySQL table
    for _, row in df.iterrows():
        cursor.execute(insert_sql, tuple(row))

    conn.commit()
    cursor.close()

if __name__ == '__main__':
    app.run(debug=True)
