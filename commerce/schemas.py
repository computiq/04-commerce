from typing import List, Optional

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product, Merchant, Address, Order


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
    product: ProductOut
    item_qty: int
    ordered: bool


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(UUIDSchema, ItemSchema):
    pass


class OrderOut(ModelSchema):
    class Config:
        model = Order
        model_fields = ['total', 'ordered']

class OrderStatusOut(UUIDSchema):
  status: str

class AddressUpdate(Schema):
  # user_id: UUID4
  work_address: Optional[bool]
  address2: Optional[str]
  address1: Optional[str]
  city_id: Optional[UUID4]
  phone: Optional[str]

class AddressCreate(Schema):
  # user_id: UUID4
  address1: str
  city_id: UUID4
  phone: str


class AddressOut(ModelSchema):
  city: CitySchema
  class Config:
      model = Address
      model_fields = ['id','phone', 'address1', 'address2', 'work_address']

class CheckoutSchema(Schema):
  note: Optional[str]
  address_id: Optional[UUID4]

class CheckoutSchemaOut(CheckoutSchema):
  note: str
  address: AddressOut
  ordered: bool
  total: int
