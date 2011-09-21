#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-09-21 19:59
# Filename: workspace/swift_app/utils.py
# Description:
#****************************************************
from swift.common import client

FILE_PATH = 'temp'

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

def get_container_list():
    auth_url, auth_token = file(FILE_PATH).read().split()
    item_list = client.get_account(auth_url, auth_token)[1]
    container_list = []
    for item in item_list:
        container_list.append(Container(item['bytes'], item['count'],
            item['name']))
    return container_list

def get_object_list(container):
    auth_url, auth_token = file(FILE_PATH).read().split()
    item_list = client.get_container(auth_url, auth_token, container)[1]
    object_list = []
    for item in item_list:
        object_list.append(Object(item['bytes']
            ,item['last_modified'], item['name']))
    return object_list


if __name__ == '__main__':
    l = get_object_list('bin')
    for i in l:
        print i.get_name()
