from typing import List

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product, Merchant


class MessageOut(Schema):
    detail: str


class UUIDSchema(Schema):
    id: UUID4


# ProductSchemaOut = create_schema(Product, depth=2)

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


# class ProductManualSchemaOut(Schema):
#     pass


class AddressSchema(Schema):
    work_address: bool = False
    address1: str
    phone: str

class CitySchema(Schema):
    name: str

class CitiesOut(CitySchema, UUIDSchema):
    pass


class AddressesOut(AddressSchema, UUIDSchema):
    city: CitiesOut



class CitiesOut(CitySchema, UUIDSchema):
    pass


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




class OrderStatusOut(Schema):
    title: str


class UserOut(Schema):
    username: str

class OrderSchema(Schema):
    items: List[ItemSchema]
    status: OrderStatusOut
    address: AddressesOut
    order_total: float
    ordered: bool
    user: UserOut
    ref_code: str
    note: str

class OrderCreate(Schema):
    items: List[UUID4]
    address: UUID4
    note: str

