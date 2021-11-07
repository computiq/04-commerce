import random
import string
from typing import List
from ninja import Router
from pydantic import UUID4
from django.contrib.auth.models import User
from django.db.models import Q
from django.db.models.fields import NullBooleanField
from django.shortcuts import get_object_or_404
from commerce.models import Address, Product, Category, City, Vendor, Item, Order, OrderStatus
from commerce.schemas import MessageOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate, addressOut, AddressSchema, OrderSchema

vendor_controller = Router(tags=['vendors'])
products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
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
    products_qs = Product.objects.filter(is_active=True).select_related(
        'merchant', 'vendor', 'category', 'label')

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


@address_controller.get('')
def list_addresses(request):
    return list(Address.objects.values())


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
        item = Item.objects.get(
            product_id=item_in.product_id, user=User.objects.first())
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

#  increase quantity


@order_controller.post('item/{id}/increase-quantity', response={
    200: MessageOut,
})
def increase_quantity(request, id: UUID4):
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


def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@order_controller.post('create-order', response=MessageOut)
def create_order(request):

    order_qs = Order.objects.create(
        user=User.objects.first(),
        status=OrderStatus.objects.get(is_default=True),
        ref_code=generate_ref_code(),
        ordered=False,
    )

    user_items = Item.objects.filter(
        user=User.objects.first()).filter(ordered=False)

    order_qs.items.add(*user_items)
    order_qs.total = order_qs.order_total
    user_items.update(ordered=True)
    order_qs.save()

    return {'detail': 'order created successfully'}


@address_controller.post('address', response={
    201: addressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressSchema):
    address = Address(**address_in.dict(), user=User.objects.first())
    address.save()
    return 201, address


@address_controller.delete('address/{id}', response={
    204: MessageOut
})
def delete_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 204, {'detail': 'Address deleted successfully'}


@address_controller.put('address/{id}', response={
    200: addressOut,
    400: MessageOut
})
def update_address(request, id: UUID4, address_in: AddressSchema):
    address = get_object_or_404(Address, id=id)
    address.address1 = address_in.address1
    address.address2 = address_in.address2
    address.phone = address_in.phone

    address.save()
    return 200, address


@address_controller.get('address/{id}', response={
    200: addressOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    return get_object_or_404(Address, id=id,)


@order_controller.get('Checkout', response={
    200: MessageOut,
    404: MessageOut
})
def checkout(request, order_in: OrderSchema):
    order = Order.objects.get(user=User.objects.first(), ordered=False)
    if order:
        order.note = order_in.note
        order.address = order_in.address
        order.ordered = True
        order.status = OrderStatus.objects.update(
            status='PROCESSING', is_default=False),

        order.save()
        return 200
    else:
        return 404
