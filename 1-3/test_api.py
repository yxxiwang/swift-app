#!/usr/bin/python
#coding=utf-8
import urllib
import urllib2
import hashlib

class Swift_Api():
    def __init__(self,username, passwd,auth_url):
        self.username = username
        self.passwd = passwd
        self.auth_url = 'http://127.0.0.1:8080/auth/v1.0'
        self.is_auth = False

    def get_auth(self):
        headers = {'X-Auth-User':self.username,'X-Auth-Key':self.passwd}
        req = urllib2.Request(self.auth_url, headers = headers)
        res = urllib2.urlopen(req)
        self.x_storage_url = res.info().getheader('X-Storage-Url')
        self.x_auth_token = res.info().getheader('X-Auth-Token')
        self.is_auth = True
        return self.x_storage_url, self.x_auth_token

    def get_container_list(self,format=None,limit=None,marker=None):
        """返回account中container的列表
        format:为返回的格式，json或xml
        limit:返回的container的数量限制
        marker:marker是个container,返回在它之后的container
        """
        if not self.is_auth:
            self.get_auth()
        data = {}
        if format:
            data['format'] = format
        if limit:
            data['limit'] = limit
        if marker:
            data['marker'] = marker
        data = urllib.urlencode(data)
        x_storage_url=self.x_storage_url+'?'+data
        req = urllib2.Request(x_storage_url,
                headers={'X-Auth-Token':self.x_auth_token})
        res = urllib2.urlopen(req)
        return res.read()

    def get_object_list(self,container, format=None,limit=None,marker=None,
            prefix=None,path=None):
        """获取container中object的列表
            prefix:返回以prefox开头的object
            path:object所在的伪路径
        """
        if not self.is_auth:
            self.get_auth()
        data = {}
        if format:
            data['format'] = format
        if limit:
            data['limit'] = limit
        if prefix:
            data['prefix'] = prefix
        if path:
            data['path'] = path
        x_storage_url = self.x_storage_url+'/'+container+'?'+urllib.urlencode(data)
        req = urllib2.Request(x_storage_url,
                headers={'X-Auth-Token':self.x_auth_token})
        res = urllib2.urlopen(req)
        return res.read()

    def create_container(self,container,tag=None):
        """建立一个container
        返回201表示创建成功
        返回202表示container已存在
        tag:给container创建的标签，为字典形式
        """
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container
        headers = {'X-Auth-Token':self.x_auth_token}
        if tag:
            for key, value in tag.items():
                headers['X-Container-Meta-%s'%key] = value
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda: 'PUT'
        res = urllib2.urlopen(req)
        return res.read().split(' ')[0]

    def delete_container(self, container):
        """删除一个container，返回204表示成功，404表示container不存在，
        409表示container不空"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container
        headers = {'X-Auth-Token':self.x_auth_token}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'DELETE'
        try:
            urllib2.urlopen(req)
        except urllib2.HTTPError,e:
            return e
        return 204

    def head_container(self, container):
        """获取container的头信息，不存在就返回404 """
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container
        headers = {'X-Auth-Token':self.x_auth_token}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'HEAD'
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError,e:
            return e.code
        return res.info()

    def get_object(self,container, object):
        """获取object,
        返回参数1：响应头信息
        放回参数2：object内容"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container+'/'+object
        headers = {'X-Auth-Token':self.x_auth_token}
        req = urllib2.Request(x_storage_url, headers=headers)
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            return e.code
        return res.info(),res.read()

    def update_object(self,container,object):
        """创建/上传object.
        201创建成功
        411缺少Content-Length
        422 etag值和md5不同"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container+'/'+object
        m = hashlib.md5(object)
        etag = m.hexdigest()
        print etag
        headers = {'X-Auth-Token':self.x_auth_token,
                'Content-Length':0}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'PUT'
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            return e.code
        return res.code

    def delete_object(self,container,object):
        """删除object，204删除成功，404不存在"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container+'/'+object
        headers ={'X-Auth-Token':self.x_auth_token}
        req = urllib2.Request(x_storage_url, headers = headers)
        req.get_method = lambda:'DELETE'
        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, e:
            return e.code
        self.create_container(container)
        return res.code

    def copy_object(self, src, des):
        """将一个object复制到另一个container中,src,des都是/container/object的形式,des的container必须存在"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+src
        print x_storage_url
        headers = {'X-Auth-Token':self.x_auth_token,'Destination':des}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'COPY'
        res = urllib2.urlopen(req)
        return res.code

    def make_public(self,container):
        """将一个container为public"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container
        headers = {'X-Auth-Token':self.x_auth_token, 'X-Container-Read':'.r:*'}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'PUT'
        res = urllib2.urlopen(req)
        return res.code

    def make_private(self, container):
        """将container变为私有"""
        if not self.is_auth:
            self.get_auth()
        x_storage_url = self.x_storage_url+'/'+container
        headers = {'X-Auth-Token':self.x_auth_token, 'X-Container-Read':''}
        req = urllib2.Request(x_storage_url, headers=headers)
        req.get_method = lambda:'PUT'
        res = urllib2.urlopen(req)
        return res.code



if __name__ == '__main__':
    api = Swift_Api('test:tester','testing','http://127.0.0.1:8080/auth/v1.0')
    print api.get_container_list()
    #print api.get_object_list('NIhao')
   # print api.create_container('faf')
    #print api.delete_container('ty2')
    #print api.head_container('faf')
    #print api.get_object('fafa','s3.txt')[0]
    #print api.update_object('faf','闲敲云子.mp3')
    #print api.delete_object('faf','hosts')
   #print api.copy_object('/faf/git使用.txt','/ff/git使用.txt')
    #print api.make_public('faf')
   # print api.make_private('OK')
