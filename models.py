from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from precise_bbcode.fields import BBCodeTextField

#####################################################################
class ForumMember(models.Model):
    '''
        To keep the User class separated from every game related 
        activity and keep them anonymous we use a forum member
        and his information here.
    '''
    # Attributes
    uid = models.BigAutoField(
        primary_key = True, db_index = True)
    name = models.CharField(
        max_length = 50)
    owner = models.ForeignKey(
            User, 
            models.SET_NULL,
            null = True,    
            related_name='forum_member_owner')
    avatar = models.ImageField(
        upload_to='static/forum/avatar', 
        default= '/static/forum/entity/av_default.jpg')
    rank = models.PositiveIntegerField(
        )
    signature = models.CharField(
        max_length = 150)
    # Methods
    def __str__(self):
        return str(self.name)

#####################################################################
class ForumCategory( models.Model ):
    '''
    Recense les catégories du forum et les ordonne pour l'affichage
    '''
    uid = models.BigAutoField(
        primary_key = True, db_index = True)
    order = models.PositiveIntegerField(
        )
    name = models.CharField(
        max_length = 50, unique= True)
    rank_visibility = models.PositiveIntegerField(
        )
    def __str__(self):
        return str(self.name)

#####################################################################
class ThreadForum(models.Model):
    '''
        Posts on the forum
    '''
    # Attributes
    uid = models.BigAutoField(
        primary_key = True, db_index = True)
    category = models.ForeignKey(
            ForumCategory, 
            models.CASCADE,
            null = False,    
            related_name='forum_category')
    name = models.CharField(
        max_length = 50, unique= True)
    is_pinned = models.BooleanField(
        default = False)
    is_closed = models.BooleanField(
        default = False)
    author = models.ForeignKey(
        ForumMember, 
        models.SET_NULL,
        null = True,related_name = 'threadforum_ForumMember')
    timestamp =  models.DateTimeField(
        default = timezone.now)
    # Methods
    def __str__(self):
        return str(self.name)
    def PostCount(self):
        # get the number of posts in a thread
        post_count = PostForum.objects.filter(thread = self).count()
        return post_count
    def LastPost(self):
        # get the last post of a thread. used for timestamp and author
        if self.PostCount() > 0:
            last_post = PostForum.objects.filter(thread = self).order_by('timestamp').reverse()[0].timestamp
        else:
            last_post= ''
        return last_post

#####################################################################
class PostForum(models.Model):
    '''
        Posts on the forum
    '''
    # Attributes
    uid = models.BigAutoField(
        primary_key = True, db_index = True)
    content = BBCodeTextField(
        )
    author = models.ForeignKey(
        ForumMember, 
        models.SET_NULL,
        null = True,related_name = 'postforum_ForumMember')
    thread = models.ForeignKey(
        ThreadForum, 
        models.CASCADE,
        null = True,related_name = 'postforum_threadForum')
    timestamp =  models.DateTimeField(
        default = timezone.now)
    # Methods
    def __str__(self):
        return str(self.uid)

####################################################################
class ThreadLastVisit(models.Model):
    '''
        Allows to link forum members and threads, tracking the last
        visit they made and when. This allows to show members what
        threads have unread posts and in the template it shows a 
        different icon color.
    '''
    # Attributes
    uid = models.BigAutoField(
        primary_key= True, db_index= True)
    thread = models.ForeignKey(
        ThreadForum, 
        models.CASCADE,
        null = True,related_name= 'thread_thread_last_visit')
    member = models.ForeignKey(
        ForumMember, 
        models.CASCADE,
        null = True,
        related_name= 'member_thread_last_visit')
    last_visit = models.DateTimeField(
        default = timezone.now)
    # Methods
    def __str__(self):
        return str(self.uid)