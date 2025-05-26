from flask import Flask, render_template, request, redirect, session, url_for
from waitress import serve  # Import waitress

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Use environment variables in production

# Hardcoded credentials
USERNAME = "admin"
PASSWORD = "1234"

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == USERNAME and request.form['password'] == PASSWORD:
            session['user'] = USERNAME
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    print("Starting server with Waitress...")
    serve(app, host='0.0.0.0', port=9000)
