import random
import string
from typing import List

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Product, Category, City, Vendor, Item, Order, OrderStatus, Address
from commerce.schemas import MessageOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate, \
    AddressSchema, AddressCreate, AddressOut, CheckoutSchema

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


"""
# product = Product.objects.all().select_related('merchant', 'category', 'vendor', 'label')
    # print(product)
    #
    # order = Product.objects.all().select_related('address', 'user').prefetch_related('items')

    # try:
    #     one_product = Product.objects.get(id='8d3dd0f1-2910-457c-89e3-1b0ed6aa720a')
    # except Product.DoesNotExist:
    #     return {"detail": "Not found"}
    # print(one_product)
    #
    # shortcut_function = get_object_or_404(Product, id='8d3dd0f1-2910-457c-89e3-1b0ed6aa720a')
    # print(shortcut_function)

    # print(type(product))
    # print(product.merchant.name)
    # print(type(product.merchant))
    # print(type(product.category))


Product <- Merchant, Label, Category, Vendor

Retrieve 1000 Products form DB

products = Product.objects.all()[:1000] (select * from product limit 1000)

for p in products:
    print(p)
    
for every product, we retrieve (Merchant, Label, Category, Vendor) records

Merchant.objects.get(id=p.merchant_id) (select * from merchant where id = 'p.merchant_id')
Label.objects.get(id=p.label_id) (select * from merchant where id = 'p.label_id')
Category.objects.get(id=p.category_id) (select * from merchant where id = 'p.category_id')
Vendor.objects.get(id=p.vendor_id) (select * from merchant where id = 'p.vendor_id')

4*1000+1

Solution: Eager loading

products = (select * from product limit 1000)

mids = [p1.merchant_id, p2.merchant_id, ...]
[p1.label_id, p2.label_id, ...]
.
.
.

select * from merchant where id in (mids) * 4 for (label, category and vendor)

4+1

"""


# address CRUD operations endpoints are here!
# ----
@address_controller.get('', response={
    200: List[AddressSchema],
    404: MessageOut
})
def list_addresses(request):
    user_addresses = Address.objects.filter(user=User.objects.first())
    return user_addresses


@address_controller.get('/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def retrieve_address(request, id: UUID4):
    return get_object_or_404(Address, id=id)


@address_controller.post('', response={
    201: AddressOut,
    400: MessageOut
})
def create_address(request, address_in: AddressCreate):
    address = Address(**address_in.dict(), user=User.objects.first())
    address.save()
    return 201, address


@address_controller.put('/{id}', response={
    200: MessageOut,
    400: MessageOut
})
def update_address(request, id: UUID4, address_in: AddressCreate):
    updated = Address.objects.all().filter(id=id, user=User.objects.first()).update(**address_in.dict())
    if updated:
        return 200, {"detail": "updated successfully"}
    return 400, {"detail": "No address found"}


@address_controller.delete("/{id}", response={
    204: MessageOut,
    404: MessageOut
})
def delete_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 204, {"detail": ""}


# ----
# @products_controller.get('categories', response=List[CategoryOut])
# def list_categories(request):
#     return Category.objects.all()

# cities endpoints are here
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


@order_controller.delete('item/{id}', response={
    204: MessageOut
})
def delete_item(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.delete()

    return 204, {'detail': 'Item deleted!'}


@order_controller.put("item/{id}/increase-quantity", response={
    200: MessageOut,
    404: MessageOut
})
def increase_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first())
    item.item_qty += 1
    item.save()
    return 200, {"detail": f"Item increased from {item.item_qty - 1} to {item.item_qty} successfully."}


def generate_ref_code():
    return ''.join(random.sample(string.ascii_letters + string.digits, 6))


@order_controller.post('create-order', response={
    201: MessageOut,
    400: MessageOut,
    403: MessageOut
})
def create_order(request):
    '''
    * add items and mark (ordered) field as True
    * add ref_number
    * add NEW status
    * calculate the total
    '''
    # First, checks whether there are items in the cart (items that are not ordered)
    user_items = Item.objects.filter(user=User.objects.first()).filter(ordered=False)
    if not user_items:
        return 400, {'detail': 'Can not create an order of an empty cart.'}

    '''
    Secondly, checks if there are already an active order.
    If True, add the items then merge the duplicates
    Else, make a new active order
    '''
    order = Order.objects.filter(user=User.objects.first(), ordered=False)[0]
    if order:
        ordered_products_id = list(Item.objects.filter(ordered=True).values('product_id'))
        ordered_products_id = list(map(lambda x: x['product_id'], ordered_products_id))
        for item in user_items:
            if item.product_id in ordered_products_id:
                ordered_item = Item.objects.filter(product_id=item.product_id)[0]
                ordered_item.item_qty += item.item_qty
                ordered_item.save()
                item.delete()
            else:
                order.items.add(item)
        # calculate the total
        order.total = order.order_total
        # mark items as ordered (added to a user order)
        user_items.update(ordered=True)
        order.save()

        return 201, {"detail": "There was already an order and your cart items were merged."}

    # New order
    # Create an order query set and we'll initially use 4 out of 8 attributes in an order
    order_qs = Order.objects.create(
        user=User.objects.first(),
        status=OrderStatus.objects.get(is_default=True),  # Which is 'NEW'
        ref_code=generate_ref_code(),
        ordered=False,
    )
    # add them to the order
    order_qs.items.add(*user_items)
    # calculate the total
    order_qs.total = order_qs.order_total
    # mark items as ordered (added to a user order)
    user_items.update(ordered=True)
    order_qs.save()

    return 201, {'detail': 'order created successfully'}


@order_controller.post("checkout", response={
    200: MessageOut,
    404: MessageOut
})
def checkout(request, checkout_data_in: CheckoutSchema):
    current_order = Order.objects.filter(user=User.objects.first()).filter(ordered=False)
    if current_order:
        processing = OrderStatus.objects.get(title='PROCESSING')  # proccessing must be added
        current_order.update(**checkout_data_in.dict(), status=processing.id, ordered=True)
        return 200, {'detail': 'Checkout was successful'}
    return 404, {"detail": "No current order found"}
