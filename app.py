from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Users, Books, Availablebooks, Members, Issuedbooks
from flask_bcrypt import Bcrypt
from werkzeug.utils import secure_filename
import os
import re
import webbrowser

app = Flask(__name__)
bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'akarshit294'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:#AKroot294@localhost/library-system'

SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = True

db.init_app(app)

with app.app_context():
    db.create_all()

app.config['UPLOAD_FOLDER'] = 'static/images'

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS 

@app.route('/')
def cover_page():
    return render_template('cover.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'password' in request.form and 'email' in request.form:
        fullname = request.form['name']
        password = request.form['password']
        email = request.form['email']

        user_exists = Users.query.filter_by(email=email).first() is not None
        if user_exists:
            message = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not fullname or not password or not email:
            message = 'Please fill out the form!'
        else:
            hashed_password = bcrypt.generate_password_hash(password)
            new_user = Users(name=fullname, email=email, password=hashed_password)
            db.session.add(new_user)
            db.session.commit()
            message = 'You Have Successfully Registered!'
            return redirect(url_for('dashboard'))


    elif request.method == 'POST':
        message = 'Please fill out the form!'
    return render_template('register.html', message = message)

@app.route('/login', methods=['GET', 'POST'])
def login():
    message = ''
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        if email == '' or password == '':
            message = 'Please enter email and password!'
        else:
            user = Users.query.filter_by(email=email).first()
            print(user)
            if user is None:
                message = 'Please enter correct email / password!'
            else:
                if not bcrypt.check_password_hash(user.password, password):
                    message = 'Please enter correct email and password!'
                else:
                    session['loggedin'] = True
                    session['userid'] = user.id
                    session['name'] = user.name
                    session['email'] = user.email
                    message = 'Login successful!'
                    return redirect(url_for('dashboard'))
            
    return render_template('login.html', message = message)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'loggedin' in session:
        total_books = Books.query.count()
        available_books = Availablebooks.query.count()
        if total_books == 0:
            total_available_books = 0.0
        else:
            total_available_books = round((available_books * 100)/ total_books, 2)
        total_issued_books = Issuedbooks.query.count()
        total_members = Members.query.count()
        return render_template(
            'dashboard.html',
            total_books=total_books,
            total_available_books=total_available_books,
            total_issued_books=total_issued_books,
            total_members=total_members)
    else:
        return redirect(url_for('login'))
    
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('userid', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/books', methods=['GET', 'POST'])
def books():
    if 'loggedin' in session:
        books = Books.query.all()
        return render_template('books.html', books = books)
    else:
        return redirect(url_for('login'))
    
@app.route('/save_book', methods=['POST'])
def save_book():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            isbn = request.form['isbn']
            action = request.form['action']

            if action == 'updateBook':
                bookid = request.form['bookid']
                book = Books.query.get(bookid)
                book.name = name
                book.isbn = isbn
                db.session.commit()
                print("UPDATE book")
            else:
                file = request.files.get('uploadFile')  # safe access
                filenameimage = None

                if file and file.filename != '' and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    filenameimage = filename
                elif file and file.filename != '':
                    msg = 'File not allowed! Please upload a valid image file.'
                    return render_template('books.html', msg=msg)

                # Proceed with inserting even if filenameimage is None
                book = Books(name=name, picture=filenameimage, isbn=isbn)
                db.session.add(book)
                db.session.commit()
                book_available = Availablebooks(bookid=book.bookid,name=name, picture=filenameimage, isbn=isbn)
                db.session.add(book_available)
                db.session.commit()
                print("INSERT INTO book")
            return redirect(url_for('books'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template('books.html', msg=msg)
    return redirect(url_for('login'))

@app.route("/edit_book", methods=['GET', 'POST'])
def edit_book():
    msg = ''
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        books = Books.query.get(bookid)
        # print(books.bookid)
        return render_template('edit_books.html', books = books)
    return redirect(url_for('login'))

@app.route("/delete_book", methods=['GET'])
def delete_book():
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        print(bookid)
        book = Books.query.get(bookid)
        db.session.delete(book)
        db.session.commit()
        # os.unlink(os.path.join(app.config['UPLOAD_FOLDER'], book.picture))
        picture_path = book.picture

        if picture_path and picture_path != "default.webp":
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], picture_path)
            if os.path.exists(file_path):
                os.unlink(file_path)

        return redirect(url_for('books'))
    return redirect(url_for('login'))

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/total_books')
def total():
    books = Books.query.all()
    return render_template('total.html', books=books)

@app.route('/available_books', methods=['GET', 'POST'])
def available():
    if 'loggedin' in session:
        books = Availablebooks.query.all()
        return render_template('available.html', books = books)
    else:
        return redirect(url_for('login'))
    
@app.route("/issue_book", methods=['GET', 'POST'])
def issue_book():
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        books = Availablebooks.query.get(bookid)
        # print(books.bookid)

        message = ''
        if request.method == 'POST':
            name = request.form['member name']
            id = request.form['member id']
            date = request.form['date']
            bookid = request.form['bookid']

            if name == '' or id == '':
                message = 'Please enter both name and id!'
            else:
                member = Members.query.filter_by(name=name, id=id).first()
                print(member)
                if member is None:
                    message = 'Please enter correct name / id!'
                else:
                    message = 'Book Issued!'
                    books = Availablebooks.query.get(bookid)
                    book_name = books.name
                    isbn = books.isbn
                    picture = books.picture
                    issued_book = Issuedbooks(bookid=bookid, name=book_name, isbn=isbn, member_id=id, member_name=name, return_date=date, picture=picture)
                    db.session.delete(books)
                    db.session.add(issued_book)
                    db.session.commit()
                    # return redirect(url_for('available'))

        return render_template('issue_books.html', books = books, message = message)
    return redirect(url_for('login'))

@app.route('/members', methods=['GET', 'POST'])
def members():
    if 'loggedin' in session:
        members = Members.query.all()
        return render_template('members.html', members = members)
    else:
        return redirect(url_for('login'))
    
@app.route('/add_member', methods=['POST'])
def add_member():
    message = ''
    if request.method == 'POST' and 'name' in request.form and 'email' in request.form:
        fullname = request.form['name']
        email = request.form['email']

        member_exists = Members.query.filter_by(email=email).first() is not None
        if member_exists:
            message = 'Email already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            message = 'Invalid email address!'
        elif not fullname or not email:
            message = 'Please fill out the form!'
        else:
            new_member = Members(name=fullname, email=email)
            db.session.add(new_member)
            db.session.commit()
            message = 'You Have Successfully Registered!'
            # return redirect(url_for('add_member'))

    elif request.method == 'POST':
        message = 'Please fill out the form!'
    members = Members.query.all()
    return render_template('members.html', message=message, members=members)

@app.route("/edit_member", methods=['GET', 'POST'])
def edit_member():
    # msg = ''
    if 'loggedin' in session:
        id = request.args.get('id')
        members = Members.query.get(id)
        # print(books.bookid)
        return render_template('edit_members.html', members = members)
    return redirect(url_for('login'))

@app.route("/delete_members", methods=['GET'])
def delete_member():
    if 'loggedin' in session:
        id = request.args.get('id')
        member = Members.query.get(id)
        db.session.delete(member)
        db.session.commit()
        
        return redirect(url_for('members'))
    return redirect(url_for('login'))

@app.route('/save_member', methods=['GET', 'POST'])
def save_member():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            action = request.form['action']

            if action == 'updateMember':
                id = request.form['id']
                member = Members.query.get(id)
                member.name = name
                member.email = email
                db.session.commit()
            
            return redirect(url_for('members'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template('members.html', msg=msg)
    return redirect(url_for('login'))
    
@app.route('/issued', methods=['GET', 'POST'])
def issued():
    if 'loggedin' in session:
        details = Issuedbooks.query.all()
        return render_template('issued.html', details = details)
    else:
        return redirect(url_for('login'))
    
@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if 'loggedin' in session:
        bookid = request.args.get('bookid')
        issued_book = Issuedbooks.query.get(bookid)
        if issued_book:
            db.session.delete(issued_book)
            db.session.commit()
            available_book = Availablebooks(name=issued_book.name, picture=issued_book.picture, isbn=issued_book.isbn)
            db.session.add(available_book)
            db.session.commit()
        return redirect(url_for('issued'))
    return redirect(url_for('login'))

@app.route('/user')
def user():
    user = Users.query.get(session['userid'])
    # print(user.name)
    return render_template('user.html', user=user)

@app.route("/edit_user", methods=['GET', 'POST'])
def edit_user():
    if 'loggedin' in session:
        id = request.args.get('id')
        users = Users.query.get(id)
        print(users.id)
        return render_template('edit_users.html', users = users)
    return 

@app.route("/delete_user", methods=['GET'])
def delete_user():
    if 'loggedin' in session:
        id = request.args.get('id')
        user = Users.query.get(id)
        db.session.delete(user)
        db.session.commit()
        
        return render_template('cover.html')
    return redirect(url_for('login'))

@app.route('/save_user', methods=['GET', 'POST'])
def save_user():
    msg = ''
    if 'loggedin' in session:
        if request.method == 'POST':
            name = request.form['name']
            email = request.form['email']
            password = request.form['password']
            hashed_password = bcrypt.generate_password_hash(password)
            action = request.form['action']

            if action == 'updateUser':
                id = request.form['id']
                user = Users.query.get(id)
                user.name = name
                user.email = email
                user.password = hashed_password
                db.session.commit()
            
            return redirect(url_for('user'))
        elif request.method == 'POST':
            msg = 'Please fill out the form!'
        return render_template('user.html', msg=msg)
    return redirect(url_for('login'))

if __name__ == '__main__':
    url = "http://127.0.0.1:5000"  
    webbrowser.open(url)  # Opens the URL automatically
    app.run(debug=True)

