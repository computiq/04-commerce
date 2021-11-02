from ninja import Router
from pydantic import UUID4

from commerce.models import Address, Product, Category, City, Vendor, Item, Order, OrderStatus
from commerce.schemas import AddressSchema, AddressesOut, CheckoutSchema, MessageOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate

products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])
city_controller = Router(tags=['cities'])


@vendor_controller.get('', response=List[VendorOut])
 def list_products(
"""


# @address_controller.get('')
# def list_addresses(request):
#     pass


# @products_controller.get('categories', response=List[CategoryOut])
# def list_categories(request):
#     return Category.objects.all()


@city_controller.get('cities', response={
    200: List[CitiesOut],
    404: MessageOut
})
 def list_cities(request):
    return 404, {'detail': 'No cities found'}


@city_controller.get('cities/{id}', response={
    200: CitiesOut,
    404: MessageOut
})
def retrieve_city(request, id: UUID4):
    return get_object_or_404(City, id=id)


@city_controller.post('cities', response={
    201: CitiesOut,
    400: MessageOut
})
	def create_city(request, city_in: CitySchema):
    return 201, city


@city_controller.put('cities/{id}', response={
    200: CitiesOut,
    400: MessageOut
})
def update_city(request, id: UUID4, city_in: CitySchema):
    return 200, city


@city_controller.delete('cities/{id}', response={
    204: MessageOut
})
def delete_city(request, id: UUID4):
	 def create_order(request):
    order_qs.save()

    return {'detail': 'order created successfully'}


@order_controller.post('/orders/item/{id}/increase-quantity', response={
    200: MessageOut,
})
def increase_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.item_qty += 1
    item.save()

    return 200, {'detail': 'Item quantity increased successfully!'}



@address_controller.get('addresses', response={
    200: List[AddressesOut],
    404: MessageOut
})
def list_addresses(request):
    addresses_qs = Address.objects.all()

    if addresses_qs:
        return addresses_qs

    return 404, {'detail': 'No addresses found'}


@address_controller.get('addresses/{id}', response={
    200: AddressesOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    return get_object_or_404(Address, id=id)


@address_controller.post('addresses', response={
   200: MessageOut,
    400: MessageOut
})
def create_address(request, address_in: AddressSchema):
    Address.objects.create(**address_in.dict() , user=User.objects.first())
    return 200, {'detail': 'Added successfully'}


@address_controller.put('addresses/{id}', response={
    200: AddressSchema,
    400: MessageOut
})
def update_address(request, id: UUID4, address_in: AddressSchema):
    address = get_object_or_404(Address, id=id)
    for key, value in address_in.items():
        setattr(address, key, value)
    return 200, address


@address_controller.delete('addresses/{id}', response={
    204: MessageOut
})
def delete_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 204, {'detail': ''}


@order_controller.put('/api/orders/checkout/{id}', response=MessageOut)

def checkout(request, id: UUID4, checkout_in: CheckoutSchema):
    order = get_object_or_404(Order, id=id)
    for key, value in checkout_in.items():
        setattr(order, key, value)
    return {'detail': 'order checkout successfully'}
