#!/usr/bin/python
#coding=utf-8
import boto.s3

access_key_id='test:tester'
secret_access_key='testing'

class S3_To_Swift:

    def __init__(self, access_key_id,secret_access_key,port=8080,
            host='127.0.0.1'):
        """建立链接"""

        self.con = boto.s3.Connection(aws_access_key_id=access_key_id,
                aws_secret_access_key=secret_access_key,port=port,
                host=host,is_secure=False,
                calling_format=boto.s3.connection.OrdinaryCallingFormat())

    def get_connection(self):
        return self.con

    def get_bucket_list(self):
        buckets = self.con.get_all_buckets()
        for bucket in buckets:
            print bucket.name
        return buckets

    def create_bucket(self, bucket):
        b = self.con.create_bucket(bucket)
        print b.name
        return b

    def delete_bucket(self, bucket):
        return self.con.delete_bucket(bucket)

    def get_object_list(self,bucket):
        b = self.con.get_bucket(bucket)
        l = b.list()
        for obj in l:
            print obj.name
        return l

    def upload_object(self,key_name ,file_path, bucket_name):
        bucket = self.con.get_bucket(bucket_name)
        key = boto.s3.Key(bucket)
        key.key = key_name
        key.set_contents_from_file(open(file_path))

    def delete_object(self, bucket_name, key_name):
        bucket = self.con.get_bucket(bucket_name)
        bucket.delete_key(key_name)

    def get_object(self, bucket_name, key_name):
        bucket = self.con.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        contents = key.get_contents_as_string()
        print contents
        return key

    def set_object_meta(self, key_name, bucket_name, meta):
        bucket = self.con.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        for k, v in meta.items():
            key.set_metadata(k, v)

    def get_object_meta(self, key_name, bucket_name, meta_name):
        bucket = self.con.get_bucket(bucket_name)
        key = bucket.get_key(key_name)
        print key.exists()
        value = key.get_metadata(meta_name)
        print value
        return value

    def copy_object(self,src_bucket_name, src_key_name, des_bucket_name,
            des_key_name):
        src_bucket = self.con.get_bucket(src_bucket_name)
        src_key = src_bucket.get_key(src_key_name)
        print 'src key is %s'%src_key.name
        src_key.copy(des_bucket_name,des_key_name)
        des_bucket =self.con.get_bucket(des_bucket_name)
        des_key = des_bucket.get_key(des_key_name)
        print des_key.name

    def make_public(self, bucket_name):
        bucket = self.con.get_bucket(bucket_name)
        print bucket.set_acl('public-read')

    def msic(self, bucket_name):
        bucket = self.con.get_bucket(bucket_name)
        for item in bucket.list_grants():
            print item.id


if __name__=='__main__':
    con = S3_To_Swift(access_key_id, secret_access_key)
    #con.get_bucket_list()
    #b = con.create_bucket('ok')
    #con.delete_bucket('ok')
    #con.get_object_list('fafa')
    #con.upload_object('test','s3.txt','fafa')
    #con.delete_object('fafa', 'hosts')
    #con.get_object('fafa', 's3.txt')
    #con.set_object_meta('s3.txt', 'fafa',{'auth':'xyj'})
    #con.get_object_meta('s3.txt', 'fafa', 'auth')
    #con.copy_object('fafa','sed.pdf','fafafafa','sed2.pdf')
    #con.make_public('fafa')
    con.msic('fafa')
