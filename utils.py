#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-10-10 14:18
# Filename: workspace/swift_app/utils.py
# Description:一些辅助类和方法
#****************************************************
import os
import urllib2
import zipfile
from swift.common import client

#FILE_PATH = 'temp'
URL = 'http://127.0.0.1:8080/auth/v1.0'
auth_url = ''
auth_token = ''
temp_dir = os.path.join(os.path.dirname(__file__),'temp')

class Container(object):
    def __init__(self,size,obj_count,name):
        """
        :param size: container大小(单位：bytes)
        :param obj_count: container内object的个数
        :param name: container的名字
        """
        self.size = size
        self.obj_count = obj_count
        self.name = name

    def get_name(self):
        return self.name

    def get_size(self):
        return self.size

    def get_obj_count(self):
        return self.obj_count

    def get_display_text(self):
        text = '%s(%s)'%(self.get_name(),self.get_obj_count())
        return text

class Object(object):
    """
    :param size:  object大小
    :param last_modified: 最后修改时间
    :param name: object名字
    """
    def __init__(self, size, last_modified, name):
        self.size = size
        self.last_modified = last_modified
        self.name = name

    def get_size(self):
        return self.size

    def get_last_modified(self):
        return self.last_modified

    def get_name(self):
        return self.name

def clear_temp_dir():
    """清理临时文件夹"""
    if len(os.listdir(temp_dir))>10:
        for f in os.listdir(temp_dir):
            os.remove(os.path.join(temp_dir,f))

def get_container_list():
    item_list = client.get_account(auth_url, auth_token)[1]
    container_list = []
    for item in item_list:
        container_list.append(Container(item['bytes'], item['count'],
            item['name']))
    return container_list

def get_object_list(container):
    item_list = client.get_container(auth_url, auth_token, container)[1]
    object_list = []
    for item in item_list:
        object_list.append(Object(item['bytes']
            ,item['last_modified'], item['name']))
    return object_list

def download_single_file(container_name, obj_name):
    """下载单个object"""
    clear_temp_dir()
    try:
        content = client.get_object(auth_url, auth_token,
                container_name, obj_name)[1]
        temp_file_path = os.path.join(temp_dir, obj_name)
        temp = open(temp_file_path, 'wb+')
        temp.write(content)
        temp.close()
        return temp_file_path
    except client.ClientException:
        return 'failure'

def download_multi_files(container_name,objs):
    """将多个objets打包成zip文件下载"""
    clear_temp_dir()
    for f in os.listdir(temp_dir):
        os.remove(os.path.join(temp_dir,f))
    temp_zip_path = os.path.join(temp_dir, 'all_in_one.zip')
    zip = zipfile.ZipFile(temp_zip_path,'w',zipfile.ZIP_DEFLATED)
    for obj in objs:
        try:
            content = client.get_object(auth_url, auth_token,
                    container_name, obj)[1]
        except client.ClientException:
            return 'failure'
        temp_file_path = os.path.join(temp_dir, obj.encode('utf-8'))
        temp = open(temp_file_path, 'wb+')
        temp.write(content)
        temp.close()
        zip.write(temp_file_path, obj)
        os.remove(temp_file_path)
    zip.close()
    return temp_zip_path

def copy_or_move(src, des,flag=False):
    """复制或移动object,flag为True为move，否则为copy"""
    url = auth_url+src
    headers = {'X-Auth-Token':auth_token,'Destination':des.encode('utf-8')}
    req = urllib2.Request(url.encode('utf-8'), headers=headers)
    req.get_method = lambda:'COPY'
    res = urllib2.urlopen(req)
    src_container = src.split('/')[1]
    des_container = des.split('/')[1]
    object = src.split('/')[2]
    if flag:
        client.delete_object(auth_url, auth_token,
                src_container,object)
    client.put_container(auth_url, auth_token, src_container)
    client.put_container(auth_url, auth_token, des_container)
    return res.code


if __name__ == '__main__':
    l = get_object_list('bin')
    for i in l:
        print i.get_name()
