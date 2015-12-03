# -*- coding:utf-8 -*-
from django import forms


class UnreuiredChoicesForm(forms.Form):
    candidate = forms.ChoiceField(required=False, choices=[(str(x), str(x)) for x in range(1, 10)])

    def clean_candidate(self):
        value = self.cleaned_data.get("candidate")
        if value:
            return value
        return "1"

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # form
    print("----------------------------------------")
    params = {"candidate": ""}
    form = UnreuiredChoicesForm(params)
    print(form.is_valid())
    print(dict(form.errors))
    print(form.cleaned_data)

    print("----------------------------------------")
    params = {}
    form = UnreuiredChoicesForm(params)
    print(form.is_valid())
    print(dict(form.errors))
    print(form.cleaned_data)

    print("----------------------------------------")
    params = {"candidate": "3"}
    form = UnreuiredChoicesForm(params)
    print(form.is_valid())
    print(dict(form.errors))
    print(form.cleaned_data)
