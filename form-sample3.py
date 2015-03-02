# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
from django import forms


class PersonForm(forms.Form):
    fruit = forms.ChoiceField(choices=[("1", "apple"), ("2", "banana")], required=False)


class PersonForm2(forms.Form):
    fruit = forms.CharField(widget=forms.Select(), required=False)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["fruit"].widget.choices = [("1", "apple"), ("2", "banana")]


if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # params = {"fruit": "3"}
    # form = PersonForm(params)
    # print(str(form["fruit"]).replace("</", "\n</"))

    print("----------------------------------------")
    params = {"fruit": "3"}
    form = PersonForm2(params)
    print(str(form["fruit"]).replace("</", "\n</"))
