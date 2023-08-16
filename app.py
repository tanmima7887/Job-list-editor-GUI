from flask import Flask, render_template, request, redirect, session, url_for, flash
from flask_bcrypt import Bcrypt
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

# replace this with your own credentials
users = {
    'admin': {
        'password': bcrypt.generate_password_hash('admin').decode('utf-8')
    },
    'Tanmim': {
        'password': bcrypt.generate_password_hash('password').decode('utf-8')
    }
}

class User(UserMixin):      # Allow multiple user to use
    pass

@login_manager.user_loader
def load_user(user_id):
    user = User()
    user.id = user_id
    return user

@login_manager.unauthorized_handler
def unauthorized():
    return redirect(url_for('login'))

def read_jobs_from_file(file_path):
    try:
        with open(file_path, 'r') as file:
            jobs = file.read().splitlines()
        return jobs
    except FileNotFoundError:
        print("Invalid path: The file does not exist.")
        return None

def write_jobs_to_file(file_path, jobs):
    with open(file_path, 'w') as file:
        file.write('\n'.join(jobs))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('job_list_editor'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username in users and bcrypt.check_password_hash(users[username]['password'], password):
            user = User()
            user.id = username
            login_user(user)
            return redirect(url_for('job_list_editor'))
        else:
            flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/job-list-editor', methods=['GET', 'POST']) # redirect to job-list-editor page if the loging page successfull. 
@login_required
def job_list_editor():
    jobs_file_path = session.get('file_path', '')
    jobs = []
    if jobs_file_path:
        jobs = read_jobs_from_file(jobs_file_path)
    return render_template('index.html', jobs_file_path=jobs_file_path, jobs=jobs)


@app.route('/')
@login_required
def index():
    jobs_file_path = session.get('file_path', '')
    jobs = []
    if jobs_file_path:
        jobs = read_jobs_from_file(jobs_file_path)
    return render_template('index.html', is_authenticated=current_user.is_authenticated, jobs_file_path=jobs_file_path, jobs=jobs)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.pop('file_path', None)
    return redirect('/login')

@app.route('/', methods=['POST'])
@login_required
def handle_job_list():
    file_path = request.form['jobs_file_path']
    session['file_path'] = file_path
    return redirect('/')
    
@login_manager.request_loader
def load_user_from_request(request):
    username = request.form.get('username')
    password = request.form.get('password')
    if username in users and bcrypt.check_password_hash(users[username]['password'], password):
        user = User()
        user.id = username
        login_user(user)
        return user

    return None
@app.route('/add', methods=['POST'])
@login_required
def add_job():
    new_job = request.form['new_job']

    if 'file_path' in session:
        file_path = session['file_path']
        jobs = read_jobs_from_file(file_path)
        jobs.append(new_job)
        write_jobs_to_file(file_path, jobs)

    return redirect('/')

@app.route('/update', methods=['POST'])
@login_required
def update_job():
    old_job = request.form['old_job']
    updated_job = request.form['updated_job']

    if 'file_path' in session:
        file_path = session['file_path']
        jobs = read_jobs_from_file(file_path)
        if old_job in jobs:
            index = jobs.index(old_job)
            jobs[index] = updated_job
            write_jobs_to_file(file_path, jobs)

    return redirect('/')

@app.route('/delete', methods=['POST'])
@login_required
def delete_job():
    deleted_job = request.form['deleted_job']

    if 'file_path' in session:
        file_path = session['file_path']
        jobs = read_jobs_from_file(file_path)
        if deleted_job in jobs:
            jobs.remove(deleted_job)
            write_jobs_to_file(file_path, jobs)

    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
# recommend to use edge browser, also if the there's any error, make sure to clear the all time cache memeory. 