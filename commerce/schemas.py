import string
from typing import List

from ninja import ModelSchema, Schema
from ninja.orm import create_schema
from pydantic import UUID4

from commerce.models import Address, Product, Merchant


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
    id : UUID4
    product: ProductOut
    item_qty: int
    ordered: bool


class ItemCreate(Schema):
    product_id: UUID4
    item_qty: int


class ItemOut(UUIDSchema, ItemSchema):
    pass

#-----------------------------------------------


class OrderStatusOut(UUIDSchema):
    title : str
    


class OrderOut(UUIDSchema) :
    total  : int = None
    note : str = None
    ordered : bool
    items : List[ItemSchema]
    ref_code : str = None


class AddressOut(UUIDSchema):
    id : UUID4
    work_address : bool = None
    address1 : str 
    address2 : str = None
    phone : str 


class AddressIn(Schema):
    work_address : bool
    address1 : str
    address2 : str  
    phone : str


    

