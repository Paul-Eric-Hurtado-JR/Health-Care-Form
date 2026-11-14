from flask import Flask, request, jsonify, render_template, session, redirect
import mysql.connector
import os
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash,check_password_hash
from datetime import datetime
from flask_wtf.csrf import CSRFProtect, generate_csrf

load_dotenv()

# Getting the name of the applicaton
app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY")

if not app.config["SECRET_KEY"]:
    raise RuntimeError("FLASK_SECRET_KEY is missing from .env")

csrf = CSRFProtect(app)
@app.context_processor
def inject_csrf_token():
    return {
        "csrf_token": generate_csrf
    }
    
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
    return render_template("login.html")

@app.route("/patient-registration")
def patient_registration():
    return render_template("patient_registration_form.html")

#Creates patient record // is going to need to be changed for new page so username and passwrod
@app.route("/patients-info", methods=["Post"])
def patients_info():
 
    patient = request.get_json(silent=True)
    
    if not isinstance(patient, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
        
    user_name = patient.get("username")
    pass_word = patient.get("password")
    first_name = patient.get("fname")
    last_name = patient.get("lname")
    age = patient.get("age")
    
    if not isinstance(user_name,str) or not user_name.strip(): 
        return jsonify({
            "message": "Missing username"
        }), 400
    if len(user_name.strip()) > 50:
        return jsonify({
            "message": "Username cannot exceed 50 characters"
        }), 400
    if not isinstance(pass_word,str) or not pass_word: 
        return jsonify({
            "message": "Missing password"
        }), 400
    if len(pass_word) < 12:
        return jsonify({
            "message": "Password must be at least 12 characters"
        }), 400
    if not isinstance(first_name, str) or not first_name.strip(): 
        return jsonify({
            "message": "Missing first name"
        }), 400
    if not isinstance(last_name, str) or not last_name.strip(): 
        return jsonify({
            "message": "Missing last name"
        }), 400
    if isinstance(age, bool) or not isinstance(age,int): 
        return jsonify({
            "message": "Missing age"
        }), 400
    if age < 0 or age > 105:
        return jsonify({
            "message": "Invalid number enterd for age either to small or to big",
            "age": age
        }), 400
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
        sql = """
            SELECT * FROM users
            WHERE Username = %s;
        """
        
        cursor.execute(sql,(user_name,))
        
        if cursor.fetchone():
            return jsonify({
                "message": "Username already exists"
            }), 409
            
        password_hash = generate_password_hash(pass_word)
 
        sql2= """
        INSERT INTO patients(Firstname,Lastname,age)
        VALUES(%s,%s,%s);
        """
        cursor.execute(sql2,(first_name.strip(),last_name.strip(),age))
        patient_id = cursor.lastrowid
        
        sql3 = """
        INSERT INTO users(PatientID,Username, Hasspassword,Userrole)
        VALUES (%s,%s, %s, %s);
        """   
        cursor.execute(sql3,(patient_id,user_name.strip(),password_hash,"patient"))
        
        db.commit()
        
        return jsonify({
            "message":"Account created successfully. Please log in",
            "Patient": patient_id
          }), 201
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during patient registration")
        return jsonify({
            "message": "Database operation failed"
        }), 500        
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()
    
#route to login in user
@app.route("/login", methods=["POST"])
def login():
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
        }), 400
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
        sql = """
            SELECT UserID, PatientID, Username, Hasspassword, Userrole FROM users
            WHERE Username = %s
            LIMIT 1;      
        """
        cursor.execute(sql, (username,))
        verify_login = cursor.fetchone()
        
        if verify_login is None or not check_password_hash(verify_login[3],password):
            return jsonify({
                "message": "Invalid Username or Password"
            }), 401
        
        if verify_login[4] == "patient":
            session.clear()
            session["username"] = verify_login[2]
            session["role"] = verify_login[4]
            session["patientID"] = verify_login[1]
            return jsonify({
                "message": "Login Successful",
                "redirect": "/patient/dashboard"
            }), 200
        if verify_login[4] == "admin":
            session.clear()
            session["username"] = verify_login[2]
            session["role"] = verify_login[4]   
            return jsonify({
                "message": "Login Successful",
                "redirect": "/admin/dashboard"
            }), 200
        return jsonify({
            "message": "Invalid role"
        }), 403
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
            
#route to logout admin
@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    
    return jsonify({
        "message": "Sucessful logout"
    }), 200 

#route to logout patient
@app.route("/patient/logout", methods=["POST"])
def patient_logout():
    session.clear()
    
    return jsonify({
        "message": "Sucessful logout"
    }), 200
    
#Admin dashboard
@app.route("/admin/dashboard", strict_slashes=False, methods=["GET"])
def admin_dashboard():
    if session.get("role") != "admin":
        return jsonify({
            "message": "You are not logged in as an admin"
        }), 401
        
    return render_template(
        "admin_dashboard.html",
        logged_User = session["username"],
        logged_role = session["role"]
    )
    
#Patient dashboard
@app.route("/patient/dashboard", strict_slashes=False, methods=["GET"])
def patient_dashboard():
    if session.get("role") != "patient":
        return jsonify({
            "message": "You are not logged in as patient"
        }), 401
        
    return render_template(
        "patient_dashboard.html",
        logged_User = session["username"],
        logged_role = session["role"],
        logged_patientID = session["patientID"]
    )
    
#Displays patient record
@app.route("/admin/retrieve-patients", methods=["GET"])
def patient_display():
    if session.get("role") != "admin":
        return jsonify({
            "message": "You are not logged in as an admin"
        }), 401
    search = request.args.get("search","").strip()
    db = None
    cursor = None
    try:   
        db = database_connection()
        cursor = db.cursor()
        if search:
            sql = """
             SELECT * FROM patients
             WHERE Firstname LIKE %s OR Lastname LIKE %s
             ORDER BY PatientID DESC;
             """
            search_pattern = f"%{search}%"
            cursor.execute(sql,(search_pattern,search_pattern))
        else:
            sql = """
            SELECT * FROM patients
            ORDER BY PatientID DESC;
            """
            cursor.execute(sql)

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
#gets a single patient record for patient only 
@app.route("/patient/my-record", methods=["GET"])
def patient_my_record():
    if session.get("role") != "patient":
        return jsonify({
            "message": "You are not logged in"
        }), 401
        
    patient_id = session.get("patientID")

    if patient_id is None:
        return jsonify({
            "message": "Patient ID not found in session"
        }), 401
    
    db = None
    cursor = None
    try:   
        db = database_connection()
        cursor = db.cursor(dictionary=True)
            
        sql="""
            SELECT PatientID, Firstname, Lastname, age FROM patients
            WHERE PatientID = %s;
            """
        cursor.execute(sql,(patient_id,))
            
        patient = cursor.fetchone() 
               
        if patient is None:
            return jsonify({
                "message": "Patient not found"
            }), 404
                
        return jsonify({
            "Patient": patient
        }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during patient retrieving")
        return jsonify({
            "message": "Database operation failed"
        }), 500 
    finally:
        if cursor is not None:
            cursor.close()
    
        if db is not None and db.is_connected():
            db.close()
#update for patient           
@app.route("/patient/update-my-record", methods=["PUT"])
def patient_update_my_record():
    if session.get("role") != "patient":
        return jsonify({
            "message": "You are not authorized to update patient records"
        }), 401
        
    info_patient = request.get_json(silent=True)
    
    if not isinstance(info_patient, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
        
    first_name = info_patient.get("fname")
    last_name = info_patient.get("lname")
    age = info_patient.get("age")
    patient_id = session.get("patientID")
    
    if patient_id is None:
        return jsonify({
            "message": "Patient ID not found in session"
         }), 401
    
    if not isinstance(first_name,str) or not first_name.strip(): 
        return jsonify({
            "message": "Missing first Name"
            }), 400 
    if not isinstance(last_name, str) or not last_name.strip(): 
        return jsonify({
            "message": "Missing last Name"
            }), 400
    if isinstance(age, bool) or not isinstance(age, int):
        return jsonify({
            "message": "Age must be a whole number"
        }), 400

    if age < 0 or age > 105:
        return jsonify({
            "message": "Age must be between 0 and 105"
        }), 400
        
    db = None
    cursor = None
    try:    
        db = database_connection()
        cursor = db.cursor()
        
        sql1 = """
         SELECT PatientID FROM patients
         WHERE PatientID = %s;
        """
        cursor.execute(sql1,(patient_id,))
        if cursor.fetchone() is None:
            return jsonify({
                "message": "Patient not found"
            }), 404
            
        sql2 = """
            UPDATE patients
            SET Firstname = %s, Lastname = %s, age = %s
            WHERE PatientID = %s
            """        
            
        cursor.execute(sql2, (first_name.strip(), last_name.strip(), age, patient_id))

        db.commit() 
           
        return jsonify({
        "message": "Patient info updated",
        "Patient": patient_id
    }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during updating information")
        return jsonify({
            "message": "Database operation failed"
        }), 500 
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()
            
#gets one record for patient admin only
@app.route("/retrieve-single-record/<int:patient_id>", methods=["GET"])
def retrieve_single_record(patient_id):
    if session.get("role") != "admin":
        return jsonify({
            "message": "You are not logged in"
        }), 401
        
    db = None
    cursor = None
    try:   
        db = database_connection()
        cursor = db.cursor(dictionary=True)
        
        sql="""
        SELECT PatientID, Firstname, Lastname, age FROM patients
        WHERE PatientID = %s;
        """
        cursor.execute(sql,(patient_id,))
        
        patient = cursor.fetchone() 
           
        if patient is None:
            return jsonify({
                "message": "Patient not found"
            }), 404
            
        return jsonify({
            "Patient": patient
        }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during during patient retrieving")
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
    if session.get("role") != "admin":
        return jsonify({
            "message": "You are not authorized to update patient records"
        }), 401
        
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
    db = None
    cursor = None
    try:    
        db = database_connection()
        cursor = db.cursor()    
        
        sql = """
            UPDATE patients
            SET Firstname = %s, Lastname = %s, age = %s
            WHERE PatientID = %s
            """
        values = (first_name.strip(), last_name.strip(), age, patient_id)

        cursor.execute(sql, values)
        if cursor.rowcount == 0:
            return jsonify({
                "message": "Patient not found"
            }), 404
                
        db.commit() 
           
        return jsonify({
        "message": "Patient info updated",
        "Patient": patient_id
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
    

    
@app.route("/update-admin-patient-page/<int:patient_id>", methods=["GET"])
def admin_update_patient_page(patient_id):
    if session.get("role") != "admin":
        return redirect("/")
    return render_template("admin_patient_update.html", patient_id = patient_id)

@app.route("/update-patient-page", methods=["GET"])
def patient_update_patient_page():
    if session.get("role") != "patient" or session.get("patientID") is None:
        return redirect("/")
    return render_template("patient_update.html", patient_id = session.get("patientID"))

#Deletes patient record
@app.route("/delete-patient-record/<int:patient_id>", methods=["DELETE"])
def delete_patient_record(patient_id):
    if session.get("role") != "admin":
        return jsonify({
            "message": "You are not logged in as an admin"
        }), 401
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
               
        sql = """
            DELETE FROM patients
            WHERE PatientID = %s;
        """
        cursor.execute(sql, (patient_id,))

        if cursor.rowcount == 0:
            db.rollback()
            return jsonify ({
                "message": "Patient not found"
                }), 404
        
        db.commit()
        return jsonify({
            "message": "Patient succesfully deleted",
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

@app.route("/patient/food-log", methods=["POST"])
def patient_food_log():
    if session.get("role") != "patient":
        return jsonify({
            "message": "You are not authorized to log food"
        }), 401
    food_log = request.get_json(silent=True)
    
    if not isinstance(food_log, dict):
        return jsonify({
            "message": "Request must be a json object"
        }), 400
    
    patient_id = session.get("patientID")
    food_name = food_log.get("foodName")
    meal_type = food_log.get("mealType")
    portion_size = food_log.get("portionSize")
    notes = food_log.get("notes")
    log_date = food_log.get("logDate")
    
    if patient_id is None:
        return jsonify({
            "message": "Patient ID not found in session"
        }), 401
    #food validation
    if not isinstance(food_name,str) or not food_name.strip(): 
         return jsonify({
            "message": "Missing food Name"
        }), 400
    food_name = food_name.strip()
    
    if len(food_name) > 100:
        return jsonify({
            "message": "Meal name cannot exceed 100 characters"
         }), 400

    if not any(character.isalpha() for character in food_name):
        return jsonify({
            "message": "Meal name must contain at least one letter"
        }), 400
        
    #meal type validation
    if not isinstance(meal_type,str) or not meal_type.strip(): 
        return jsonify({
            "message": "Missing food type"
        }), 400
    else:
        meal_type = meal_type.strip()
        
    valid_meal_types = ["Breakfast", "Lunch", "Dinner", "Snack"]
    if meal_type not in valid_meal_types:
        return jsonify({
            "message": "Invalid meal type"
        }), 400
        
    #portion size validation
    if not isinstance(portion_size,str) or not portion_size.strip(): 
        return jsonify({
            "message": "Missing portion size"
        }), 400
    portion_size = portion_size.strip()

    if len(portion_size) > 50:
        return jsonify({
            "message": "Serving size cannot exceed 50 characters"
        }), 400

    if not any(character.isalpha() for character in portion_size):
        return jsonify({
            "message": "Serving size must include a unit or description"
        }), 400

    #note validation
    if notes is None:
        notes = ""
    elif not isinstance(notes, str):
        return jsonify({
            "message": "Invalid notes"
        }), 400
    notes = notes.strip()
    
    if len(notes) > 500:
        return jsonify({
            "message": "Note  cannot exceed 500 characters"
         }), 400
    #date validation
    if not isinstance(log_date, str) or not log_date.strip():
        return jsonify({
            "message": "Invalid log date. Use YYYY-MM-DD"
        }), 400
    log_date = log_date.strip()
    try:
        parsed_date = datetime.strptime(log_date, "%Y-%m-%d").date()
    except ValueError:
        return jsonify({
            "message": "Invalid log date. Use YYYY-MM-DD"
        }), 400

    today = datetime.now().date()

    if parsed_date > today:
        return jsonify({
            "message": "Meal date cannot be in the future"
        }), 400
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
        
        sql = """
            INSERT INTO food_logs(PatientID,Foodname,Mealtype,Portionsize,Notes,LogDate)
            VALUES(%s,%s,%s,%s,%s,%s);
        """
        
        cursor.execute(sql,(patient_id,food_name,meal_type,portion_size,notes,log_date))
        
        db.commit()
        return jsonify({
            "message": "Meal successfully logged",
        }), 200
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        app.logger.exception("Database error during food logging")
        return jsonify({
            "message": "Database operation failed"
        }), 500 
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()
@app.route("/patient/log-food-page")
def patient_log_food_page():
    if session.get("role") != "patient":
        return redirect("/")
    return render_template("patient_log_food.html")

@app.route("/patient/get-food", methods=["GET"])
def patient_get_food():
    if session.get("role") != "patient":
        return jsonify({
            "message": "You are not authorized to view food logs"
        }), 401
        
    patient_id = session.get("patientID")
    if patient_id is None:
        return jsonify({
            "message": "Patient ID not found in session"
        }), 401
        
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor(dictionary=True)
        
        sql= """
            SELECT Foodname, Mealtype, Portionsize, Notes, DATE_FORMAT(LogDate, '%Y-%m-%d') AS LogDate FROM food_logs
            WHERE PatientID = %s
            ORDER BY LogDate ASC;
        """
        cursor.execute(sql,(patient_id,))
        
        meals = cursor.fetchall()    

        return jsonify({
            "meals": meals
        }), 200
    except mysql.connector.Error as error:
        app.logger.exception("Database error during food log retrival")
        return jsonify({
            "message": "Database operation failed"
        }), 500 
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()

@app.route("/contact")
def contact():
    return("Office Numer")


# Makes it so application and updates when a change is made
if __name__ == "__main__":
    app.run(debug=True)