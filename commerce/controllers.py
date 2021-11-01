import random
import string
from typing import List

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Product, Category, City, Vendor, Item, Address, Order, OrderStatus
from commerce.schemas import MessageOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate, \
    AddressSchema, AddressOut, CheckoutSchema

''' Routers '''
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


""" Cities """


@address_controller.get('cities', response={
    200: List[CitiesOut],
    404: MessageOut
})
def list_cities(request):
    cities_qs = City.objects.all()

    if cities_qs:
        return cities_qs

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
    404: MessageOut
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


""" Addresses """


@address_controller.get('', response={
    200: List[AddressOut],
    404: MessageOut
})
def list_addresses(request):
    addresses = Address.objects.all()
    if addresses:
        return addresses
    return 404, {'detail': 'No Addresses Found'}


@address_controller.get('/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    return address


@address_controller.post('', response={
    201: AddressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressSchema):
    city_instance = City.objects.get(id=address_in.city)
    del address_in.city
    address = Address.objects.create(**address_in.dict(), city=city_instance, user=User.objects.first())
    address.save()
    return 201, address


@address_controller.put('/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def update_address(request, id: UUID4, new_data: AddressSchema):
    address = get_object_or_404(Address, id=id)
    city_instance = City.objects.get(id=new_data.city)
    new_data.city = city_instance
    for attr, value in new_data.dict().items():
        setattr(address, attr, value)
    address.save()
    return 200, address


@address_controller.delete('/{id}', response={
    204: MessageOut
})
def delete_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 204, {'detail': ''}


""" Orders """


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
    400: MessageOut
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


@order_controller.post('item/{id}/increase-quantity', response={
    200: MessageOut,
})
def increase_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.item_qty += 1
    item.save()

    return 200, {'detail': 'Item quantity increased successfully!'}


@order_controller.delete('item/{id}', response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.delete()

    return 204, {'detail': 'Item deleted!'}


def ref_code():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=6))


@order_controller.post('/create-order', response={
    200: MessageOut,
    400: MessageOut
})
def create_order(request):
    if not Order.objects.filter(ordered=False):
        order = Order.objects.create(
            user=User.objects.first(),
            status=OrderStatus.objects.get(is_default=True),
            ref_code=ref_code(),
            ordered=False
        )

        user_items = Item.objects.filter(user=User.objects.first()).filter(ordered=False)
        order.items.add(*user_items)
        order.total = order.order_total
        user_items.update(ordered=True)
        order.save()
        return 200, {'detail': 'created successfully '}

    else:
        
        order_items = Order.objects.filter(user=User.objects.first(), ordered=False).values('items__product__id',
                                                                                            'items__item_qty', 
                                                                                            'items__product__discounted_price')
        cart_items = Item.objects.filter(user=User.objects.first()).values('product', 'item_qty')
        for item_in_cart in list(cart_items):
            for item_in_order in list(order_items):
                if item_in_cart['product'] == item_in_order['items__product__id']:
                    item_in_cart['item_qty'] += item_in_order['items__item_qty']

                # just wanted a way to update total after merging the quantities
                item_discounted_price = [li['items__product__discounted_price'] for li in order_items]

                for discount in item_discounted_price:
                    total_price = sum(item['item_qty'] * discount for item in list(cart_items))

                Order.objects.update(total=total_price)

    return 400, {'detail': 'There is an active order'}


@order_controller.post('/checkout', response={
    200: MessageOut,
    404: MessageOut
})
def checkout(request, checkout_info: CheckoutSchema):
    order_obj = get_object_or_404(Order, user=User.objects.first(), ordered=False)

    if order_obj:
        order_obj.note = checkout_info.note
        order_obj.address = Address.objects.get(id=checkout_info.address)
        order_obj.status = OrderStatus.objects.get(is_default=False)
        order_obj.ordered = True
        order_obj.save()
        return 200, {'detail': 'checkout done'}

    return 404, {'detail': 'No active orders found'}

