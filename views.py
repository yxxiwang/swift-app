#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-09-22 17:33
# Filename: workspace/swift_app/views.py
# Description: 视图函数
#****************************************************
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib import auth
from swift.common import client
from swift_app.login_form import Login_Form
from swift_app import utils

def login(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/already-logged')
    if request.method == 'POST':
        form = Login_Form(request.POST)
        if not form.is_valid():
            return render_to_response('login.html',{'form':form})
        username = request.POST.get('username','')
        password = request.POST.get('password', '')
        con = client.Connection(utils.URL,username,password)
        try:
            auth_url, auth_token = con.get_auth()
        except Exception, e:
            if e[0]==111:
                form = Login_Form()
                return render_to_response('login.html', {'form':form,'swift_no_start':True})
        utils.auth_url = auth_url
        utils.auth_token = auth_token
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request,user)
            return HttpResponseRedirect('/control-panel')
        else:
            return render_to_response('login.html',
                    {'form':Login_Form(),'incorrect':True})
    form = Login_Form()
    return render_to_response('login.html',{'form':form})

@login_required
def already_logged(request):
    if request.user.is_authenticated():
        return render_to_response('already_logged.html')
    else:
        return HttpResponseRedirect('login')

@login_required
def control_panel(request):
    """控制面板"""
    container_list = utils.get_container_list()
    return render_to_response('control_panel.html',
            {'container_list':container_list})

@login_required
def operation(request):
    """对swift的后台操作"""
    q = request.GET.get('q','')
    name = request.GET.get('name','')
    if q=='cc':#创建container
        try:
            client.put_container(utils.auth_url, utils.auth_token, name)
        except client.ClientException:
            return HttpResponse('failure')
    elif q=='dc': #删除container
        try:
            client.delete_container(utils.auth_url, utils.auth_token, name)
        except client.ClientException:
            return HttpResponse('failure')
    elif q=='lo': #列出container中的object
        try:
            object_list = utils.get_object_list(name)
            name_list = '\n'.join([obj.get_name() for obj in object_list])
            return HttpResponse(name_list)
        except client.ClientException:
            return HttpResponse('failure')
    return HttpResponse('success')


def logout(request):
    """退出登入"""
    auth.logout(request)
    return HttpResponseRedirect('/login')
