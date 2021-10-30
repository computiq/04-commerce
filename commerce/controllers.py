from typing import List
import random
import string

from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4

from commerce.models import Address, Order, OrderStatus, Product, City, Vendor, Item
from commerce.schemas import AdressOut, CreateAdress, MessageOut, OrderOut, OrderShemaCreat, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemCreate

products_controller = Router(tags = ['products'] )
address_controller  = Router(tags = ['addresses'] )
vendor_controller   = Router(tags = ['vendors'] )
order_controller    = Router(tags = ['orders'] )
checkout_controller = Router(tags = ['checkout'])


@vendor_controller.get('', response = List[VendorOut] )
def list_vendors(request):
    return Vendor.objects.all()


@products_controller.get('', response={
    200: List[ProductOut],
    404: MessageOut
})
def list_products(
        request, *,
        q:          str = None,
        price_from: int = None,
        price_to:   int = None,
        vendor          = None, ):

    products_qs = Product.objects.filter(is_active = True).select_related('merchant', 'vendor', 'category', 'label')

    if not products_qs:
        return 404, {'detail': 'No products found'}

    if q:
        products_qs = products_qs.filter(
            Q(name__icontains = q) | Q(description__icontains = q)
        )

    if price_from:
        products_qs = products_qs.filter(discounted_price__gte = price_from)

    if price_to:
        products_qs = products_qs.filter(discounted_price__lte = price_to)

    if vendor:
        products_qs = products_qs.filter(vendor_id = vendor)
    
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


"""
finish the addresses CRUD operations
/api/addresses
"""

@address_controller.get('', response= {
    200: List[AdressOut],
    404: MessageOut
})
def list_addresses(request):
    adress_qs = Address.objects.all()
    if adress_qs:
        return 200, adress_qs

    return 404, {'detail': 'No adresses found'}

@address_controller.post("add-adress", response={
    200: AdressOut
})
def add_adress(request, adress_in: CreateAdress):
    adress = Address(**adress_in.dict(), user= User.objects.first())
    adress.save()
    return 200, adress

@address_controller.delete("delete-adress{id}/", response= {
    200: MessageOut
})
def delete_adress(request, adress_in: CreateAdress):
    adress = get_object_or_404(Address, id = id)
    adress.delete()
    return 200, {"dital": ""}

@address_controller.put('update-adress/{id}', response={
    200: AdressOut,
    400: MessageOut
})
def update_adress(request, id: UUID4, adress_in: CreateAdress):
    adress = get_object_or_404(Address, id = id)
    adress.delete()
    adress = Address(id = id, **adress_in.dict(), user= User.objects.first() )
    adress.save()
    return 200, adress


# @products_controller.get('categories', response=List[CategoryOut])
# def list_categories(request):
#     return Category.objects.all()


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
    return get_object_or_404(City, id = id)


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
    city = get_object_or_404(City, id = id)
    city.name = city_in.name
    city.save()
    return 200, city


@address_controller.delete('cities/{id}', response={
    204: MessageOut
})
def delete_city(request, id: UUID4):
    city = get_object_or_404(City, id = id)
    city.delete()
    return 204, {'detail': 'city Has been Ddeleted successfully'}


@order_controller.get('cart', response={
    200: List[ItemOut],
    404: MessageOut
})
def view_cart(request):
    cart_items = Item.objects.filter(user = User.objects.first(), ordered = False)

    if cart_items:
        return cart_items

    return 404, {'detail': 'Your cart is empty, go shop like crazy!'}


@order_controller.post('add-to-cart', response={
    200: MessageOut,
    # 400: MessageOut
})
def add_update_cart(request, item_in: ItemCreate):
    try:
        item = Item.objects.get(product_id = item_in.product_id, user = User.objects.first(), ordered = False )
        item.item_qty += 1
        item.save()
        return 200, {'detail': 'Added from cart successfully'}

    except Item.DoesNotExist:
        Item.objects.create(**item_in.dict(), user = User.objects.first() )
        return 200, {'detail': 'Item Created into cart successfully'}


@order_controller.post('item/{id}/reduce-quantity', response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, product_id = id, user = User.objects.first(), ordered = False  )
    if item.item_qty <= 1:
        item.delete()
        return 200, {'detail': 'Item deleted!'}

    item.item_qty -= 1
    item.save()
    return 200, {'detail': 'Item quantity reduced successfully!'}


@order_controller.delete('item/{id}', response={
    200: MessageOut
})
def delete_item(request, id: UUID4):
    item = get_object_or_404(Item, id = id, user = User.objects.first() )
    item.delete()
    return 200, {'detail': 'Item deleted!'}

"""
receives the item id and increase the quantity accordingly
/api/orders/item/{id}/increase-quantity
"""
@order_controller.post('item/{id}/increase-quantity', response={
    200: MessageOut,
})
def increase_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, product_id = id, user = User.objects.first(), ordered = False)
    if item.item_qty < 1:
        return 200, {'detail': 'Item Doesnt Exist!'}

    item.item_qty += 1
    item.save()
    return 200, {'detail': 'Item quantity increased successfully!'}

"""
'create-order' endpoint :
-    create a new order
-    set ref_code to a randomly generated 6 alphanumeric value
-    take all current items (ordered=False) and add them to the recently created order
-    set added items (ordered field) to be True
/api/orders/create
"""
def get_item_p_id(query_set):
    field_product_id = []
    for field in query_set:
        try:
            field_item = field.items.values() 
            for i in field_item:
                field_product_id.append(i['product_id'])
        except:
            for item in query_set:
                field_product_id.append(item.product_id)

    return field_product_id

def generate_ref_code():
    ref_code = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(6) )
    return ref_code

@order_controller.post("create", response= {
    200: MessageOut,
    404: MessageOut
})
def create_order(request):

    items = Item.objects.filter(user = User.objects.first(), ordered = False)

    # Check If we have Precreated Order
    if items:
        orders = Order.objects.filter(user = User.objects.first(), ordered = False)
        if orders:
            for item in items:
                for order in orders:
                    order_items = Item.objects.filter(order = order.id)
                    for order_item in order_items:
                        if order_item.product_id == item.product_id != None:
                            order_item.item_qty += item.item_qty
                            order_item.save()
                            items_ = Item.objects.filter(id = item.id)
                            items_.delete()

                order.total = order.order_total
                order.save()
            items = Item.objects.filter(user = User.objects.first(), ordered = False)
            if items:
                order = Order.objects.get(user = User.objects.first(), ordered = False)
                order.items.add(*items)
                order.total = order.order_total

                order.save()
                items.update(ordered = True)

            return 200, {"detail":f"Order with ID: {order.id}, Has been Ubdated "}

        # create New Order
        order = Order(user = User.objects.first(),
                    status = OrderStatus.objects.get(is_default = True),
                    ref_code = generate_ref_code(), ordered = False )

        order.save()

        order.items.add(*items)
        order.total = order.order_total

        order.save()
        items.update(ordered = True)

        return 200, {"detail":f"Order Has been Created with ID: {order.id}"}
    return 404, {"detail": "No Items Found"}

@order_controller.get("view-order", response={
    200: List[OrderOut],
    404: MessageOut
})
def view_order(request):
    order = Order.objects.filter(user = User.objects.first(), ordered = False)

    if order:
        return 200, order.all()

    return 404, {"detail": "No Items Found"}

@order_controller.delete("delet-order", response={
    200: MessageOut,
    404: MessageOut
})
def delet_order(request):
    order = Order.objects.filter(user = User.objects.first(), ordered = False)

    if Order:
        order.delete()
        return 200, {"detail": "Order Deleted"}        

    return 404, {"detail": "No Items Found"}


"""
checkout:
    if this user has an active order
    add address
    accept note
    update the status
    mark order.ordered field as True
"""
@checkout_controller.put("checkout", response={
    200: MessageOut,
    404: MessageOut
})
def checkout(request, order_in: OrderShemaCreat):
    order = Order.objects.filter(user = User.objects.first(), ordered = False)

    if order:
        order.update(address = order_in.address_id, note = order_in.note,
                    ordered = True, status = OrderStatus.objects.get(title = "PROCESSING") )

        return 200, {"detail": "Your Order Now been Processed"}

    return 404, {"detail": "No Order Found"}


@checkout_controller.get("view-processing-order", response={
    200: List[OrderOut],
    404: MessageOut
})
def view_processing_order(request):
    order = Order.objects.filter(user = User.objects.first(), ordered = True)

    if order:
        return 200, order.all()

    return 404, {"detail": "No Items Found"}
