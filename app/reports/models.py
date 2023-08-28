import json, random
from mongoengine import *
from datetime import datetime

class Report(Document):
    date = DateTimeField(default=datetime.utcnow)
    location = StringField(unique=False, required=True)
    image_url = StringField(unique=True, required=True)
    
    meta = {
        "ordering": ["-date"]
    }

    def json(self):
        user_dict = {
            'date': self.date.isoformat(),
            'location': self.location,
            'image_url': self.image_url,
        }
        return json.dumps(user_dict)
    
    def asdict(self):
        user_dict = {
            'date': str(self.date),
            'location': self.location,
            'image_url': self.image_url,
        }
        return user_dict