#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-09-20 16:57
# Filename: workspace/swift_app/views.py
# Description:
#****************************************************
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.contrib import auth
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
        con = utils.Connection(username,password)
        auth_url, auth_token = con.get_auth()
        open(utils.FILE_PATH,'w').writelines([auth_url+'\n',auth_token])
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
    container_list = utils.get_container_list()
    return render_to_response('control_panel.html',
            {'container_list':container_list})

def logout(request):
    auth.logout(request)
    return HttpResponseRedirect('/login')
