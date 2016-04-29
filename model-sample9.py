# -*- coding:utf-8 -*-

"""
filtering by inner join
"""

# -*- coding:utf-8 -*-
import django
from django.db import models
from django.conf import settings
from django.db import connections
from django.core.management.color import no_style


settings.configure(
    DEBUG=True,
    DATABASES={"default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:"
    }},
    INSTALLED_APPS=[__name__]
)

django.setup()


def create_table(model):
    connection = connections['default']
    if hasattr(connection, "schema_editor"):
        with connection.schema_editor() as schema_editor:
            schema_editor.create_model(model)
    else:
        cursor = connection.cursor()
        sql, references = connection.creation.sql_create_model(model, no_style())
        for statement in sql:
            cursor.execute(statement)

        for f in model._meta.many_to_many:
            create_table(f.rel.through)


class Item(models.Model):
    name = models.CharField(max_length=32, default="foo", blank=False)

    class Meta:
        app_label = __name__


class Review(models.Model):
    name = models.CharField(max_length=32, default="about foo", blank=False)
    item = models.OneToOneField(Item, null=True)

    class Meta:
        app_label = __name__


if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG)
    django.setup()

    create_table(Item)
    create_table(Review)

    item = Item(name="potion")
    item.save()
    review = Review(item=item, name="about potion")
    review.save()
    item = Item(name="potion2")
    item.save()
    item = Item(name="potion3")
    item.save()
    review = Review(item=item, name="about potion3")
    review.save()

    print(Item.objects.filter(review__isnull=False).count())
