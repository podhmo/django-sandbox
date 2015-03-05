# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PersonForm(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)

    def clean_age(self):
        age = self.cleaned_data.get("age")
        if age is not None:
            return abs(age)
        return age


class PersonForm2(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)

    def clean(self):
        super(PersonForm2, self).clean()
        if any(self.errors):
            return self.cleaned_data

        age = self.cleaned_data.get("age")
        if age is not None:
            self.cleaned_data["age"] = abs(age)
        return self.cleaned_data


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # form
    params = {"name": "foo", "age": -10}
    form = PersonForm(params)
    print(form.is_valid())
    print(form.errors)
    print(form.cleaned_data)
    # {'name': 'foo', 'age': 10}

    # form2
    params = {"name": "foo", "age": -10}
    form = PersonForm2(params)
    print(form.is_valid())
    print(form.errors)
    print(form.cleaned_data)
    # {'name': 'foo', 'age': 10}
