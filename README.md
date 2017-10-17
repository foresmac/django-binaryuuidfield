# django-binaryuuidfield
A Django model field that uses best practices to optimize UUID primary keys on MySQL.

## Installtion
```bash
pip install django-binaryuuidfield
```

## Usage
```python
from binuuid import BinaryUUIDField
from django.db import models

class MyModel(models.Model):
    id = BinaryUUIDField(primary_key=True)
    name = models.CharField(max_length=128)
    note = models.TextField()
```

## Rationale
Django's [default](https://docs.djangoproject.com/en/1.11/_modules/django/db/models/fields/#BinaryField)
`UUIDField`  uses `CHAR(32)` columns on databases other than Postgres. While this implementation is 
simple and easy to understand, it is space-inefficient and—particularly on MySQL—can have
[important performance ramifications](http://kccoder.com/mysql/uuid-vs-int-insert-performance/) 
when used as a primary key. For this reason, `BinaryUUIDField` uses a `BINARY(16)` column type on 
MySQL, which uses half the space to store the data. Furthermore, by default it uses UUID type 1
with a [re-arranged byte order](http://mysqlserverteam.com/storing-uuid-values-in-mysql-tables/) to 
get the [most efficient](https://www.percona.com/blog/2014/12/19/store-uuid-optimized-way/) storage
space, indexing, and INSERT speed.

