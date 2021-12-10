import random
import string
from typing import List
from uuid import uuid4

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Address, Product, Category, City, Vendor, Item, Order, OrderStatus
from commerce.schemas import AddressOut, MessageOut, OrderOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate

products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])


@vendor_controller.get('', response=List[VendorOut])
def list_vendors(request):
    return Vendor.objects.all()


@products_controller.get('', response={
    200: List[ProductOut],
    404: MessageOut
})
def list_products(
        request, *,
        q: str = None,
        price_from: int = None,
        price_to: int = None,
        vendor=None,
):
    products_qs = Product.objects.filter(is_active=True).select_related('merchant', 'vendor', 'category', 'label')

    if not products_qs:
        return 404, {'detail': 'No products found'}

    if q:
        products_qs = products_qs.filter(
            Q(name__icontains=q) | Q(description__icontains=q)
        )

    if price_from:
        products_qs = products_qs.filter(discounted_price__gte=price_from)

    if price_to:
        products_qs = products_qs.filter(discounted_price__lte=price_to)

    if vendor:
        products_qs = products_qs.filter(vendor_id=vendor)

    return products_qs




@address_controller.get('address', response={
    200: List[AddressOut],
    404 : MessageOut
})
def list_addresses(request):
    add_qs= Address.objects.all()
    if add_qs:
        return add_qs
    return 404,{'details': 'no address'}

@address_controller.get('addaddress', response={
    200: MessageOut,
    404 : MessageOut
})
def create_addresse(request, add_in: AddressOut):
    Address.objects.create(**add_in.dict(), user= User.objects.first())
    return 200, {'ddetails',"address added!"}

    
@address_controller.get('address/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    return get_object_or_404(Address, id=id)

@address_controller.put('address/{id}', response={
    200: AddressOut,
    400: MessageOut
})
def update_address(request, id: UUID4, add_in: AddressOut):
    address = get_object_or_404(Address, id=id)
    for key, value in add_in.items():
        setattr(address, key, value)
    return 200, address


@address_controller.get('cities', response={
    200: List[CitiesOut],
    404: MessageOut
})
def list_cities(request):
    cities_qs = City.objects.all()

    if cities_qs:
        return cities_qs

    return 404, {'detail': 'No cities found'}

@address_controller.get('Items',response={
    200: List[ItemCreate],
    404: MessageOut,
})
def list_item(request):
    item_qs = Item.objects.all()

    if item_qs:
        return item_qs

    return 404, {'detail': 'No cities found'}


@address_controller.get('cities/{id}', response={
    200: CitiesOut,
    404: MessageOut
})

def retrieve_city(request, id: UUID4):
    return get_object_or_404(City, id=id)


@address_controller.post('cities', response={
    201: CitiesOut,
    400: MessageOut
})
def create_city(request, city_in: CitySchema):
    city = City(**city_in.dict())
    city.save()
    return 201, city


@address_controller.put('cities/{id}', response={
    200: CitiesOut,
    400: MessageOut
})
def update_city(request, id: UUID4, city_in: CitySchema):
    city = get_object_or_404(City, id=id)
    city.name = city_in.name
    city.save()
    return 200, city


@address_controller.delete('cities/{id}', response={
    204: MessageOut
})
def delete_city(request, id: UUID4):
    city = get_object_or_404(City, id=id)
    city.delete()
    return 204, {'detail': ''}


@order_controller.get('cart', response={
    200: List[ItemOut],
    404: MessageOut
})
def view_cart(request):
    cart_items = Item.objects.filter(user=User.objects.first(), ordered=False)

    if cart_items:
        return cart_items

    return 404, {'detail': 'Your cart is empty, go shop like crazy!'}


@order_controller.post('add-to-cart', response={
    200: MessageOut,
    # 400: MessageOut
})
def add_update_cart(request, item_in: ItemCreate):
    try:
        item = Item.objects.get(product_id=item_in.product_id, user=User.objects.first())
        item.item_qty += 1
        item.save()
    except Item.DoesNotExist:
        Item.objects.create(**item_in.dict(), user=User.objects.first())

    return 200, {'detail': 'Added to cart successfully'}


@order_controller.post('item/{id}/reduce-quantity', response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    if item.item_qty <= 1:
        item.delete()
        return 200, {'detail': 'Item deleted!'}
    item.item_qty -= 1
    item.save()

    return 200, {'detail': 'Item quantity reduced successfully!'}


@order_controller.post('item/{id}/increase-qty', response={
    200: MessageOut
})
def increase_qty(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.item_qty +=1
    item.save()
    return 200 , {'detail': 'Item quantity icreased successfully!'}


@order_controller.post('create', response={
    200: OrderOut ,
    400: MessageOut
})
def create_order():
    # set order specification
    orderquery = Order.objects.create(
        user = User.objects.first(),
        status = OrderStatus.objects.get(is_defualt=True),
        ref_code= generate_ref_code(),
        Order=False,
    )
    # get itemes from item tb - to specific user- oserderd is false
    item_list = Item.objects.filter(user=User.objects.first()).filter(ordered=False)

    #links  items to order
    orderquery.items.add(*item_list)
    item_list.update(ordered=True)
    orderquery.total =orderquery.order_total
    orderquery.save()
    return {'detail': 'successfull creation'}



@order_controller.delete('item/{id}', response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.delete()

    return 204, {'detail': 'Item deleted!'}


def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@order_controller.post('create-order', response=MessageOut)
def create_order(request):
    '''
    * add items and mark (ordered) field as True
    * add ref_number
    * add NEW status
    * calculate the total
    '''

    order_qs = Order.objects.create(
        user=User.objects.first(),
        status=OrderStatus.objects.get(is_default=True),
        ref_code=generate_ref_code(),
        ordered=False,
    )

    user_items = Item.objects.filter(user=User.objects.first()).filter(ordered=False)

    order_qs.items.add(*user_items)
    order_qs.total = order_qs.order_total
    user_items.update(ordered=True)
    order_qs.save()

    return {'detail': 'order created successfully'}


