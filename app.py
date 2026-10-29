from flask import Flask, request, jsonify, render_template, session
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import check_password_hash

load_dotenv()

# Getting the name of the applicaton
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

#creates database connection

def database_connection():
    return mysql.connector.connect(
        host = os.getenv("db_host"),
        user = os.getenv("db_user"),
        password = os.getenv("db_password"),
        database = os.getenv("db_database")
)

#take user to home page
@app.route("/")
def home():
    return render_template("admin_login.html")

#Creates patient record
@app.route("/patients-info", methods=["Post"])
def patients_info():
 
    patient = request.get_json(silent=True)
    
    if not isinstance(patient, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
        
    first_name = patient.get("fname")
    last_name = patient.get("lname")
    age = patient.get("age")
    
    if not isinstance(first_name,str) or not first_name.strip(): 
        return jsonify({
            "message": "Missing first Name"
            }), 400 
    if not isinstance(last_name, str) or not last_name.strip(): 
        return jsonify({
            "message": "Missing last Name"
            }), 400
    if age is None or age == "": 
        return jsonify({
            "message": "Missing age"
            }), 400
    try:
        age = int(age)
    except(TypeError,ValueError):
        return jsonify({
            "message": "Invalid number entered for age"
        }), 400
        
    if age < 0 or age > 105:
        return jsonify({
            "message": "Invalid number enterd for age either to small or to big",
            "age": age
        }), 400
    
    db = database_connection()
    cursor = db.cursor()
    
    sql = """
    INSERT INTO patients(Firstname, Lastname, age)
    VALUES (%s, %s, %s);
    """   
    values = (first_name.strip(), last_name.strip(), age)
    try:
        cursor.execute(sql,values)
        db.commit()
        #gets id for patient that was created
        patient_id = cursor.lastrowid
    finally:
        cursor.close()
        db.close()
    
    return jsonify({
        "message":"Patient info stored",
        "Patient": patient_id
          }), 201
    
@app.route("/admin/login", methods=["POST"])
def admin_login():
    login = request.get_json(silent=True)
        
    if not isinstance(login, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
    
    username = login.get("uname")
    password = login.get("pw")
    
    if not isinstance(username,str) or not isinstance(password,str):
        return jsonify({
            "message": "Username and Password are required"
        }), 400

    username = username.strip()
    if not username or not password:
        return jsonify({
            "message": "Username and Password are required"
        }) , 400
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
        sql = """
            SELECT Username, Hasspassword FROM admin
            WHERE Username = %s
            LIMIT 1         
        """
        cursor.execute(sql, (username,))
        verify_login = cursor.fetchone()
        
        if verify_login is None or not check_password_hash(verify_login[1],password):
            return jsonify({
                "message": "Invalid Username or Password"
            }), 401
            
        
        session.clear()
        session["admin_username"] = verify_login[0]
        
        return jsonify({
            "message": "Login Successful",
            "redirect": "/admin/dashboard"
        }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during admin login")
        return jsonify({
            "message": "Database operation failed"
        }), 500       
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()
@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    
    return jsonify({
        "message": "Sucessful logout"
    }), 200 

#Admin dashboard
@app.route("/admin/dashboard", strict_slashes=False, methods=["GET"])
def admin_dashboard():
    print("DASHBOARD PATH:", request.path)
    print("DASHBOARD URL:", request.url)
    if "admin_username" not in session:
        return jsonify({
            "message": "You are not logged in as an admin"
        }), 401
        
    return render_template(
        "admin_dashboard.html",
        logged_User = session["admin_username"]
    )
    
    
#Displays patient record
@app.route("/admin/retrieve-patients", methods=["GET"])
def patient_display():
    if "admin_username" not in session:
        return jsonify({
            "message": "You are not logged in as an admin"
        }), 401
    db = None
    cursor = None
    try:   
        db = database_connection()
        cursor = db.cursor()

        sql = """
        SELECT * FROM patients
        ORDER BY PatientID DESC
        """
    
        cursor.execute(sql)
        #gets only one row
        patient = cursor.fetchall()    

        return jsonify({
            "Patient": patient
        }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during admin login")
        return jsonify({
            "message": "Database operation failed"
        }), 500 
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()

#Updates patient record
@app.route("/update-patient-records/<int:patient_id>", methods=["PUT"])
def update_patient_records(patient_id):
    info_patient = request.get_json(silent=True)
    
    if not isinstance(info_patient, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
        
    first_name = info_patient.get("fname")
    last_name = info_patient.get("lname")
    age = info_patient.get("age")

    if not isinstance(first_name,str) or not first_name.strip(): 
        return jsonify({
            "message": "Missing first Name"
            }), 400 
    if not isinstance(last_name, str) or not last_name.strip(): 
        return jsonify({
            "message": "Missing last Name"
            }), 400
    if age is None or age == "": 
        return jsonify({
            "message": "Missing age"
            }), 400
    try:
        age = int(age)
    except(TypeError,ValueError):
        return jsonify({
            "message": "Invalid number entered for age"
        }), 400
        
    if age < 0 or age > 105:
        return jsonify({
            "message": "Invalid number enterd for age either to small or to big",
            "age": age
        }), 400
    
    db = database_connection()
    cursor = db.cursor()    
    
    sql = """
        UPDATE patients
        SET Firstname = %s, Lastname = %s, age = %s
        WHERE PatientID = %s
        """
    values = (first_name.strip(), last_name.strip(), age, patient_id)
    
    try:
        cursor.execute(sql, values)
        if cursor.rowcount == 0:
            return jsonify({
                "message": "Patient not found"
            }), 404
            
        db.commit()
    finally:
        cursor.close()
        db.close()
    
    return jsonify({
        "message": "Patient info updated",
        "Patient": patient_id
    }), 200

#Deletes patient record
@app.route("/delete-patient-record/<int:patient_id>", methods=["DELETE"])
def delete_patient_record(patient_id):
    db = database_connection()
    cursor = db.cursor()
    
    sql = """
        DELETE FROM patients
        WHERE PatientID = %s;
    """
    try:
        cursor.execute(sql, (patient_id,))

        if cursor.rowcount == 0:
            return jsonify ({
                "message": "Patient not found"
                }), 400
    
        db.commit()
    finally:
        cursor.close()
        db.close()
    
    return jsonify({
        "message": "Succesfully deleted patient",
        "Patient": patient_id
    }), 200
    
@app.route("/contact")
def contact():
    return("Office Numer")


# Makes it so application and updates when a change is made
if __name__ == "__main__":
    app.run(debug=True)