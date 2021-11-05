# GIZ Task 3 - COMMERCE

Task resolution process:

* Fork the repo
* Clone the forked repo to your local machine
* Resolve the task
* Commit your solution
* Push to GitHub
* create a pull request

# Task 4

This task in complimentary task for the ongoing project (COMMERCE).
Note: don't forget to `makemigrations` and `migrate`

## implement the following API endpoints

* receives the item id and increase the quantity accordingly
* this endpoint is extremely similar to the reduce-quantity endpoint

```http request
/api/orders/item/{id}/increase-quantity
```

* create a create-order endpoint
* this endpoint should satisfy the following
  * create a new order
  * set ref_code to a randomly generated 6 alphanumeric value
  * take all current items (ordered=False) and add them to the recently created order
  * set added items (ordered field) to be True

```http request
/api/orders/create
```

* finish the addresses CRUD operations

```http request
/api/addresses
```

* create the checkout endpoint
  * you should be able to add an optional note
  * you should be able to add an address to the order
  * set (ordered field) to True, thus the order becomes sealed
  * change order status accordingly

```http request
/api/orders/checkout
```

## Bonus - (Rabab-Challenge 😈)

* the above API endpoints should satisfy the following
  * adding items to the cart are separate from the previous order items
  * check if you have an active order, then the create-order endpoint will check for the matching items (i.e. if you have items in your active order that matches the items in the cart) and instead of adding them to the order, just merge them (add the quantities)
  * you can only have one **active** order

# Workflow

* user lists the products
  * user can filter and search based on a specific criteria
* user clicks on (add to cart) and specify the qty
  * item is created (cart item)
  * user can increase the qty
  * user can decrease the qty
  * user can delete the item
* user can order (create-order)
* user can add his address (multip)
  * user can update address
  * user can delete address
* user can checkout (checkout)

## create order

* add items and mark (ordered) field as True
* add ref_number
* add NEW status
* calculate the total

## checkout

* if this user has an active order
* add address
* accept note
* update the status
* mark order.ordered field as True

## addresses

* create addresses schema
* create crud operations

<br/>
<br/>

# Zubaidah's TODO

* [x] `Item Model` =>  increse-quantity endpoint

```http request
/api/orders/item/{id}/increase-quantity
```

* [x] `Address Model` => CRUD operations

```http request
/api/addresses
```

* [ ] `Order Model` => checkout endpoint

```http request
/api/orders/checkout
```

* [ ] Bonus
