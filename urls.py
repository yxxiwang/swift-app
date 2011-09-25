#!/usr/bin/python
#coding=utf-8
#****************************************************
# Author: 徐叶佳 - xyj.asmy@gmail.com
# Last modified: 2011-09-24 23:07
# Filename: workspace/swift_app/urls.py
# Description:
#****************************************************

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()
from django.conf.urls.defaults import *
import os

urlpatterns = patterns('swift_app.views',
    # Example:
    # (r'^swift_app/', include('swift_app.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
     (r'^admin/', include(admin.site.urls)),
     (r'^$','login'),
    (r'^login/$', 'login'),
    (r'^register/$','register'),
    (r'^logout/$', 'logout'),
    (r'^already-logged/$','already_logged'),
    (r'^control-panel/$','control_panel'),
    (r'^operation/$','operation'),
    (r'^upload/$','upload'),
    (r'download/$','download'),
)
urlpatterns+=patterns('',
        (r'^medias/(?P<path>.*)$','django.views.static.serve',{'document_root':os.path.join(os.path.dirname(__file__),'medias')}),)
