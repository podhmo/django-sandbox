# -*- coding:utf-8 -*-
import logging
logger = logging.getLogger(__name__)
import contextlib
from django import forms
from django.conf import settings

import django
settings.configure()
django.setup()


class M(object):
    def input(self, v):
        print("input data: {}".format(v))

    def output(self, v, message=""):
        print("output data: {}".format(v))
        if message:
            print("  # {}".format(message))

    def validate(self, form):
        status = form.is_valid()
        print("validation: {}".format(status))
        if not status:
            print("errors: {}".format(dict(form.errors)))


@contextlib.contextmanager
def section(message):
    print("----------------------------------------")
    print(message)
    print("----------------------------------------")
    yield M()


class UserForm(forms.Form):
    name = forms.CharField(label="name", required=False, min_length=4)
    age = forms.IntegerField(label="age", required=True)

with section("one value") as m:
    input_data = {}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data, "empty data")


with section("one value2") as m:
    input_data = {"name": "foobar", "age": "10"}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data, "convert string -> int")


with section("one value3") as m:
    input_data = {"name": "foobar", "age": "10@"}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data, "invalid value is not stored")


with section("one value4") as m:
    input_data = {"name": "foobar", "age": "10"}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data)


class RegisterForm(forms.Form):
    name = forms.CharField(label="name", required=True)
    password = forms.CharField(label="password", required=True)
    re_password = forms.CharField(label="re_password", required=True)

    def clean(self):
        super(RegisterForm, self).clean()
        cdata = self.cleaned_data
        # invalid value is not stored. so...
        if cdata.get("password") and cdata.get("re_password"):
            if cdata["password"] != cdata["re_password"]:
                raise forms.ValidationError("invalid")
        return cdata


with section("first implementation") as m:
    input_data = {"name": "foo", "password": "bar", "re_password": "bar"}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data, "empty data")


class RegisterForm(forms.Form):
    name = forms.CharField(label="name", required=True)
    password = forms.CharField(label="password", required=True)
    re_password = forms.CharField(label="re_password", required=True)

    def clean(self):
        cdata = super(RegisterForm, self).clean()
        if not any(self.errors):
            return cdata
        # format check is ok, absolutely.
        if cdata["password"] != cdata["re_password"]:
            raise forms.ValidationError("invalid")
        return cdata


with section("first implementation") as m:
    input_data = {"name": "foo", "password": "bar", "re_password": "bar"}
    m.input(input_data)
    form = UserForm(input_data)
    m.validate(form)
    m.output(form.cleaned_data, "empty data")
