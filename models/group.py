from mongoengine import *


class Group(Document):
    group_id = IntField(primary_key=True)
    name = StringField(required=True)
    price = IntField(required=True)
    duration = IntField(required=True)

    def __str__(self):
        return self.name

def get_group(group_id):
    return Group.objects(group_id=group_id).first()


def create_group(group_id, name, price, duration):
    group = Group(group_id=group_id, name=name, price=price, duration=duration)
    group.save()
    return group


def get_all_groups():
    return Group.objects()


def update_group(group_id, name=None, price=None, duration=None):
    group = get_group(group_id)
    if name:
        group.name = name
    if price:
        group.price = price
    if duration:
        group.duration = duration
    group.save()
    return group
