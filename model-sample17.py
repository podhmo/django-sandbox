# -*- coding:utf-8 -*-

"""
totaling
"""
import django
from django.db import models
from django.conf import settings
from django.db import connections


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
    with connection.schema_editor() as schema_editor:
        schema_editor.create_model(model)


class Person(models.Model):
    name = models.CharField(max_length=32, default="a", blank=False)
    age = models.PositiveIntegerField(null=False)
    gender = models.SmallIntegerField(null=True)  # 1 = female, 2 = male

    class Meta:
        app_label = __name__


def extra_select(qs, **kwargs):
    qs = qs.all()
    for name, col in kwargs.items():
        qs.query.values_select.append(name)
        qs.query.add_select(col)
    return qs


if __name__ == "__main__":
    create_table(Person)

    FEMALE = 1
    MALE = 2
    import logging
    for name in ['django.db.backends']:
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(logging.StreamHandler())

    Person.objects.bulk_create(
        [Person(name="foo{}".format(i), age=i, gender=FEMALE)for i in range(1, 40)]
    )
    Person.objects.bulk_create(
        [Person(name="bar{}".format(i), age=i, gender=MALE)for i in range(1, 30)]
    )
    Person.objects.bulk_create(
        [Person(name="boo{}".format(i), age=i)for i in range(1, 20)]
    )

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    from django.db.models import Count, Case, When, Value, Q
    # group by with count
    qs = Person.objects.all()
    # sub query
    case = Case(
        When(age__lt=10, then=Value(0)),
        When(Q(age__gte=10, age__lt=20), then=Value(1)),
        When(Q(age__gte=20, age__lt=30), then=Value(2)),
        When(Q(age__gte=30, age__lt=40), then=Value(3)),
        When(Q(age__gte=40, age__lt=50), then=Value(4)),
        default=Value(-1),
        output_field=models.IntegerField()
    )
    qs = qs.annotate(rank=case)
    qs = qs.values("rank")
    qs.query.set_group_by()
    qs = extra_select(qs, c=Count("*"))
    print(qs.query)
    print(list(qs))

"""
SELECT
  COUNT(*),
  CASE
    WHEN "__main___person"."age" < 10 THEN 0
    WHEN ("__main___person"."age" < 20 AND "__main___person"."age" >= 10) THEN 1
    WHEN ("__main___person"."age" < 30 AND "__main___person"."age" >= 20) THEN 2
    WHEN ("__main___person"."age" < 40 AND "__main___person"."age" >= 30) THEN 3
    WHEN ("__main___person"."age" < 50 AND "__main___person"."age" >= 40) THEN 4
    ELSE -1
  END AS "rank"
FROM "__main___person"
GROUP BY
  CASE
    WHEN "__main___person"."age" < 10 THEN 0
    WHEN ("__main___person"."age" < 20 AND "__main___person"."age" >= 10) THEN 1
    WHEN ("__main___person"."age" < 30 AND "__main___person"."age" >= 20) THEN 2
    WHEN ("__main___person"."age" < 40 AND "__main___person"."age" >= 30) THEN 3
    WHEN ("__main___person"."age" < 50 AND "__main___person"."age" >= 40) THEN 4
    ELSE -1
  END
"""
