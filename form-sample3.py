# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PersonForm(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)

    # テストだるい
    # def clean_age(self):
    #     age = self.cleaned_data.get("age")
    #     if age is not None:
    #         if age < 0:
    #             raise forms.ValidationError("oops")

    # form.add_errorもcleaned_dataに依存
    # def validation_age(self, data):
    #     age = data.get("age")
    #     if age is not None:
    #         if age < 0:
    #             self.add_error("age", "oops")

    def validation_age(self, data):
        age = data.get("age")
        if age is not None:
            if age < 0:
                raise forms.ValidationError("oops", code="age")

    def clean(self):
        super(PersonForm, self).clean()
        if any(self.errors):
            return self.cleaned_data

        self.validate_age(self.cleaned_data)
        return self.cleaned_data


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # success
    params = {"name": "foo", "age": -10}
    form = PersonForm()
    form.validation_age(params)
