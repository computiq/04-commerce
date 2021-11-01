from typing import List
from uuid import UUID, uuid4

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


class CitySchema(Schema):
    name: str


class CitiesOut(CitySchema, UUIDSchema):
    pass


class ItemSchema(Schema):
    # user:
    item_qty: int
    ordered: bool
    product: ProductOut


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(ItemSchema, UUIDSchema):
    pass


class AddressSchema(Schema):
    work_address: bool
    address1: str
    address2: str
    phone: str
    city: CitiesOut


class AddressCreate(Schema):
    work_address: bool
    address1: str
    address2: str
    phone: str
    city_id: UUID4


class AddressOut(AddressSchema, UUIDSchema):
    pass


class OrderOut(Schema):
    note: str = None
    ref_code: str
    ordered: bool
    address: AddressSchema = None
    items: List[ItemOut]


class OrderSchema(OrderOut, UUIDSchema):
    pass


class OrderChange(Schema):
    item_id: UUID4
    prodect_id: UUID4



class CheckOut(Schema):
    note: str
    address_id: UUID4