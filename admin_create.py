from werkzeug.security import generate_password_hash
import mysql.connector
import os
from dotenv import load_dotenv
import getpass

#creates database connection
load_dotenv()
def database_connection():
    return mysql.connector.connect(
        host = os.getenv("db_host"),
        user = os.getenv("db_user"),
        password = os.getenv("db_password"),
        database = os.getenv("db_database")
)
    
def create_admin():
    user_name = input("Enter Username: ").strip()
    
    if not user_name:
        print("Username can't be empty")
        return
    
    password = getpass.getpass("Enter Password: ")
    confirmedPW = getpass.getpass("Verify Password: ")
    
    if len(password) < 12:
        print("Password is not long enough. Must be 12 or more.")
        return
    
    if password != confirmedPW:
        print("Passwords do not match.")
        return
    
    password_hash = generate_password_hash(password)
    db = None
    cursor = None
    try:
        db = database_connection()
        cursor = db.cursor()
        
        sql = """
            SELECT * FROM admin
            WHERE Username = %s;
        """
        
        cursor.execute(sql,(user_name,))
        
        if cursor.fetchone():
            print("User already exists")
            return
        
        sql2 = """
            INSERT INTO admin(Username,Hasspassword)
            VALUES(%s,%s);
        """
        
        cursor.execute(sql2,(user_name,password_hash))
        db.commit()
        print("admin account created")
    except mysql.connector.Error as error:
        if db is not None and db.is_connected():
            db.rollback()
        print("Database operation failed:", error)
        
    finally:
        if cursor is not None:
            cursor.close()

        if db is not None and db.is_connected():
            db.close()
        
if __name__ == "__main__":
    create_admin()
    