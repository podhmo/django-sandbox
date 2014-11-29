# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PersonForm(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)
    birth = forms.DateTimeField(required=False)
    death = forms.DateTimeField(required=False)

    def clean(self):
        super(PersonForm, self).clean()
        if any(self.errors):
            return

        if self.cleaned_data["birth"] and self.cleaned_data["death"]:
            if self.cleaned_data["birth"] > self.cleaned_data["death"]:
                # raise forms.ValidationError("oops")
                self.add_error("birth", "must be birth < death")


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # success
    params = {"name": "foo", "age": "10",
              "birth": "2010-10-01 01:01:01",
              "death": "2000-10-01 01:01:01",
    }
    form = PersonForm(params)

    assert form.is_valid() is False
    print(form.cleaned_data)
    print(dict(form.errors))

# {'death': datetime.datetime(2000, 10, 1, 1, 1, 1), 'name': 'foo', 'age': 10}
# {'birth': ['must be birth < death']}

