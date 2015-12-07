# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms
from django.http.request import QueryDict


class XForm(forms.Form):
    x = forms.MultipleChoiceField(choices=[(str(i), str(i)) for i in range(10)])


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()
    # form
    params = QueryDict("x=0&x=1&x=2&x=4")
    print(params)
    form = XForm(params)
    print(form.is_valid())
    print(dict(form.errors))
    print(form.cleaned_data)

# <QueryDict: {u'x': [u'0', u'1', u'2', u'4']}>
# True
# {}
# {'x': [u'0', u'1', u'2', u'4']}
