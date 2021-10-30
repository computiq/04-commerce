from typing import List

from ninja import ModelSchema, Schema
# from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Product, Merchant


class MessageOut(Schema):
    detail: str


class UUIDSchema(Schema):
    id: UUID4


# ProductSchemaOut = create_schema(Product, depth=2)

class VendorOut(UUIDSchema):
    name:  str
    image: str


class LabelOut(UUIDSchema):
    name: str


class MerchantOut(ModelSchema):
    class Config:
        model = Merchant
        model_fields = ['id', 'name']


class CategoryOut(UUIDSchema):
    name:        str
    description: str
    image:       str
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

class OrderStatusShcema(Schema):
    title:      str
    is_default: bool

class CreateAdress(Schema):
    work_address:    bool
    address1:        str
    address2:        str
    city_id:         UUID4
    phone:           str

class AdressOut(CreateAdress, UUIDSchema):
    pass

class OrderShema(Schema):
    address_id:  UUID4 = None
    note:        str = None

class OrderOut(OrderShema):
    items:       List[ItemOut]
    status_id:   UUID4 = None
    total:       float
    ref_code:    str
    ordered:     bool

class OrderShemaCreat(OrderShema):
    address_id:  UUID4


"""
    @property
    def order_total(self):
        return sum(
            i.product.discounted_price * i.item_qty for i in self.items.all()
        )
"""
