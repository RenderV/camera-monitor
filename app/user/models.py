import json
from flask_wtf import FlaskForm
from mongoengine import *
from datetime import datetime
import random

class User(Document):
    username = StringField(unique=False, required=True)
    email = EmailField(unique=True)
    password = BinaryField(required=True)
    date_created = DateTimeField(default=datetime.utcnow)
    admin = BooleanField(default=False)

    meta = {
        "indexes": ["email"],
        "ordering": ["-date_created"]
    }
    
    def json(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "date_created": str(self.date_created),
            "is_admin": self.admin
        }
        return json.dumps(user_dict)

    def asdict(self):
        user_dict = {
            "username": self.username,
            "email": self.email,
            "date_created": str(self.date_created),
            "is_admin": self.admin,
        }
        return user_dict