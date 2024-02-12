import datetime
from tkinter import CASCADE

from tortoise import Model, fields

from examples.enums import ProductType, Status
from fastapi_admin.models import AbstractAdmin


class Admin(AbstractAdmin):
    last_login = fields.DatetimeField(description="Last Login", default=datetime.datetime.now)
    email = fields.CharField(max_length=200, default="")
    avatar = fields.CharField(max_length=200, default="")
    intro = fields.TextField(default="")
    created_at = fields.DatetimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.pk}#{self.username}"


class Category(Model):
    slug = fields.CharField(max_length=200)
    name = fields.CharField(max_length=200)
    created_at = fields.DatetimeField(auto_now_add=True)


class Room(Model):
    categories = fields.ManyToManyField("models.Category")
    name = fields.CharField(max_length=50)
    title = fields.TextField()
    description = fields.TextField()
    view_num = fields.IntField(description="View Num")
    sort = fields.IntField()
    is_active = fields.BooleanField(description="Is Active")
    type = fields.IntEnumField(ProductType, description="Product Type")
    recommended_video = fields.CharField(max_length=200)
    body = fields.TextField()
    created_at = fields.DatetimeField(auto_now_add=True)

class Collection(Model):
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    rooms = fields.ManyToManyField('models.Room', related_name='collections')

class Module(Model):
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    author = fields.ForeignKeyField('models.User', related_name='modules', on_delete=CASCADE)
    level = fields.IntField()
    is_active = fields.BooleanField(default=False)
    collections = fields.ManyToManyField('models.Collection', related_name='modules')

class Section(Model):
    title = fields.CharField(max_length=255)
    description = fields.TextField(null=True)
    room = fields.ForeignKeyField('Room', related_name='sections', on_delete=CASCADE, null=True)
    order = fields.IntField()


class Question(Model):
    text = fields.TextField()
    section = fields.ForeignKeyField('Section', related_name='questions', on_delete=CASCADE)
    order = fields.IntField()

class Config(Model):
    label = fields.CharField(max_length=200)
    key = fields.CharField(max_length=20, unique=True, description="Unique key for config")
    value = fields.JSONField()
    status: Status = fields.IntEnumField(Status, default=Status.on)
