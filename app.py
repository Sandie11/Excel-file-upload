from flask import Flask, render_template, request, jsonify
from werkzeug.utils import secure_filename
import os
import pandas as pd
import pymysql

app = Flask(__name__)

UPLOAD_FOLDER = 'C:/Users/lenovo/Documents/dj'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# MySQL connection details
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '123Aa',
    'database': 'userdb',
    'cursorclass': pymysql.cursors.DictCursor
}

# Route for the index page
@app.route('/')
def index():
    return render_template('index.html')

# Route for the dashboard page
@app.route('/dashboard')
def dashboard():
    # Open a connection to the database
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # Fetch insights from the database
            cursor.execute("SELECT COUNT(*) AS total_customers FROM customers")
            total_customers = cursor.fetchone()['total_customers']

            cursor.execute("SELECT COUNT(*) AS customers_from_usa FROM customers WHERE country = 'USA'")
            customers_from_usa = cursor.fetchone()['customers_from_usa']

            cursor.execute("SELECT MAX(creditLimit) AS highest_credit_limit FROM customers")
            highest_credit_limit = cursor.fetchone()['highest_credit_limit']

            cursor.execute("SELECT AVG(creditLimit) AS average_credit_limit FROM customers")
            average_credit_limit = cursor.fetchone()['average_credit_limit']

            cursor.execute("SELECT COUNT(*) AS customers_no_sales_rep FROM customers WHERE salesRepEmployeeNumber IS NULL")
            customers_no_sales_rep = cursor.fetchone()['customers_no_sales_rep']

            # Repeat the process for other insights...

    except Exception as e:
        # Handle exceptions (e.g., log the error, provide a fallback response)
        print(f"Error: {e}")
        # You might want to render an error page or provide a meaningful response here.

    finally:
        # Close the database connection
        connection.close()

    # Render the HTML template with the fetched data
    return render_template('dashboard.html', 
                            total_customers=total_customers, 
                            customers_from_usa=customers_from_usa,
                            highest_credit_limit=highest_credit_limit,
                            average_credit_limit=average_credit_limit,
                            customers_no_sales_rep=customers_no_sales_rep)

# Route for handling file upload
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
    # Open a connection to the database
    connection = pymysql.connect(**db_config)

    try:
        with connection.cursor() as cursor:
            # Assuming 'employees' table exists in your MySQL database
            table_name = 'employees'

            # Construct SQL INSERT statement
            insert_sql = f"INSERT INTO {table_name} ({', '.join(df.columns)}) VALUES ({', '.join(['%s' for _ in df.columns])})"

            # Insert each row of data into the MySQL table
            for _, row in df.iterrows():
                cursor.execute(insert_sql, tuple(row))

        # Commit the changes
        connection.commit()

    except Exception as e:
        # Handle exceptions (e.g., log the error, provide a fallback response)
        print(f"Error: {e}")

    finally:
        # Close the database connection
        connection.close()

if __name__ == '__main__':
    app.run(debug=True)
