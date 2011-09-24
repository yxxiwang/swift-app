#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-09-20 16:16
# Filename: workspace/swift_app/login_form.py
# Description:
#****************************************************
from django import forms

class Login_Form(forms.Form):
    username = forms.CharField(max_length=20, label='用户名')
    password = forms.CharField(max_length=16,widget=forms.PasswordInput,
            label='密码')


class Register_Form(forms.Form):
    username = forms.CharField(max_length=20, label='用户名')
    password = forms.CharField(max_length=16, widget=forms.PasswordInput,
            label='密码')
    password_again = forms.EmailField(max_length=16, widget=forms.PasswordInput,
            label='重复密码')
    email = forms.CharField(max_length=20, label='邮箱')
