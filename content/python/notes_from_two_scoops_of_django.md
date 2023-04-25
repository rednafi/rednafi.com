---
title: Notes from two scoops of Django
date: 2022-01-18
tags:
    - Python
    - Django
draft: true
---

## Project structure

### Flat is better than nested

Unless you're creating a resuable Django app, it's better to flatten the nested structure created by Django's `startproject` and `startapp` commands. If you run the follwing command:

```
django-admin startproject foo && cd foo && python manage.py foo_app
```

you'll end up with the following files in your project folder:


```
foo
├── foo
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── foo_app
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

The top folder `foo` isn't necessary unless you're creating a resuable package. Moreover, it hides the project's structure behind a gratuitous layer. You can flatten this and turn it into the following directory structure without any additional work. The flattened version of the above structure will look like this:

```
.
├── foo
│   ├── __init__.py
│   ├── asgi.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── foo_app
│   ├── migrations
│   │   └── __init__.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── tests.py
│   └── views.py
└── manage.py
```

### Naming apps

* When possible keep to single word names like flavors, **animals**, **blog**, **polls**, **dreams**, **estimates**,
and **finances**.

* As a general rule, the app’s name should be a plural version of the app’s main model

### Ruby on rails style app structure

Putting business logic of an app in dedicated modules is better than putting them in the `models.py` or `views.py` modules. This way, you can achieve loose coupling between different apps. Also, it'll help you keep you models and views leaner.

To do so, place your business logic in
`service.py` and `selectors.py`. Your strurcture should look as follows:

```
foo_app/
├── migrations
│   └── __init__.py
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── selectors.py  # Service layer location for business logic
├── services.py  # Service layer location for queries
├── tests.py
└── views.py
```

Here, by business logic I mean, functions or classes to create, update and delete Model objects.

## Settings & requirements files

### Settings module

* Don't use a separate `settings.py` file for local development, this adds additional confusion.

* Don't push `SECRET_KEY` to your VCS.

* Don't opt-in for an app architecture with multiple `settings.py` files unless you absolutely have to. If you need to use multiple settings files, follow DRY principle.

    Keep your base settings in a file named, `foo/base_settings.py` and other settings file like `foo/settings_local.py` or `foo/settings_prod.py` can import setting-variables from `foo/base_settings.py` file.

    You'll run a Django command with a specific setting as follows:

    ```
    python manage.py runserver --settings=foo.settings_local
    ```

    or,

    ```
    python manage.py runserver --settings=foo.settings_prod
    ```

* Seperate configuration from code. Adopt [12 factor app](https://12factor.net/config) philosophies to achieve that.

* Don't import Django components in your settings modules.

* Don't hardcode paths in the settings modules. Consider using the `pathlib` module to avoid that.

### Requirements file

* Pin you dependencies to the exact version.

* Seperate your top-level and transient dependencies. You can use tools like [pip-tools](https://github.com/jazzband/pip-tools) or [poetry](https://github.com/python-poetry/poetry) to achieve that.

## Database

* Don't use Sqlite database in development, unless you're using that in production as well. Adopting a database like PostgreSQL can give you access to better concurrency concurrency management and a stronger type system. Prefer to develop in the same DB that you'll be running in production.

## Models

### Model inheritance

* Take advantage of **abstract base class inheritance** when it makes sense. In this case, no table is created for the **parent** model. A table is created for the **child** model only. This doesn't suffer from the overhead of extra tables and joins that are incurred from **multi-table inheritance**.

* Avoid **multi-table inheritance** where Django creates table for both parent and child models. This adds substantial overhead since each query on a child table requires joins with all parent tables.

* Instead of multi-table inheritance,
use explicit `OneToOneFields` and `ForeignKeys` between models so you can control when joins are traversed.

* Use inheritance to timestamp all of your models. Consider this example:

    ```python
    from django.db import models


    class AuditLogModel(models.Models):
        """
        An abstract base class model that provides self
        updating `created_at` and `updated_at` fields.
        """

        created_at = models.DateTimeField(auto_now_add=True)
        updated_at = models.DateTimeField(auto_now=True)

        class Meta:
            abstract = True


    # Use the models as follows.


    class FooModel(AuditLogModel):
        title = models.CharField(max_length=200)
        ...
    ```

    Here, the `FooModel` will inherit `created_at` and `updated_at` fields from the `AuditLogModel`. The `abstract=True` field in the `Meta` class makes sure that no tables are created for the `AuditLogModel`.

### Migrations

* Backup your data before running the `migrate` command.
* Use `sqlmigrate` command to inspect the SQL instructions before running complex migrations.
