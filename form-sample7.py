# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PointForm(forms.Form):
    x = forms.BooleanField()
    y = forms.BooleanField(required=False)
    a = forms.BooleanField()
    b = forms.BooleanField(required=False)


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # form
    params = {"x": "false", "y": "false", "a": "true", "b": "true"}
    form = PointForm(params)
    print(form.is_valid())
    print(dict(form.errors))
    print(form.cleaned_data)

# False
# {'x': ['This field is required.']}
# {'a': True, 'y': False, 'b': True}

