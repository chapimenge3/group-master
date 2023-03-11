from datetime import datetime
from mongoengine import *
from models.user import User
from models.group import Group
from models.transaction import Transaction
from bson.objectid import ObjectId
from uuid import uuid4 as uuid


class Membership(Document):
    membership_id = UUIDField(required=True, primary_key=True)
    user = ReferenceField(User, required=True)
    group = ReferenceField(Group, required=True)
    start_date = DateField(required=True)
    end_date = DateField(required=True)
    status = StringField(required=True)
    transaction = ReferenceField(Transaction, required=True)
    created_at = DateTimeField(required=True)
    updated_at = DateTimeField(required=True)

    def __str__(self):
        return self.membership_id


def get_membership(membership_id):

    return Membership.objects(membership_id=membership_id).first()


def create_membership(user, group, start_date, end_date, status, transaction, created_at=None, updated_at=None):
    membership_id = uuid()
    if not created_at:
        created_at = datetime.now()
    if not updated_at:
        updated_at = datetime.now()

    membership = Membership(membership_id=membership_id, user=user, group=group, start_date=start_date, end_date=end_date,
                            status=status, transaction=transaction, created_at=created_at, updated_at=updated_at)
    membership.save()
    return membership


def get_all_memberships():
    return Membership.objects()


def update_membership(membership_id, user=None, group=None, start_date=None, end_date=None, status=None, transaction=None, created_at=None, updated_at=None):
    membership = get_membership(membership_id)
    if user:
        membership.user = user
    if group:
        membership.group = group
    if start_date:
        membership.start_date = start_date
    if end_date:
        membership.end_date = end_date
    if status:
        membership.status = status
    if transaction:
        membership.transaction = transaction
    if created_at:
        membership.created_at = created_at
    if updated_at:
        membership.updated_at = updated_at
    else:
        membership.updated_at = datetime.now()

    membership.save()
    return membership


def get_membership_by_user_and_group(user, group):
    return Membership.objects(user=user, group=group).first()


def check_valid_membership(user, group):
    membership = get_membership_by_user_and_group(user, group)
    today = datetime.now().date()
    if membership and membership.end_date >= today:
        return True
    return False


def get_membership_by_user(user):
    return Membership.objects(user=user)
