from typing import List

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product, Merchant, Address,City


class MessageOut(Schema):
    detail: str


class UUIDSchema(Schema):
    id: UUID4



class VendorOut(UUIDSchema):
    name: str
    image: str


class LabelOut(UUIDSchema):
    name: str


class MerchantOut(ModelSchema):
    class Config:
        model = Merchant
        model_fields = ['id', 'name']


class CategoryOut(UUIDSchema):
    name: str
    description: str
    image: str
    children: List['CategoryOut'] = None


CategoryOut.update_forward_refs()


class ProductOut(ModelSchema):
    vendor: VendorOut
    label: LabelOut
    merchant: MerchantOut
    category: CategoryOut

    class Config:
        model = Product
        model_fields = ['id',
                        'name',
                        'description',
                        'qty',
                        'price',
                        'discounted_price',
                        'vendor',
                        'category',
                        'label',
                        'merchant',
                        ]
#
#
# class AddressOut(UUIDSchema):
#     # city = CitiesOut
#     class Config:
#         model: Address
#         model_fields = [
#             'user',
#             'work_address',
#             'address1',
#             'address2',
#             'city',
#             'phone'
#         ]
#
#
# class AddressSchema(Schema):
#     user: UUID4
#     work_address: bool
#     address1: str
#     address2: str
#     city: CitySchemaOut
#     phone: str
#
#
class CitySchemaOut(Schema):
    name: str


class CityOut(CitySchemaOut, UUIDSchema):
    class Config:
        model = City
        model_fields = ['name']

#
#


class CitySchema(Schema):
    city: str

class AddressSchemaOut(Schema):
    id: UUID4
    work_address: bool
    address1: str
    address2: str
    city: CitySchemaOut
    phone: str


class AddressCreateDataIn(Schema):
    work_address: bool
    address1: str
    address2: str
    city_id: UUID4
    phone: int

class ItemSchema(Schema):
    # user:
    product: ProductOut
    item_qty: int
    ordered: bool


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(UUIDSchema, ItemSchema):
    pass

class CheckoutSchema(Schema):
    note: str =None
    addresss: UUID4
