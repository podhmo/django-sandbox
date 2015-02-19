# -*- coding:utf-8 -*-
from django.forms.formsets import formset_factory
from django import forms
import logging
logger = logging.getLogger(__name__)


class PersonForm(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)
    birth = forms.DateTimeField(required=False)
    death = forms.DateTimeField(required=False)


class PersonWarnForm(forms.Form):
    name = forms.CharField(label=u"名前")
    age = forms.IntegerField(label=u"年齢", required=False)
    birth = forms.DateTimeField(required=False)
    death = forms.DateTimeField(required=False)

    def clean(self):
        super(PersonWarnForm, self).clean()
        if any(self.errors):
            return

        if self.cleaned_data["birth"] and self.cleaned_data["death"]:
            if self.cleaned_data["birth"] > self.cleaned_data["death"]:
                # raise forms.ValidationError("oops")
                self.add_error("birth", "must be birth < death")


class HasWarningsFormLike(object):
    def __init__(self, form, warn_form):
        self.form = form
        self.warn_form = warn_form
        self._is_validated = False

    def is_valid(self):
        self.warn_form.is_valid()
        status = self.form.is_valid()
        self._is_validated = True
        return status

    def _constraint(self):
        if not self._is_validated:
            raise RuntimeError("is_valid() is not called")

    @property
    def warnings(self):
        self._constraint()
        return self.warn_form.errors

    @property
    def errors(self):
        self._constraint()
        return self.form.errors

    @property
    def cleaned_data(self):
        self._constraint()
        return self.form.cleaned_data


class PersonFormSetBuilder(object):
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def build(self):
        formset = formset_factory(PersonForm)(*self.args, **self.kwargs)
        warn_formset = formset_factory(PersonWarnForm)(*self.args, **self.kwargs)
        return HasWarningsFormLike(formset, warn_formset)

if __name__ == "__main__":
    from django.conf import settings
    import django
    settings.configure()
    django.setup()

    # # success
    # params = {
    #     "name": "foo", "age": "10",
    #     "birth": "2010-10-01 01:01:01",
    #     "death": "2000-10-01 01:01:01",
    # }
    # form = PersonFormWrapper(params)

    # assert form.is_valid() is True
    # print(form.cleaned_data)
    # print(dict(form.warnings))
    # print(dict(form.errors))

    print("formset------------")
    params = {
        "form-TOTAL_FORMS": "1",
        "form-INITIAL_FORMS": "0",
        "form-MAX_NUM_FORMS": "1",
        "form-0-name": "foo",
        "form-0-age": "10",
        "form-0-birth": "2010-10-01 01:01:01",
        "form-0-death": "2000-10-01 01:01:01",

    }
    b = PersonFormSetBuilder(params)
    formset = b.build()
    assert formset.is_valid() is True
    print(formset.cleaned_data)
    print(formset.warnings)
    print(formset.errors)

