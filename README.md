# GIZ Task 3 - COMMERCE

Task resolution process:

* Fork the repo
* Clone the forked repo to your local machine
* Resolve the task
* Commit your solution
* Push to GitHub
* create a pull request


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