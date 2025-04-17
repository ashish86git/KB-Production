from flask import Flask, render_template,request, redirect, url_for,jsonify,flash
import mysql.connector
from werkzeug.security import generate_password_hash
import time
from flask import session
from mysql.connector import Error
from werkzeug.security import generate_password_hash, check_password_hash  # For secure password storage
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message


app = Flask(__name__)
app.secret_key = "your_secret_key"
# Database configurationpythone
db_config = {
    'host': '127.0.0.1',
    'user': 'root',
    'password': 'WJ28@krhps',
    'database': 'Kb_production',
    'port': 3306
}

# Test database connection on startup
try:
    conn = mysql.connector.connect(**db_config)
    if conn.is_connected():
        print("Connected to the database")
    conn.close()
except Error as err:
    print(f"Database connection failed: {err}")


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/hrms')
def hrms():
    # Handle the HRMS page or redirection
    return "HRMS Page - Here you will manage HR information."


# Route for the create profile page
@app.route('/create-profile', methods=['GET', 'POST'])
def create_profile():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')

        # Validate input fields
        if not username or not email or not password or not password_confirm:
            return jsonify({'status': 'error', 'message': 'All fields are required'}), 400

        # Check if passwords match
        if password != password_confirm:
            return jsonify({'status': 'error', 'message': 'Passwords do not match'}), 400

        # Hash the password
        hashed_password = generate_password_hash(password)

        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Corrected SQL query: Matches placeholders with parameters
            query = "INSERT INTO users (username, email, password,password_confirm) VALUES (%s, %s, %s,%s)"
            values = (username, email, hashed_password,password_confirm)

            cursor.execute(query, values)  # Execute query with proper parameters
            conn.commit()

            # Close connections
            cursor.close()
            conn.close()

            return redirect(url_for('home'))

        except Error as err:
            print(f"Database Error: {err}")  # Debugging message
            return jsonify({'status': 'error', 'message': 'Failed to sign up'}), 500

    # Render the create profile template
    return render_template('create_profile.html')


@app.route('/signin', methods=['GET', 'POST'])
def signin():
    if request.method == 'POST':
        # Retrieve login details
        email = request.form.get('email')
        password = request.form.get('password')
        print(email)

        if not email or not password:
            return render_template('login.html', error="Email and password are required!")

        try:
            # Connect to the database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor(dictionary=True)  # Fetch results as dictionary

            # Query to fetch user details
            query = "SELECT  email, password FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user = cursor.fetchone()

            cursor.close()
            conn.close()

            # Check if user exists and verify password
            if user and check_password_hash(user['password'], password):
                # Store user ID in session
                #session['user_id'] = user['id']
                return redirect(url_for('my_work'))  # Redirect to dashboard

            # Authentication failed
            return render_template('login.html', error="Invalid email or password!")

        except Error as err:
            print(f"Database Error: {err}")
            return jsonify({'status': 'error', 'message': 'Login failed'}), 500

    # Render the sign-in form on GET request
    return render_template('login.html')

# Route for the dashboard page
# @app.route('/dashboard')
# def dashboard():
#     return render_template('project_dashboard.html')
@app.route('/my_work')
def my_work():
    return render_template('my_work.html')


# Route for the new project page
# Route for the new project page
@app.route('/my_work/project_dashboard')
def project_dashboard():
    return render_template('project_dashboard.html')

# Route for Dashboard (Main Page)
@app.route('/dashboard')
def dashboard():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all projects
        cursor.execute("SELECT * FROM projects ORDER BY project_id DESC")
        projects = cursor.fetchall()

        # Fetch all shoots
        cursor.execute("SELECT * FROM shoots ORDER BY shoot_id DESC")
        shoots = cursor.fetchall()

        # Fetch all deliverables
        cursor.execute("SELECT * FROM deliverables ORDER BY deliverable_id DESC")
        deliverables = cursor.fetchall()

        # Fetch all payment schedules
        cursor.execute("SELECT * FROM payment_schedule ORDER BY payment_id DESC")
        payment_schedules = cursor.fetchall()

        # Fetch all received payments
        cursor.execute("SELECT * FROM received_payments ORDER BY received_id DESC")
        received_payments = cursor.fetchall()

        return render_template('dashboard.html', 
                               projects=projects, 
                               shoots=shoots, 
                               deliverables=deliverables, 
                               payment_schedules=payment_schedules, 
                               received_payments=received_payments)

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return "Error fetching data", 500

    finally:
        cursor.close()
        conn.close()


# 📌 API to Fetch Data for Auto-Refresh
@app.route('/api/data', methods=['GET'])
def fetch_data():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # Fetch all projects
        cursor.execute("SELECT * FROM projects ORDER BY project_id DESC")
        projects = cursor.fetchall()

        # Fetch all shoots
        cursor.execute("SELECT * FROM shoots ORDER BY shoot_id DESC")
        shoots = cursor.fetchall()

        # Fetch all deliverables
        cursor.execute("SELECT * FROM deliverables ORDER BY deliverable_id DESC")
        deliverables = cursor.fetchall()

        # Fetch all payment schedules
        cursor.execute("SELECT * FROM payment_schedule ORDER BY payment_id DESC")
        payment_schedules = cursor.fetchall()

        # Fetch all received payments
        cursor.execute("SELECT * FROM received_payments ORDER BY received_id DESC")
        received_payments = cursor.fetchall()

        return jsonify({
            'projects': projects,
            'shoots': shoots,
            'deliverables': deliverables,
            'payment_schedules': payment_schedules,
            'received_payments': received_payments
        })

    except mysql.connector.Error as err:
        return jsonify({'error': str(err)}), 500

    finally:
        cursor.close()
        conn.close()

# @app.route('/my_work/project_dashboard/new_project')
# def new_project():
#     return render_template('new_project.html')
@app.route('/my_work/project_dashboard/new_project', methods=['GET', 'POST'])
def new_project():
    if request.method == 'POST':
        try:
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()

            # Retrieve form data
            project_name = request.form.get('project_name')
            package_cost = request.form.get('package_cost')
            client_name = request.form.get('client_name')
            relation = request.form.get('relation')
            phone_number = request.form.get('phone_number')
            country = request.form.get('country')
            email = request.form.get('email')

            # Insert into projects table
            insert_project_query = """
            INSERT INTO projects (project_name, package_cost, client_name, relation, phone_number, country, email)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_project_query, (project_name, package_cost, client_name, relation, phone_number, country, email))
            project_id = cursor.lastrowid  # Get the ID of the inserted project

            #Insert Shoots
            shoot_title = request.form.get('shoot_title[]')
            shoot_date = request.form.get('shoot_date[]')
            shoot_time = request.form.get('shoot_time[]')
            shoot_city = request.form.get('shoot_city[]')

            insert_shoot_query = """
            INSERT INTO shoots (project_id, shoot_title, shoot_date, shoot_time, shoot_city)
            VALUES (%s, %s, %s, %s, %s)
            """
            for title, date, time, city in zip(shoot_title, shoot_date, shoot_time,shoot_city):
                cursor.execute(insert_shoot_query, (project_id,shoot_title,shoot_date,shoot_time,shoot_city))

            # Insert Deliverables
            deliverable_title = request.form.get('deliverable_title[]')
            deliverable_cost = request.form.get('deliverable_cost[]')
            deliverable_quantity = request.form.get('deliverable_quantity[]')
            deliverable_due_date = request.form.get('deliverable_due_date[]')

            insert_deliverable_query = """
            INSERT INTO deliverables (project_id, deliverable_title, deliverable_cost, deliverable_quantity, deliverable_due_date)
            VALUES (%s, %s, %s, %s, %s)
            """
            for title, cost, quantity, due_date in zip(deliverable_title, deliverable_cost, deliverable_quantity, deliverable_due_date):
                cursor.execute(insert_deliverable_query, (project_id, deliverable_title, deliverable_cost, deliverable_quantity, deliverable_due_date))

            # # Insert Payment Schedule
            amount = request.form.getlist('amount[]')
            description = request.form.getlist('description[]')
            due_date = request.form.getlist('due_date[]')

            insert_payment_query = """
            INSERT INTO payment_schedule (project_id, amount, description, due_date)
            VALUES (%s, %s, %s, %s)
            """

            for amount, description, due_date in zip(amount, description, due_date):
                cursor.execute(insert_payment_query, (project_id, amount, description, due_date))
            
            conn.commit()  
            return jsonify({'status': 'success', 'message': 'Project added successfully!'}), 400

        except Error as err:
            print(f"Database Error: {err}")
            return jsonify({'status': 'error', 'message': 'Login failed'}), 500
        finally:
            cursor.close()
            conn.close()

        return redirect('/my_work/project_dashboard/new_project')

    return render_template('new_project.html')




@app.route('/my_work/shoots_dashboard')
def shoots_dashboard():
    return render_template('shoots_dashboard.html')

@app.route('/my_work/shoots_dashboard/get_shoots', methods=['GET'])
def get_shoots():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)  # Returns data as dictionaries

        # Fetch all shoot records
        cursor.execute("SELECT * FROM new_shoot")
        shoots = cursor.fetchall()  # Returns a list of dictionaries
        #print(shoots)
        return jsonify({
            'status': 'success',
            'shoots': shoots
        })
    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        return jsonify({'status': 'error', 'message': 'Database Error'}), 500

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()



@app.route('/my_work/shoots_dashboard/new_shoot', methods=['GET', 'POST'])
def new_shoot():
    if request.method == 'POST':
        try:
            # Connect to Database
            conn = mysql.connector.connect(**db_config)
            cursor = conn.cursor()
            # Get Form Data
            project = request.form.get('project', '').strip()
            shoot = request.form.get('shoot', '').strip()
            custom_shoot = request.form.get('custom_shoot', '').strip()  
            date = request.form.get('date', '').strip()
            reporting_time = request.form.get('reporting_time', '').strip()
            duration_hours = request.form.get('duration_hours', '0').strip()
            duration_minutes = request.form.get('duration_minutes', '0').strip()
            city = request.form.get('city', '').strip()
            venue = request.form.get('venue', '').strip()
            photographer_name = request.form.get('photographer_name', '').strip()
            photographer_role = request.form.get('photographer_role', '').strip()
            videographer_name = request.form.get('videographer_name', '').strip()
            videographer_role = request.form.get('videographer_role', '').strip()
            crew_member_name = request.form.get('crew_member_name', '').strip()
            crew_responsibility = request.form.get('crew_responsibility', '').strip()
            notes = request.form.get('notes', '').strip()

            # If "Other" is selected, use custom_shoot value
            shoot_type = custom_shoot if shoot == "Other" and custom_shoot else shoot

            # ✅ Corrected SQL Query (15 placeholders for 15 values)
            insert_query = """
            INSERT INTO new_shoot (
                project, shoot, date, reporting_time, duration_hours, duration_minutes, city, venue, 
                photographer_name, photographer_role, videographer_name, videographer_role,
                crew_member_name, crew_responsibility, notes
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            
            # ✅ Corrected Values (15 values matching the 15 placeholders)
            values = (
                project, shoot_type, date, reporting_time, duration_hours, duration_minutes, city, venue,
                photographer_name, photographer_role, videographer_name, videographer_role,
                crew_member_name, crew_responsibility, notes
            )

            # Execute Query
            cursor.execute(insert_query, values)
            conn.commit()

            return jsonify({'status': 'success', "message": "Submitted successfully!"})

        except mysql.connector.Error as err:
            print(f"Database Error: {err}")
            return jsonify({'status': 'error', 'message': 'Failed'}), 500

        finally:
            cursor.close()
            conn.close()

    # Render the new_shoot.html template for GET requests
    return render_template('new_shoot.html')


@app.route('/my_work/deliverables')
def deliverables():
    return render_template('deliverables.html')

@app.route('/my_work/deliverables/new_deliverables')
def new_deliverables():
    return render_template('new_deliverables.html')


@app.route('/my_work/task_dashboard')
def task_dashboard():
    return render_template('task_dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
