from mongoengine import *
from models.user import User
from models.group import Group
from uuid import uuid4 as uuid
from bson.objectid import ObjectId
from datetime import datetime


class Transaction(Document):
    transaction_id = UUIDField(required=True, primary_key=True)
    user = ReferenceField(User, required=True)
    group = ReferenceField(Group, required=True)
    amount = IntField(required=True)
    status = StringField(required=True)
    payment_method = StringField(required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    def __str__(self):
        return self.transaction_id


def get_transaction(transaction_id):
    return Transaction.objects(transaction_id=transaction_id).first()


def create_transaction(user, group, amount, status, payment_method, created_at=None, updated_at=None):
    transaction_id = uuid()
    if not created_at:
        created_at = datetime.now()
    if not updated_at:
        updated_at = datetime.now()
    transaction = Transaction(transaction_id=transaction_id, user=user, group=group, amount=amount,
                              status=status, payment_method=payment_method, created_at=created_at, updated_at=updated_at)
    transaction.save()
    return transaction


def get_all_transactions():
    return Transaction.objects()


def update_transaction(transaction_id, user=None, group=None, amount=None, status=None, payment_method=None, created_at=None, updated_at=None):
    transaction = get_transaction(transaction_id)
    if user:
        transaction.user = user
    if group:
        transaction.group = group
    if amount:
        transaction.amount = amount
    if status:
        transaction.status = status
    if payment_method:
        transaction.payment_method = payment_method
    if created_at:
        transaction.created_at = created_at
    if updated_at:
        transaction.updated_at = updated_at
    else:
        transaction.updated_at = datetime.now()
    transaction.save()
    return transaction


def delete_transaction(transaction_id):
    transaction = get_transaction(transaction_id)
    transaction.delete()
