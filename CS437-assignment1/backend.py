from flask import Flask, render_template, redirect, url_for, flash, session, send_file
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_mail import Mail, Message
from PIL import Image, ImageDraw, ImageFont
import io
import random
from pymongo import MongoClient
from pymongo.server_api import ServerApi

app = Flask(__name__)


app.config['SECRET_KEY'] = 'helloworld'

# Flask-Mail configuration for Gmail
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
app.config['MAIL_USERNAME'] = 'turkish_news@gmail.com'  
app.config['MAIL_PASSWORD'] = 'turkishnews1234'  
app.config['MAIL_DEFAULT_SENDER'] = 'turkish_news@gmail.com' 
mail = Mail(app)

# MongoDB configuration
mongo_uri = "mongodb+srv://alpcivan858:c27nCi1qs38eEre0@cluster0.6ofoijn.mongodb.net/?retryWrites=true&w=majority"
client = MongoClient(mongo_uri, server_api=ServerApi('1'))
db = client.your_database  # Replace "your_database" with your actual database name
users_collection = db.users

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(e)


# Data set for user information (to login use any username and password)
# Now data is fetched from MongoDB
users = list(users_collection.find())

# Data set for user information (to login use any username and password)
users = [
    {'username': 'user1', 'email': 'user1@example.com', 'password': 'password1'},
    {'username': 'user2', 'email': 'user2@example.com', 'password': 'password2'},
    {'username': 'user3', 'email': 'user3@example.com', 'password': 'password3'}
]

# Data set with admin information (to login use username and password)
admin = {'username': 'admin','email':'admin@exampl.ecom', 'password': 'adminpassword'}

# class for user login
class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Login')

# class for admin login
class AdminLoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    captcha = StringField('Captcha', validators=[DataRequired()])
    submit = SubmitField('Login')

# class to send email for forget password
class ForgetPasswordEmailForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Continue')

# class to enter the code sent by email to forget password
class ForgetPasswordCodeForm(FlaskForm):
    code = StringField('Code', validators=[DataRequired(), Length(min=6, max=6)])
    submit = SubmitField('Verify Code')

# CAPTCHA CREATION (static 4-digit number for user, changing image-based for admin)

@app.route('/captcha')
def serve_captcha():
    image_io = generate_captcha_image()
    return send_file(image_io, mimetype='image/png')

def generate_captcha_image():
    # Use a static 4-digit number as CAPTCHA text
    captcha_text = "5395"

    # Save the CAPTCHA text in the session
    session['captcha'] = captcha_text

    # Generate an image with the CAPTCHA text
    image = Image.new('RGB', (120, 40), color='white')
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 10), captcha_text, font=font, fill='black')

    # Save the image to a BytesIO object
    image_io = io.BytesIO()
    image.save(image_io, 'PNG')
    image_io.seek(0)

    return image_io

# FORGET PASSWORD (5 mins expiration duration, sent by email)

# function to generate a reset code
def generate_reset_code():
    return str(random.randint(100000, 999999))

# function to send a message to email
def send_reset_code_email(email, code):
    subject = 'Password Reset Code'
    body = f'Your password reset code is: {code}. Enter this code to reset your password.'
    message = Message(subject, recipients=[email], body=body)
    mail.send(message)

@app.route('/forget_password_email', methods=['GET', 'POST'])
def forget_password_email():
    form = ForgetPasswordEmailForm()

    if form.validate_on_submit():
        email = form.email.data
        # Check if the email exists in the dataset
        if any(user['email'] == email for user in users):
            session['reset_email'] = email
            reset_code = generate_reset_code()
            session['reset_code'] = reset_code
            send_reset_code_email(email, reset_code)
            return redirect(url_for('forget_password_code'))

        else:
            flash('Email not found. Please enter a registered email address.', 'danger')

    return render_template('forget_password_email.html', form=form)

@app.route('/forget_password_code', methods=['GET', 'POST'])
def forget_password_code():
    form = ForgetPasswordCodeForm()

    if 'reset_email' not in session or 'reset_code' not in session:
        flash('Invalid request. Please start the password reset process again.', 'danger')
        return redirect(url_for('login'))

    if form.validate_on_submit():
        entered_code = form.code.data
        if entered_code == session['reset_code']:
            # Code is valid, allow the user to reset the password
            flash('Code verified. You can now reset your password.', 'success')
            # You can redirect the user to the password reset page here
            # For simplicity, let's redirect back to the login page
            return redirect(url_for('login'))

        else:
            flash('Invalid code. Please enter the correct code.', 'danger')

    return render_template('forget_password_code.html', form=form)

# LOGIN FOR USER

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check the CAPTCHA
        if form.captcha.data != session['captcha']:
            flash('CAPTCHA is incorrect.', 'danger')
            return redirect(url_for('login'))

        # Check if user is in users list
        user = next((u for u in users if u['username'] == username), None)

        if user and user['password'] == password:
            flash('Login successful!', 'success')
            return redirect(url_for('home'))

        else:
            flash('Login unsuccessful. Check username and password.', 'danger')

    # CAPTCHA for each login attempt
    generate_captcha_image()

    return render_template('login.html', form=form)

# LOGIN FOR ADMIN

@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    form = AdminLoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        # Check the CAPTCHA
        if form.captcha.data != session['captcha']:
            flash('CAPTCHA is incorrect.', 'danger')
            return redirect(url_for('admin_login'))

        if username == admin['username'] and password == admin['password']:
            flash('Admin Login successful!', 'success')
            return redirect(url_for('home'))

        else:
            flash('Admin Login unsuccessful. Check username and password.', 'danger')

    # Generate a new CAPTCHA for each login attempt
    generate_captcha_image()

    return render_template('admin_login.html', form=form)

# RENDERING HTML PAGES (home page for now)

# Home page
@app.route('/home')
def home():
    return render_template('home_page.html')

# When we choose admin or user login in home_page.html
@app.route('/choose_login/<role>', methods=['GET'])
def choose_login(role):
    if role == 'user':
        return redirect(url_for('login'))  # redirecting to login function
    elif role == 'admin':
        return redirect(url_for('admin_login'))  # redirecting to admin login function
    else:
        return redirect(url_for('home'))
    


if __name__ == '__main__':
    app.run(debug=True, port=3000)  # Set the port to 3000
