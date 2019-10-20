from django.contrib import admin
from .models import *

#####################################################################
class AdminThreadForum(admin.ModelAdmin):
    list_display= ['uid', 'name', 'is_closed', 'author', 'category', 'timestamp']
    ordering= ['timestamp']
admin.site.register(ThreadForum, AdminThreadForum)

#####################################################################
class AdminPostForum(admin.ModelAdmin):
    list_display= ['uid', 'content', 'author', 'thread']
    ordering= ['timestamp']
admin.site.register(PostForum, AdminPostForum)

#####################################################################
class AdminForumMember(admin.ModelAdmin):
    list_display= ['uid', 'name','owner']
    ordering= ['name', 'owner']
admin.site.register(ForumMember, AdminForumMember)

#####################################################################
class AdminForumCategory(admin.ModelAdmin):
    list_display= [ 'uid' , 'order' , 'name' , 'rank_visibility' ]
    ordering= [ 'order', 'name' ]
admin.site.register(ForumCategory, AdminForumCategory)

