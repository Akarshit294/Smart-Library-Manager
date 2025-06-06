from flask_sqlalchemy import SQLAlchemy;

db = SQLAlchemy()

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)
    password = db.Column(db.String(150), index=True, unique=True)

    # def __repr__(self):
    #     return f'<User {self.fullname}>'

class Books(db.Model):
    __tablename__ = 'tblbook'
    bookid = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    picture = db.Column(db.String(150), index=True, unique=True, nullable=True)
    isbn = db.Column(db.String(150), index=True, unique=True)

    # One-to-one with Availablebooks
    available = db.relationship('Availablebooks', backref='book', uselist=False,
                                 cascade="all, delete", passive_deletes=True)
    
    # One-to-many with Issuedbooks
    issuedbooks = db.relationship('Issuedbooks', backref='book',
                                  cascade='all, delete', passive_deletes=True)

class Availablebooks(db.Model):
    __tablename__ = 'tblavailablebook'
    bookid = db.Column(db.Integer, db.ForeignKey('tblbook.bookid'), primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    picture = db.Column(db.String(150), index=True, unique=True, nullable=True)
    isbn = db.Column(db.String(150), index=True, unique=True)

class Members(db.Model):
    __tablename__ = 'members'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    email = db.Column(db.String(150), index=True, unique=True)

class Issuedbooks(db.Model):
    __tablename__ = 'tblissuedbook'
    bookid = db.Column(db.Integer, db.ForeignKey('tblbook.bookid', ondelete='CASCADE'), primary_key=True)
    name = db.Column(db.String(150), index=True, unique=True)
    isbn = db.Column(db.String(150), index=True, unique=True)
    member_id = db.Column(db.Integer, unique=False, nullable=False)
    member_name = db.Column(db.String(150), index=True, unique=False)
    return_date = db.Column(db.String(150), index=True, unique=False)
    picture = db.Column(db.String(150), index=True, unique=False, nullable=True)
