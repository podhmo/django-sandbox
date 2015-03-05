# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PointForm(forms.Form):
    value = forms.CharField(required=True)
    maybevalue = forms.CharField(required=False)

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # success
    params = {"value": "a"}
    form = PointForm(params)

    assert form.is_valid() is True
    print(form.cleaned_data)  # => {'maybevalue': '', 'value': 'a'}
