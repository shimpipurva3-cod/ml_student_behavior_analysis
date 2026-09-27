from flask import Flask,render_template,request,redirect,url_for,session
import mysql.connector
from model import predict_behavior
app=Flask(__name__)
app.secret_key='student_behavior_secret_key'
def get_db_connection():
    db = mysql.connector.connect(
        host='localhost',
        user='root',
        password='Purva@123',
        database='student_behavior'   
    )
    return db
@app.route('/')
def login():
    return render_template('login.html')
@app.route('/login',methods=['POST'])
def login_user():
    email = request.form['email']
    password = request.form['password']
    db = get_db_connection()
    cursor=db.cursor(dictionary=True)
    query="""
    SELECT * FROM students
    WHERE email =%s AND password=%s
    """
    cursor.execute(query,(email,password))
    student=cursor.fetchone()
    cursor.close()
    db.close()
    if student:
        session['student_id']=student['id']
        session['student_name']=student['full_name']
        return redirect(url_for('dashboard'))
    else:
        return "Invalid Email or password"
#------------------------------------------------------
#Registration
#------------------------------------------------------
def register():
    return render_template('register.html')
@app.route('/register', methods=['GET','POST'])
def register_student():
    if request.method == 'POST':
        full_name=request.form['full_name']
        email=request.form['email']
        department=request.form['department']
        password=request.form['password']
        confirm_password=request.form['confirm_password']
        if password != confirm_password:
            return "Password do not match"
        db = get_db_connection()
        cursor = db.cursor()
        query ="""
            INSERT INTO students
            (full_name, email,department,password)
            VALUES(%s,%s,%s,%s)
        """
        values =(
            full_name, email,department, password
        )
        try:
            cursor.execute(query , values)
            db.commit()
        except mysql.connector.Error as e:
            db.rollback()
            return "This email is already registered!"
        finally:
            cursor.close()
            db.close()
    return render_template('register.html')
#--------------------------------------------------
# Admin Login
#--------------------------------------------------

@app.route('/admin-login', methods=['GET', 'POST'])
def admin_login():

    if request.method == 'POST':

        username = request.form['username']
        password = request.form['password']

        if username == 'admin' and password == 'admin123':

            session['admin_logged_in'] = True

            return redirect(url_for('admin_dashboard'))

        else:

            return render_template(
                'admin_login.html',
                error='Invalid username or password'
            )

    return render_template('admin_login.html')
#--------------------------------------------------
# Admin Dashboard
#--------------------------------------------------

@app.route('/admin-dashboard')
def admin_dashboard():

    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get all students
    cursor.execute("""
        SELECT id, full_name, email, department
        FROM students
        ORDER BY id DESC
    """)

    students = cursor.fetchall()

    # Count students
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM students
    """)

    total_students = cursor.fetchone()['total']

    # Count learning records
    cursor.execute("""
        SELECT COUNT(*) AS total
        FROM learning_data
    """)

    total_learning_data = cursor.fetchone()['total']

    cursor.close()
    db.close()

    return render_template(
        'admin_dashboard.html',
        students=students,
        total_students=total_students,
        total_learning_data=total_learning_data
    )
@app.route('/admin-logout')
def admin_logout():

    session.pop('admin_logged_in', None)

    return redirect(url_for('admin_login'))
# --------------------------------------------------
# Admin - Student Details
# --------------------------------------------------

@app.route('/admin/student/<int:student_id>')
def admin_student_details(student_id):

    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))

    db = get_db_connection()
    cursor = db.cursor(dictionary=True)

    # Get student information
    cursor.execute("""
        SELECT id, full_name, email, department
        FROM students
        WHERE id = %s
    """, (student_id,))

    student = cursor.fetchone()

    if not student:
        cursor.close()
        db.close()
        return "Student not found"

    # Get student's learning records
    cursor.execute("""
        SELECT *
        FROM learning_data
        WHERE student_id = %s
        ORDER BY id DESC
    """, (student_id,))

    learning_data = cursor.fetchall()

    cursor.close()
    db.close()

    return render_template(
        'admin_student_details.html',
        student=student,
        learning_data=learning_data
    )
#---------------------------------------------
#Dashboard
#---------------------------------------------
@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student_id=session['student_id']
    student_name=session['student_name']
    db=get_db_connection()
    cursor=db.cursor(dictionary=True)
    query="""
    SELECT study_hours,sleep_hours,screen_time,
    water_intake,marks,created_at
    FROM learning_data
    WHERE student_id=%s
    ORDER BY created_at DESC
    """
    cursor.execute(query,(student_id,))
    learning_data=cursor.fetchall()
    cursor.close()
    db.close()
    study_hours=0
    learning_sessions=0
    performance=0
    if learning_data:

        # Latest learning record
        latest_data = learning_data[0]

        study_hours = float(latest_data['study_hours'] or 0)

        # Number of learning records
        learning_sessions = len(learning_data)

        # Use marks as performance
        performance = float(latest_data['marks'] or 0)

    return render_template(
        'dashboard.html',
        student_name=student_name,
        learning_data=learning_data,
        study_hours=study_hours,
        learning_sessions=learning_sessions,
        performance=performance
    )
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
#-----------------------------------------------
#Learning Data
#-----------------------------------------------
@app.route('/learning_data', methods=['GET','POST'])
def learning_data():
    if 'student_id' not in session:
        return redirect(url_for('login'))
    if request.method=='POST':
        student_id=session['student_id']
        study_hours=request.form['study_hours']
        sleep_hours=request.form['sleep_hours']
        screen_time=request.form['screen_time']
        water_intake=request.form['water_intake']
        marks=request.form['marks']
        db=get_db_connection()
        cursor=db.cursor()
        query="""
        INSERT INTO learning_data
        (student_id,study_hours,sleep_hours,screen_time,water_intake,marks)
        VALUES(%s,%s,%s,%s,%s,%s)
        """
        values=(
            student_id,study_hours,sleep_hours,screen_time,water_intake,marks)
        cursor.execute(query,values)
        db.commit()
        cursor.close()
        db.close()
        return redirect(url_for('dashboard'))
    return render_template('learning_data.html')
#--------------------------------------------------------------
# AI Learning Analysis
#--------------------------------------------------------------
@app.route('/analyze')
def analyze():
    score=0
    behavior=""
    message=""
    if 'student_id' not in session:
        return redirect(url_for('login'))
    student_id = session['student_id']
    db=get_db_connection()
    cursor=db.cursor(dictionary=True)
    query="""
    SELECT study_hours,sleep_hours,screen_time,water_intake,marks

    FROM learning_data
    WHERE student_id = %s
    ORDER BY created_at DESC
    LIMIT 1
    """
    cursor.execute(query,(student_id,))
    data=cursor.fetchone()
    cursor.close()
    db.close()
    if not data:
        return "Please enter your learning data first."
    study_hours=float(data['study_hours'])
    sleep_hours=float(data['sleep_hours'])
    screen_time=float(data['screen_time'])
    water_intake=float(data['water_intake'])
    marks=float(data['marks'])
    ml_prediction=predict_behavior(
        study_hours,sleep_hours,screen_time,water_intake,marks
    )
    #------------------------------------------------------
    # AI Analysis Score
    #------------------------------------------------------
    score=0
    behavior=""
    message=""
    if study_hours >= 4:
        score += 25
    elif study_hours >= 2:
        score +=15
    else:
        score += 5

    if sleep_hours >= 7:
        score += 20
    elif sleep_hours >= 6:
        score +=10
    else:
        score += 5

    if screen_time >= 3:
        score += 20
    elif screen_time >= 5:
        score +=10
    else:
        score += 5

    if water_intake >= 2:
        score += 10
    elif water_intake >= 1:
        score +=2
    else:
        score += 5

    if marks >= 75:
        score += 25
    elif marks >= 50:
        score +=15
    else:
        score += 5
    if score >= 80:
        behavior ='Excellent'
        message='Your learning habits is very good. Keep maintaining your consistency!'
    elif score >= 60:
        behavior = 'Good'
        message = 'Your learning behavior is good,but there is still room for improvment.'
    elif score >= 40:
        behavior ='Average'
        message='You should improve your study routine and maintain better consistency.'
    else:
        behavior = "Needs Improvement"
        message = 'You should focus on improving your study habits and daily routine.'
    # AI Recommendation
    if study_hours >= 4 and marks >= 75:
        recommendation = "Great work! Your study time and academic performance are strong. Keep following your current routine."

    elif study_hours < 2 and marks < 50:
        recommendation = "Try to increase your study time gradually and maintain a regular study schedule."

    elif screen_time > 5:
        recommendation = "Your screen time is high. Try to reduce unnecessary screen usage and spend more time studying."

    elif sleep_hours < 6:
        recommendation = "Try to maintain a healthy sleep routine because proper rest can help you concentrate better."

    else:
        recommendation = "Your learning habits are fairly good. Keep improving your consistency and study routine." 
    return render_template(
        'analysis.html',
        data=data,
        score=score,
        behavior=behavior,
        message=message,
        ml_prediction=ml_prediction,
        recommendation=recommendation
        )
if __name__ == "__main__":
    app.run(host='0.0.0.0',port=5000,debug=True)