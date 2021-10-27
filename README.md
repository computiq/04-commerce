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




# ARCHIVED TASKS


# Task 3:

This is an intermediary task, you will have to complete the task to move to the next one.

## create the following API endpoints

* return all products, you have to query the database somehow like for example: `Product.objects.all()`, then return the result QuerySet as a dictionary so Django-Ninja can serialize it to JSON.

```http request
GET /api/products
Content-Type: application/json
```

* return all addresses, so you have to query the database to return all addresses: `Address.objects.all()`, then like in `products` endpoint, return a dictionary.

```http request
GET /api/addresses
Content-Type: application/json
```

**Bonus task:**

Instead of returning the related models as an ID, which is the default behaviour, you should return the related model data!

**Hint:** If you apply what you learned until now, you can solve the tasks, including the bonus task! Think well!

**Note:** 
* You can refer to Django docs, Django-Ninja docs, online research, or any cheating/copy-paste method you prefer ;)
* You can use what ever tools comfortable, packages, third party libraries, etc...

