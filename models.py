from tortoise import Model, fields
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

from pydantic import BaseModel, EmailStr

from pydantic import BaseModel, EmailStr, Field


class User_login(BaseModel):
    email: EmailStr
    password: str


class Reset(BaseModel):
    email: EmailStr
    password: str


class Update_Product(BaseModel):
    id: int
    price: float
    discount: int


class Update_City(BaseModel):
    b_name: str
    city: str


# class UserRegisterSchema(BaseModel):
#     name: str = Field(..., max_length=20)
#     email: EmailStr
#     password: str


class User(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=100, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False, unique=True)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.utcnow)


class Bussiness(Model):
    id = fields.IntField(pk=True, index=True)
    b_name = fields.CharField(max_length=20, null=False, unique=True)
    city = fields.CharField(max_length=20, null=False, default="unspecified")
    region = fields.CharField(max_length=20, null=False, default="unspecified")
    description = fields.TextField(null=True)
    logo = fields.CharField(max_length=200, null=False, default="default.jpg")
    owner = fields.ForeignKeyField("models.User", related_name="bussiness")


class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=20, null=False, index=True)
    category = fields.CharField(max_length=30, index=True)
    price = fields.DecimalField(max_digits=12, decimal_places=2)
    discount = fields.IntField(default=0)
    offer_expiration_date = fields.DatetimeField(default=datetime.utcnow)
    image = fields.CharField(max_length=2000, null=False, default="product.jpg")
    bussiness = fields.ForeignKeyField("models.Bussiness", related_name="products")


User_Pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
UserIn_Pydantic = pydantic_model_creator(
    User, name="UserIn", exclude_readonly=True, exclude=("is_verified", "join_date")
)
UserOut_Pydantic = pydantic_model_creator(User, name="UserOut", exclude=("password",))

Bussiness_Pydantic = pydantic_model_creator(Bussiness, name="Bussiness")
BussinessIn_Pydantic = pydantic_model_creator(
    Bussiness, name="BussinessIn", exclude_readonly=True
)

Product_Pydantic = pydantic_model_creator(Product, name="Product")
ProductIn_Pydantic = pydantic_model_creator(
    Product, name="ProductIn", exclude=("discount", "id")
)
