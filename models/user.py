from mongoengine import *

class User(Document):
    user_id = IntField(primary_key=True)
    first_name = StringField(required=True)
    last_name = StringField()
    username = StringField()
    email = StringField()
    
    def __str__(self):
        return self.username

# util methods

def get_user(user_id):
    return User.objects(user_id=user_id).first()

def get_user_by_username(username):
    return User.objects(username=username).first()

def create_user(user_id, first_name, last_name, username, email=None):
    user = User(user_id=user_id, first_name=first_name, last_name=last_name, username=username, email=email)
    user.save()
    return user

def update_user(user_id, first_name=None, last_name=None, username=None, email=None):
    user = get_user(user_id)
    if first_name:
        user.first_name = first_name
    if last_name:
        user.last_name = last_name
    if username:
        user.username = username
    if email:
        user.email = email
    user.save()
    return user

def delete_user(user_id):
    user = get_user(user_id)
    user.delete()

