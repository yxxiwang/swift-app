#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-10-08 17:41
# Filename: workspace/swift_app/views.py
# Description: 视图函数
#****************************************************
from django.http import HttpResponseRedirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.servers.basehttp import FileWrapper
from django.shortcuts import render_to_response
from django.contrib import auth
from swift.common import client
from swift_app.forms import Login_Form, Register_Form
from swift_app import utils
import os

def login(request):
    """登入页面"""
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
            utils.auth_url = auth_url
            utils.auth_token = auth_token
        except Exception, e:
            if e[0]==111:
                form = Login_Form()
                return render_to_response('login.html', {'form':form,'swift_no_start':True})
        user = auth.authenticate(username=username, password=password)
        if user is not None and user.is_active:
            auth.login(request,user)
            return HttpResponseRedirect('/control-panel')
        else:
            return render_to_response('login.html',
                    {'form':Login_Form(),'incorrect':True})
    form = Login_Form()
    return render_to_response('login.html',{'form':form})

def register(request):
    if request.method == 'POST':
        form = Register_Form(request.POST)
        if not form.is_valid():
            return render_to_response('register.html',{'form':form})
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        email = request.POST.get('email','')
        if User.objects.filter(username=username):
            return render_to_response('register.html',{'form':form,'msg':'该用户已存在'})
        user = User.objects.create_user(username=username,password=password,email=email)
        user.save()
        return HttpResponseRedirect('/login')
    form = Register_Form()
    return render_to_response('register.html',{'form':form})

@login_required
def already_logged(request):
    if request.user.is_authenticated():
        return render_to_response('already_logged.html')
    else:
        return HttpResponseRedirect('login')

@login_required
def control_panel(request):
    """控制面板"""
    user = request.user.username.split(':')[1]
    account = request.user.username.split(':')[0]
    container_list = utils.get_container_list()
    return render_to_response('control_panel.html',
            {'container_list':container_list,
                'user':user,'account':account})

@login_required
def operation(request):
    """对swift的后台操作,ajax调用"""
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
            name_list = '^'.join([obj.get_name() for obj in object_list])
            time_list = '^'.join([obj.get_last_modified() for obj in object_list])
            size_list = '^'.join([str(obj.get_size()) for obj in object_list])
            obj_list = '\n'.join([name_list,time_list,size_list])
            return HttpResponse(obj_list)
        except client.ClientException:
            return HttpResponse('failure')
    elif q=='do': #删除object
        objs = name.split('^')
        container_name = objs[-1:][0]
        objs = objs[:-1]
        for obj in objs:
            try:
                client.delete_object(utils.auth_url,utils.auth_token,
                        container_name, obj)
            except client.ClientException:
                return HttpResponse('failure')
        client.put_container(utils.auth_url,utils.auth_token,
                container_name)
    elif q=='dl': #下载object
        objs = name.split('^')
        container_name = objs[-1:][0]
        objs = objs[:-1]
        if len(objs)==1:
            response = utils.download_single_file(container_name, objs[0])
            return response
    elif q=='ic':#查询container信息
        try:
            result = client.get_container(utils.auth_url,utils.auth_token,
                    name)[0].get('x-container-read','')
            if result:
                result = utils.auth_url+'/'
            return HttpResponse(result)
        except client.ClientException:
            return HttpResponse('failure')
    elif q=='sc':#共享container
        try:
            client.post_container(utils.auth_url,utils.auth_token,
                    name,headers={'X-Container-Read':'.r:*'})
            return HttpResponse(utils.auth_url+'/')
        except client.ClientException:
            return HttpResponse('failure')
    elif q=='pc':#使container变为私有
        try:
            client.post_container(utils.auth_url,utils.auth_token,
                    name,headers={'X-Container-Read':''})
            return HttpResponse('success')
        except client.ClientException:
            return HttpResponse('failure')
    return HttpResponse('success')

@login_required
def download(request):
    """下载文件"""
    name = request.GET.get('name','')
    objs = name.split('^')
    container_name = objs[-1:][0]
    objs = objs[:-1]
    if len(objs)==1:
    #只有一个文件要下载的情况
        result = utils.download_single_file(container_name, objs[0])
        if result=='failure':
            return HttpResponse(result)
        wrapper = FileWrapper(open(result,'rb'))
        response = HttpResponse(wrapper,mimetype='application/octet-stream')
        response['Content-Length'] = os.path.getsize(result)
        response['Content-Disposition'] = 'attachment; filename=%s' % objs[0].encode('utf-8')
        return response
    else:
    #有多个文件要下载的情况
        result = utils.download_multi_files(container_name, objs)
        if result == 'failure':
            return HttpResponse(result)
        wrapper = FileWrapper(open(result,'rb'))
        response = HttpResponse(wrapper,content_type='application/zip')
        response['Content-Disposition'] = 'attachment; filename=all_in_one.zip'
        return response

@login_required
def preview(request):
    """预览object"""
    items = request.GET.get('name','').split('^')
    container = items[-1:][0]
    objs = items[:-1]
    if len(objs)==1:
        result = utils.download_single_file(container,objs[0])
        if result == 'failure':
            return HttpResponse(result)
        if objs[0].endswith('txt'):
            return HttpResponse(open(result).read(1000))
        return HttpResponse(objs[0])

@login_required
def upload(request):
    """上传文件"""
    illegal_char = ['+','^','#','&',' ']
    file_obj = request.FILES.get('file',None)
    container_name = request.POST.get('container_name','')
    name = ''
    for c in file_obj.name:
        if c in illegal_char:
            name+= '_'
        else:
            name+= c
    file_obj.name = name
    temp_file_path = os.path.join(utils.temp_dir, 'temp_up')
    temp_file = open(temp_file_path,'wb')
    for chunk in file_obj.chunks():
        temp_file.write(chunk)
    temp_file.close()
    client.put_object(utils.auth_url, utils.auth_token,
            container_name, file_obj.name, open(temp_file_path,'rb'))
    client.put_container(utils.auth_url, utils.auth_token,
            container_name)
    os.remove(temp_file_path)
    return HttpResponseRedirect('/control-panel')

@login_required
def move(request):
    """移动或复制object"""
    src_con = request.POST.get('src_con','')
    des_con = request.POST.get('des_con','')
    obj_list = request.POST.get('obj_list','')
    objs = obj_list.split('^')
    operate = request.POST.get('operate','')
    flag = False
    if operate=='move':
        flag = True
    for obj in objs:
        src = '/'+src_con+'/'+obj
        des = '/'+des_con+'/'+obj
        utils.copy_or_move(src, des, flag)
    return HttpResponseRedirect('/control-panel')


def logout(request):
    """退出登入"""
    auth.logout(request)
    return HttpResponseRedirect('/login')
