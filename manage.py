from os import name
from typing import List
from django.db import models

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4
# from pydantic.main import Model

from commerce.models import Address, OrderStatus, Product, Merchant


class MessageOut(Schema):
 class CategoryOut(UUIDSchema):
    children: List['CategoryOut'] = None


CategoryOut.update_forward_refs()  


class ProductOut(ModelSchema):
class ItemOut(UUIDSchema, ItemSchema):
    pass


class AddressSchema(Schema):
    work_address:str
    address1:str
    address2:str
    phone:str
    city_id:UUID4

class addressOut(AddressSchema):
     pass


class OrderSchema(Schema):

    note:str
    address:addressOut
