from typing import List
import string
import random
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import *
from commerce.schemas import *

products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
	@ @ -53, 61 + 54, 6 @ @ def list_products(
    return products_qs



@ address_controller.get('')
def list_addresses(request):
	@ @ -212, 6 + 158, 20 @ @ def reduce_item_quantity(request, id: UUID4):
    return 200, {'detail': 'Item quantity reduced successfully!'}


@ order_controller.post('item/{id}/increase-quantity', response={
    200: MessageOut,
})
def increase_item_quantity(request, id: UUID4):
    item=get_object_or_404(Item, id=id, user=User.objects.first())
    if item.item_qty <= 1:
        item.delete()
        return 200, {'detail': 'Item deleted!'}
    item.item_qty += 1
    item.save()

    return 200, {'detail': 'Item quantity increase successfully!'}


@ order_controller.delete('item/{id}', response={
    204: MessageOut
})
	@ @ -220, 3 + 180, 98 @ @ def delete_item(request, id: UUID4):
    item.delete()

    return 204, {'detail': 'Item deleted!'}

def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))

# -----------create-order----------------
@ order_controller.post('create-order', response=MessageOut)
def create_order(request):

    order_qs=Order.objects.create(
        user=User.objects.first(),
        status=OrderStatus.objects.get(is_default=True),
        ref_code=generate_ref_code(),
        ordered=False,
    )

    user_items=Item.objects.filter(
        user=User.objects.first()).filter(ordered=False)

    order_qs.items.add(*user_items)
    order_qs.total=order_qs.order_total
    user_items.update(ordered=True)
    order_qs.save()

    return {'detail': 'order created successfully'}

# -----------address----------------

@ order_controller.get('address', response={
    200: List[AddressOut],
    404: MessageOut
})
def list_address(request):
    address_qs=Address.objects.all()

    if address_qs:
        return address_qs

    return 404, {'detail': 'No address found'}


@ address_controller.get('order_address/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    return get_object_or_404(Address, id=id)


@ order_controller.post('order_address', response={
    201: AddressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressSchema):
    address=Address(**address_in.dict())
    address.save()
    return 201, address


@ order_controller.put('order_address/{id}', response={
    200: AddressOut,
    400: MessageOut
})
def update_address(request, id: UUID4, address_in: AddressSchema):
    address=get_object_or_404(Address, id=id)
    address.address1=address_in.address1
    address.address2=address_in.address2
    address.phone=address_in.phone
    address.work_address=address_in.work_address
    address.save()
    return 200, address


@ order_controller.delete('order_address/{id}', response={
    204: MessageOut
})
def delete_city(request, id: UUID4):
    address=get_object_or_404(Address, id=id)
    address.delete()
    return 204, {'detail': ''}


# ----------------checkout-----------

@ order_controller.post('checkout', response=MessageOut)
def checkout(request, order_address: CheckOut):
    order_item=Order.objects.filter(
        user=User.objects.first()).filter(ordered=False)
    if order_item:
        order_item.note=order_address.note
        order_item.address=order_address.address
        order_item.update(ordered=True)
        order_item.status=OrderStatus.objects.get(is_default=False)
        order_item.save()
        return {'detail': 'done checkout'}
    else:
        return{'detail': 'nothing'}
