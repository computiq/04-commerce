from typing import List
import random
import string

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Product, Address, Category, City, OrderStatus, Vendor, Order
from commerce.schemas import MessageOut, AddressSchemaOut, AddressCreateDataIn, ProductOut \
    , CitySchemaOut, CityOut, VendorOut, CheckoutSchema, \
    ItemOut, ItemSchema, ItemCreate

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
    200: list[AddressSchemaOut],
    404: MessageOut
})
def list_addresses(request):
    address = Address.objects.all()
    if address:
        return address
    else:
        return 404, {'detail': 'error'}


@address_controller.get('address/{id}', response={
    200: AddressesOut,
    404: MessageOut
})
def address(request, id: UUID4):
    return get_object_or_404(Address, id=id)

@address_controller.post('adrress', response={
    201: AddressSchemaOut,
    404: MessageOut
})
def add_adress(request, adress_in: AddressCreateDataIn):
    address = Address.objects.create(**address_in.dict(), user=User.objects.first())
    address.save()
    return 201, address


@address_controller.put('address/{id}')
def address_update(request, id: UUID4, adress_in: AddressCreateDataIn):
    address = get_object_or_404(Address, id=id)
    for attr, value in adress_in.dict().items():
        setattr(employee, attr, value)
        address.save()


@address_controller.delete('address/{id}', response=MessageOut)
def address_delete(request, id: UUID4, ):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 200, {'detail': 'done'}


@address_controller.get('cities', response={
    200: List[CityOut],
    404: MessageOut
})
def list_cities(request):
    cities_qs = City.objects.all()

    if cities_qs:
        return cities_qs

    return 404, {'detail': 'No cities found'}


@address_controller.get('cities/{id}', response={
    200: CityOut,
    404: MessageOut
})
def retrieve_city(request, id: UUID4):
    return get_object_or_404(City, id=id)


@address_controller.post('cities', response={
    201: CityOut,
    400: MessageOut
})
def create_city(request, city_in: CitySchemaOut):
    city = City(**city_in.dict())
    city.save()

    return 201, city


#
# @address_controller.post('city', response={
#     201: CityOut,
#     400: MessageOut
# })
# def create_city(request, city_in: CitySchemaOut):
#     city = City(**city_in.dict())
#     city.save()
#     return 201, city


@address_controller.put('cities/{id}', response={
    200: CityOut,
    400: MessageOut
})
def update_city(request, id: UUID4, city_in: CitySchemaOut):
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
    return 200, {'detail': ''}


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


@order_controller.post('item/{id}/increase-quantity', response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.item_qty += 1
    item.save()

    return 200, {'detail': 'Item quantity increase successfully!'}


@order_controller.delete('item/{id}', response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.delete()

    return 204, {'detail': 'Item deleted!'}


def generta_ref_Code():
    return ''.join(random.smaple(string.ascii_letters + string.digits, 6))


@order_controller.post('ceate-order', response=MessageOut)
def create_order(request):
    order_qs = Order(
        user=User.objects.first(),
        status=OrderStatus.objects.get(is_default=True),
        red_code=generta_ref_Code(),
        ordered=False
    )
    user_items = Item.objects.filter(user=User.objects.first())
    user_items.update(ordered=True)
    order_qs.items.append(*user_items)
    order_qs.total = order_qs.order_total
    order_qs.save()

    return {'detail': 'create done'}


@order_controller.post('/checkout', response={
    200: MessageOut,
    404: MessageOut
})
def checkout(request, checkout_info: CheckoutSchema):
    order = get_object_or_404(Order, user=User.objects.first(), ordered=False)

    if order:
        order.note = checkout_info.note
        order.address = Address.objects.get(id=checkout_info.address)
        order.status = OrderStatus.objects.get(is_default=False)
        order.ordered = True
        order.save()
        return 200, {'detail': 'checkout succifully'}
    else:
        return 404, {'detail': 'No active orders '}
