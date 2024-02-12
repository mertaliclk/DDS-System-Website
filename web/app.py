from flask import Flask, request, render_template, session, redirect, url_for, send_file, flash
import sqlite3
import hashlib
import random
import datetime
from flask_mail import Mail, Message
from captcha.image import ImageCaptcha
import io
import string, feedparser, logging
from logging.handlers import RotatingFileHandler

app = Flask(__name__)
app.secret_key = 'a_random_secret_key'  # Replace with a strong secret key in production
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587  # or 465 for SSL
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'mertaliclk13@gmail.com'
app.config['MAIL_PASSWORD'] = 'ndyrcqvbiuvjjaro'
app.config['MAIL_DEFAULT_SENDER'] = 'mertaliclk13@gmail.com'

mail = Mail(app)

logger = logging.getLogger('honeypot_logger')
logger.setLevel(logging.INFO)
handler = RotatingFileHandler('honeypot.log', maxBytes=10000000, backupCount=5)
logger.addHandler(handler)

reset_codes = {}
comments = {}  # In-memory storage for comments

def log_request(req_type, endpoint, status, remote_addr, user_agent):
    # Classify the attempt type based on the endpoint and status
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    attempt_type = "Normal Request"
    if endpoint == "/verify_reset_code" and "Invalid reset code." in status:
        attempt_type = "Password Reset Abuse"
    elif endpoint == "/login" and "Failed" in status:
        attempt_type = "Login Attempt"
    elif endpoint == "/verify_mfa" and "Failed" in status:
        attempt_type = "MFA Verification Abuse"

    # Log the detailed request information without email
    logger.info(f"Time: {current_time}, RequestType: {req_type}, Endpoint: {endpoint}, Status: {status}, "
                f"IP: {remote_addr}, UserAgent: {user_agent}, "
                f"AttemptType: {attempt_type}")

@app.route('/captcha')
def captcha():
    image = ImageCaptcha(width=280, height=90)
    # Generate a random alphanumeric string for captcha_text
    characters = string.ascii_letters + string.digits
    captcha_text = ''.join(random.choice(characters) for i in range(6))  # e.g., "x5ash21"
    data = image.generate(captcha_text)
    session['captcha_answer'] = captcha_text.lower()  # Store lowercase version for case-insensitive comparison
    return send_file(io.BytesIO(data.read()), mimetype='image/png')

def hash_password(password):
    return hashlib.sha256(password.encode('utf-8')).hexdigest()

def send_reset_email(email, reset_code):
    try:
        msg = Message('Password Reset Code', sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
        msg.body = f'Your password reset code is: {reset_code}\nThis code will expire in 2 minutes.'
        mail.send(msg)
    except Exception as e:
        app.logger.error(f"Failed to send reset email: {e}")
        
@app.route('/')
def home():
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    # Fetch news items from the news table
    cursor.execute("SELECT * FROM news")
    news_items = cursor.fetchall()  # This will contain all news items

    # Dictionary to hold comments for each news item, including the comment id
    news_comments = {}
    for item in news_items:
        news_id = item[0]  # Assuming the first column in the news table is the id
        cursor.execute("""
            SELECT id, email, comment_text
            FROM comments
            WHERE news_id = ?
            """, (news_id,))
        comments = cursor.fetchall()
        news_comments[news_id] = comments

    conn.close()
    return render_template('dashboard.html', news_items=news_items, news_comments=news_comments)

@app.route('/comment', methods=['POST'])
def post_comment():
    print("Session data:", session)

    if 'email' not in session:
        return redirect(url_for('login'))  # Redirect to login if the user is not logged in

    email = session['email']
    news_id = request.form.get('news_id')
    user_comment = request.form.get('comment')

    # Connect to the database and insert the comment
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO comments (news_id, email, comment_text) VALUES (?, ?, ?)", 
                   (news_id, email, user_comment))
    conn.commit()
    conn.close()

    return redirect(url_for('home'))

@app.route('/forgot_password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        # Generate a 2-digit reset code
        reset_code = str(random.randint(10, 99))
        reset_codes[email] = {'code': reset_code, 'expires': datetime.datetime.now() + datetime.timedelta(minutes=2)}
        send_reset_email(email, reset_code)

        # Redirect to the verify_reset_code page after sending the reset code
        return redirect(url_for('verify_reset_code'))
    else:
        return render_template('forgot_password.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    num1 = random.randint(1, 10)
    num2 = random.randint(1, 10)
    operation = random.choice(['+', '-', '*'])
    captcha_question = f"{num1} {operation} {num2}"
    correct_answer = str(eval(captcha_question))


    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        captcha_response = request.form.get('captcha', '')

        # Log the login attempt
        # Inside the verify_reset_code function
        log_request(req_type="POST",
            endpoint="/login",
            status="Attempt",
            remote_addr=request.remote_addr,
            user_agent=request.user_agent.string)

        
        if captcha_response != session.get('captcha_answer', ''):
            message = 'Incorrect CAPTCHA.'
        else:
            hashed_password = hash_password(password)
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ? AND password = ?", (email, hashed_password))
            result = cursor.fetchone()
            conn.close()

            if result:
                session['email'] = email
                return redirect(url_for('home'))
            else:
                message = 'Failed to log in!'

    session['captcha_answer'] = correct_answer

    return render_template('user_login.html', message=message, captcha_question=captcha_question)
'''
@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    message = ''
    status = "Attempt"
    if request.method == 'POST':
        admin_email = request.form['admin_email']
        admin_password = request.form['admin_password']
        captcha_response = request.form['captcha_response']	

        if captcha_response != session.get('captcha_answer', ''):
            message = 'Incorrect CAPTCHA.'
            status = "Failed - Incorrect CAPTCHA"  # Update status for logging
        else:
            hashed_password = hash_password(admin_password)
            
            # Verify if the email and password are correct and if the user is an admin
            conn = sqlite3.connect('database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM admins WHERE email = ? AND password = ?", (admin_email, hashed_password))
            admin = cursor.fetchone()
            conn.close()

            if admin:
                # Generate a random 6-digit MFA code
                mfa_code = '{:06d}'.format(random.randint(0, 999999))
                # Save the MFA code and expiration in the session
                session['mfa_code'] = mfa_code
                session['mfa_code_expires'] = (datetime.datetime.now() + datetime.timedelta(minutes=2)).strftime("%Y-%m-%d %H:%M:%S")
                session['mfa_attempts'] = 0
            else: 
                message = 'Invalid email or password.'
                status = 'Failed - Invalid Credentials'
            
        log_request(req_type="POST", endpoint="/admin_login", status=status, remote_addr=request.remote_addr, user_agent=request.user_agent.string)
    return render_template('admin_login.html', message=message)
'''

@app.route('/logout', methods=['POST'])
def logout():
    # Remove user information from the session
    session.clear()

    # Redirect to the homepage or login page
    return redirect(url_for('home'))

@app.route('/verify_reset_code', methods=['GET', 'POST'])
def verify_reset_code():
    message = None  # Initialize message
    if request.method == 'POST':
        email = request.form.get('email')
        user_code = request.form.get('reset_code')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')

        if email and user_code:
            if email in reset_codes and reset_codes[email]['expires'] > datetime.datetime.now():
                if reset_codes[email]['code'] == user_code:
                    if new_password == confirm_password:
                        # Passwords match, proceed with resetting password
                        conn = sqlite3.connect('database.db')
                        cursor = conn.cursor()
                        hashed_password = hash_password(new_password)
                        cursor.execute("UPDATE users SET password = ? WHERE email = ?", (hashed_password, email))
                        conn.commit()
                        conn.close()

                        # Set the user as logged in
                        session['email'] = email

                        # Redirect to the dashboard
                        flash('Password reset successful. You are now logged in.')
                        return redirect(url_for('home'))

                    else:
                        message = 'Passwords do not match.'
                else:
                    message = 'Invalid reset code.'
            else:
                message = 'Reset code has expired or does not exist.'
        else:
            message = 'Email or reset code is missing.'

    return render_template('verify_reset_code.html', message=message)


@app.route('/report', methods=['GET', 'POST'])
def report():
    # Check if the user is logged in as a normal user or an admin
    if 'email' not in session:
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        # Handle report submission
        report_content = request.form.get('report_content')

        flash('Your report has been submitted successfully.')
        return redirect(url_for('home'))

    return render_template('report.html')

@app.route('/video', methods=['GET', 'POST'])
def video():
    # Check if the user is logged in as a normal user or an admin
    if 'email' not in session:
        flash('You must be logged in to access this page.')
        return redirect(url_for('login'))

    return render_template('video.html')

@app.route('/ecg_results', methods=['GET', 'POST'])
def ecg_results():
    return render_template('ecg_results.html')

@app. route('/ecg_plot.html', methods=['GET'])
def chart1():
    return render_template('ecg_plot.html')

@app.route('/model_reconstruction_MAE_example_1.html')
def chart2(): 
    return render_template('model_reconstruction_MAE_example_1.html')

@app.route('/model_reconstruction_CosineSimilarity_example_3.html')
def chart3():
    return render_template('model_reconstruction_CosineSimilarity_example_3.html')

@app.route('/model_reconstruction_Huber_example_1.html')
def chart():
    return render_template('model_reconstruction_Huber_example_1.html')

@app.route('/Results_of_Data.html')
def chart4():
    return render_template('Results_of_Data.html')

@app.route('/reconstructions_CosineSimilarity.html')
def chart5():
    return render_template('reconstructions_CosineSimilarity.html')

@app.route('/reconstructions_Huber.html')
def chart6():
    return render_template('reconstructions_Huber.html')

@app.route('/reconstructions_MAE.html')
def chart7():
    return render_template('reconstructions_MAE.html')

@app.route('/reconstructions_MSE.html')
def chart8():
    return render_template('reconstructions_MSE.html')

@app.route('/reconstructions_CosineSimilarity.html')
def chart9():
    return render_template('reconstructions_CosineSimilarity.html')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')