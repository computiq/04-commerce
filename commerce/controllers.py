from typing import List
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import get_object_or_404
from ninja import Router
from pydantic import UUID4
import string
import random
from commerce.models import Address, Order, OrderStatus, Product, Category, City, Vendor, Item
from commerce.schemas import AddressIn, MessageOut, ProductOut, CitiesOut, CitySchema, VendorOut, ItemOut, ItemSchema, ItemCreate,OrderOut , OrderStatusOut,AddressOut


products_controller = Router(tags=['products'])
address_controller = Router(tags=['addresses'])
vendor_controller = Router(tags=['vendors'])
order_controller = Router(tags=['orders'])
checkout_controller = Router(tags=['checkout'])







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
        item = Item.objects.get(product_id=item_in.product_id, user=User.objects.first(),ordered = False)
        item.item_qty += 1
        item.save()
    except Item.DoesNotExist:
        Item.objects.create(**item_in.dict(), user=User.objects.first())

    return 200, {'detail': 'Added to cart successfully'}


@order_controller.post('item/{id}/reduce-quantity', response={
    200: MessageOut,
})
def reduce_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first(),ordered = False)
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
    item = get_object_or_404(Item, id=id, user=User.objects.first(),ordered = False)
    item.delete()

    return 204, {'detail': 'Item deleted!'}





#------------------------------------------------------------------------------------------------------
# My Solution Start From Here

# first =>  endpoint to  receives the item id and increase the quantity accordingly
@order_controller.post('/item/{id}/increase-quantity', response={200: MessageOut,})
def increase_item_quantity(request, id: UUID4):
    item = get_object_or_404(Item, id=id, user=User.objects.first(),ordered = False)
    item.item_qty += 1
    item.save()
    return 200, {'detail': 'item increased successfully'}

# -----------------------------------------------------------------------------------------------------
# second =>  create a new order  
@order_controller.post('/create/', response={200: MessageOut,201: MessageOut})
def create_update_order(request):
    # set ref_code to a randomly generated 6 alphanumeric value
    ref_code = ''.join(random.sample(string.ascii_letters+string.digits,6))
    # get status 
    try :
        get_status = OrderStatus.objects.get(title = "NEW")
    except OrderStatus.DoesNotExist :
        get_status = OrderStatus.objects.create(title = "NEW",is_default = True)

    # take all current items (ordered=False) 
    items_qs = Item.objects.filter(user = User.objects.first(),ordered = False)
    order_qs = Order.objects.filter(user=User.objects.first(),ordered = False)
    items_qs_true = Item.objects.filter(user=User.objects.first(),ordered = True)

    if order_qs.exists():
        order = order_qs.first()
        # add items to the order
        for i in items_qs : 
            for j in items_qs_true:
                if i.product.id == j.product.id :
                    j.item_qty += i.item_qty
                    j.save()
                    i.delete()
                    items_qs.update()
                else :           
                    i.ordered = True
                    i.save()   
        order.items.add(*items_qs)
        order.save()
        return 200, {"detail": "Order Updated Successfully"}
    else:
        for i in items_qs :
            i.ordered = True
            i.save()
        order = Order.objects.create(user=User.objects.first(),status = get_status,ref_code =ref_code,ordered = False)
        order.items.add(*items_qs)
        order.save()
        return 201, {"detail": "Order Created Successfully"}


# ----------------------------------------------------------------------------------------------------------
# Third finish the addresses CRUD operations


# create address
@address_controller.post('/create_address/', response={
    201: MessageOut,
    400: MessageOut
})
def create_address(request, address_in: AddressIn,city_id : UUID4):
    city = City.objects.get(id = city_id)
    address_qs = Address(**address_in.dict(),user = User.objects.first(),city = city)
    address_qs.save()
    return 201, {"detail":"address created succesfully"}

# update address 
@address_controller.put('/update_address/{id}', response={200: AddressOut,400: MessageOut})
def update_address(request, id: UUID4, address_in: AddressIn):
    address = get_object_or_404(Address, id=id)
    for attr, value in address_in.dict().items():
        setattr(address, attr, value)
    address.save()
    return 200,address

# retrive address
@address_controller.get('get_address_by_id/{id}', response={
    200: AddressOut,
    404: MessageOut
})
def get_address_by_id(request, id: UUID4):
    return get_object_or_404(Address, id=id)

# get list addresses 
@address_controller.get('/list_all_addresses/',response={200:List[AddressOut],404 : MessageOut})
def list_addresses(request):
    adresses_qs = Address.objects.all()
    if adresses_qs:
        return adresses_qs

    return 404, {'detail': 'No adresses found'}


# delete address 
@address_controller.delete('delete/{id}', response={204: MessageOut})
def delete_address(request, id: UUID4):
    address = get_object_or_404(Address, id=id)
    address.delete()
    return 204, {'detail': 'deleted address sucessfully'}
 
# --------------------------------------------------------------------------------------
# fourth create checkout
@checkout_controller.post('/create/', response={200: MessageOut, 404: MessageOut})
def checkout(request, address_in: AddressIn, city_name : str, note : str = None):
    # crete city
    city = City.objects.create(name = city_name)
    # create address
    address_qs = Address(**address_in.dict(),user = User.objects.first(),city = city)
    address_qs.save()
    # get Order
    try:
        checkout = Order.objects.get(ordered=False, user= User.objects.first())
    except Order.DoesNotExist:
        return 404 ,{'detail': 'Order Not Found'}
    # get note if exist 
    if note : 
        checkout.note = note

    checkout.status = OrderStatus.objects.get(title = "PROCESSING")
    checkout.total = checkout.order_total
    checkout.ordered = True
    checkout.address = address_qs
    checkout.save()
    return 200, {'detail': 'Checkout Created successfully'}