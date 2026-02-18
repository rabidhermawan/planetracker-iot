from werkzeug.security import generate_password_hash, check_password_hash # Hmmm I dunno, may change it to bcrypt
from faizencryption import db, login_manager # Extends the database to be here
from flask_login import UserMixin # Provides user auth, easier for protecting routes
from uuid import uuid4
from datetime import datetime, timezone

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column("id", db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))
    name = db.Column("name", db.String(100), nullable=False)
    email = db.Column("email", db.String(100), nullable=False, unique=True)
    password_hashed = db.Column("password", db.String(128), nullable=False)
    
    @property
    def password(self):
        raise AttributeError("Password is not a readable attribute")
    
    @password.setter
    def password(self, password):
        self.password_hashed = generate_password_hash(password)
    
    def verify_password(self, password):
        return check_password_hash(self.password_hashed, password)
    
    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.password = password
    
    documents = db.relationship(
        "UserDocument",
        back_populates="user",
        cascade="all, delete-orphan"
    )
    
        
class Document(db.Model, UserMixin):
    id = db.Column("id", db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid4()))
    user_uuid = db.Column(db.String(36), db.ForeignKey("user.uuid"), nullable=False)
    
    name = db.Column("name", db.String(100), nullable=False)
    file_type = db.Column("type", db.String(100), nullable=False)
    enc_type = db.Column(db.String(16), nullable=False)
    
    # description = db.Column("description", db.LargeBinary, nullable=False)
    upload_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    def __init__(self, user_uuid, name, file_type, enc_type):
        self.user_uuid = user_uuid
        self.name = name
        self.file_type = file_type
        self.enc_type = enc_type
        
    users = db.relationship(
        "UserDocument",
        back_populates="document",
        cascade="all, delete-orphan"
    )
        
class UserDocument(db.Model):
    id = db.Column("id", db.Integer, primary_key=True)
    user_id = db.Column(db.Integer , db.ForeignKey('user.id'))
    document_id = db.Column(db.Integer , db.ForeignKey('document.id'))
    share_date = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    
    user = db.relationship("User", back_populates="documents")
    document = db.relationship("Document", back_populates="users")