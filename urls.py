from django.conf.urls import url
from .views import *
from .models import *

urlpatterns = [
    url(r'newthread/(?P<category_uid>[\w-]+)', ForumNewThread),
    url(r'thread/(?P<thread_uid>[\w-]+)', ForumThread),
    url(r'report/(?P<post_uid>[\w-]+)', ReportForumPost),
    url(r'editpost/(?P<post_uid>[\w-]+)', ForumEditPost),
    url(r'profile', ForumProfile),
    url(r'', ForumIndex),
    ]