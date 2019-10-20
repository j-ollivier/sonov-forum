from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from .models import *
import operator #for sorting objects from different tables in one aggregated list
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .utils import *
from .forms import *
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMessage, send_mail
from django.db.models import AutoField
from precise_bbcode.bbcode import get_parser
from django.utils import timezone


#####################################################################
def ForumIndex( request ):
    '''
        The overview of the forum
    '''
    current_state_data = CurrentStateCheck( request.user )
    threads = ThreadForum.objects.all().order_by( 'timestamp' )
    try:
        current_member = ForumMember.objects.get( 
                    owner = request.user )
        member_last_visits = list( ThreadLastVisit.objects.filter( 
                    member = current_member ) )
    except ObjectDoesNotExist:
        current_member = False
    except TypeError:
        current_member = False

    # Appending a virtual attribute to all threads to monitor unread
    # posts for each thread
    for thread in threads:
        thread.has_unread_post= False
        if current_member:
            try:
                thread_last_visit= ThreadLastVisit.objects.get( 
                    member = current_member, thread = thread )
            except ObjectDoesNotExist:
                thread.has_unread_post= True
            else:
                if thread_last_visit.last_visit < thread.LastPost():
                    thread.has_unread_post= True
                else:
                    thread.has_unread_post= False
        else:
            thread.has_unread_post= False
    if current_member:
        categories = ForumCategory.objects.filter( rank_visibility__lte = current_member.rank  ).order_by( 'order' )
    else:
        categories = ForumCategory.objects.filter( rank_visibility = 1 ).order_by( 'order' )
    page_specifics = {
        'page_title': 'Forum',
        'categories': categories,
        'threads': threads,
    }
    # Merge the dictionaries
    context = {**current_state_data, **page_specifics}
    template = loader.get_template( 
        'forum/forum_index.html' )
    return HttpResponse( template.render( context, request ) )

#####################################################################
def ForumThread( request, thread_uid ):
    '''
        Straigthforward mate
    '''
    current_state_data = CurrentStateCheck( request.user )
    if request.method== 'GET' and request.user.is_authenticated:
        is_logged= True
        thread = ThreadForum.objects.get( 
            pk= thread_uid )
        post_list= PostForum.objects.filter( 
            thread= thread ).order_by( 'timestamp' )
        current_member= ForumMember.objects.get( 
                owner= request.user )
        # Modify or add a last_visit entry to keep track of member's
        # read threads
        # note that update is not verbose enough here too bad we
        # have to get the obj in memory
        try:
            last_visit= ThreadLastVisit.objects.get( 
                thread=thread, member=current_member )
            last_visit.last_visit= timezone.now()
            last_visit.save() 
        except ObjectDoesNotExist:
             new_visit= ThreadLastVisit( 
                 thread= thread, member= current_member )
             new_visit.save()
        page_specifics = {
            'page_title': thread.name,
            'current_member': current_member,
            'thread': thread,
            'post_list': post_list,
            'reply_form': ForumReplyForm()
        }
        context = {**current_state_data, **page_specifics}
        template = loader.get_template( 
            'forum/forum_thread.html' )
        return HttpResponse( template.render( context, request ) )
    elif request.method== 'POST' and request.user.is_authenticated:
        is_logged= True
        form= ForumReplyForm( request.POST )
        if form.is_valid():
            new_post= PostForum()
            new_post.thread= ThreadForum.objects.get( 
                pk= thread_uid )
            new_post.author= ForumMember.objects.get( 
                owner= request.user )
            new_post.content= form.cleaned_data['content']
            new_post.save()
            return HttpResponseRedirect( 
                '/forum/thread/{}'.format( thread_uid ) )
        else:
            return HttpResponseRedirect( '/nope' )
    else: # anonymous visitor
        is_logged= False
        thread = ThreadForum.objects.get( 
            pk= thread_uid )
        post_list= PostForum.objects.filter( 
            thread= thread ).order_by( 'timestamp' )
        page_specifics = {
            'page_title': thread.name,
            'thread': thread,
            'post_list': post_list,
            'is_logged': is_logged,
        }
        context = {**current_state_data, **page_specifics}
        template = loader.get_template( 
            'forum/forum_thread.html' )
        return HttpResponse( template.render( context, request ) )


@login_required
#####################################################################
def ForumEditPost( request, post_uid ):
    '''
        
    '''
    if request.method== 'GET':
        current_state_data = CurrentStateCheck( request.user )
        current_post= PostForum.objects.get( pk= post_uid )
        current_member= ForumMember.objects.get( owner= request.user )
        if current_post.author != current_member:
            # if someone else than the author tries to view the page
            return HttpResponseRedirect( '/forum/nope' )
        else: # if author and page viewer's character match
            page_specifics = {
                'page_title': 'Editer message',
                'change_post_form': ForumReplyForm( 
                    instance= current_post ),
                'current_post': current_post,
            }
            context = {**current_state_data, **page_specifics}
            template= loader.get_template( 
                'forum/forum_edit_post.html' )
            return HttpResponse( template.render( context, request ) )
    else: # method == post
        form= ForumReplyForm( request.POST )
        if form.is_valid():
            current_post= PostForum.objects.get( pk= post_uid )
            current_post.content= form.cleaned_data['content']
            current_post.save()
            return HttpResponseRedirect( 
                '/forum/thread/{}'.format( 
                    current_post.thread.uid ) )
        else:
            return HttpResponseRedirect( '/nope' )

@login_required
#####################################################################
def ForumNewThread( request , category_uid ):
    '''
        Post a new thread. User chooses the category, title ( name ) 
        and content and it creates the thread object. Once created,
        it retrieves the thread to attach a post to it ( OP ) using
        its name ( which is unique ).
    '''
    if request.method== 'GET':
        current_state_data = CurrentStateCheck( request.user )
        page_specifics = {
            'page_title': 'Nouveau fil',
            'new_thread_form': NewThreadForm(),
            'category' : ForumCategory.objects.get( uid = category_uid )
        }
        context = {**current_state_data, **page_specifics}
        template= loader.get_template( 
            'forum/new_thread.html' )
        return HttpResponse( template.render( context, request ) )
    else: # method == post
        form = NewThreadForm( request.POST )
        if form.is_valid():
            poster= ForumMember.objects.get( owner= request.user )
            # a thread is blank and has a first original post so
            # the form generates 2 objects in 2 tables.
            # thread generation
            new_thread = ThreadForum()
            new_post = PostForum()
            new_thread.name = form.cleaned_data['name']
            new_thread.author = poster
            new_thread.category = ForumCategory.objects.get( uid = int( category_uid ) ) 
            new_thread.save()
            # post generation
            # name of thread has unique constraint so we use it to 
            # retrieve it and attach an original post to it
            thread_to_link= ThreadForum.objects.get( 
                name=form.cleaned_data['name'] )
            new_post.content = form.cleaned_data['content']
            new_post.author = poster
            new_post.thread = thread_to_link
            new_post.save()
            return HttpResponseRedirect( 
                '/forum/thread/{}'.format( 
                    thread_to_link.uid ) )
        else:
            return HttpResponseRedirect( '/nope' )

@login_required
#####################################################################
def ForumProfile( request ):
    '''
        Display a forum member profile.
    '''
    if request.method== 'GET':
        current_state_data = CurrentStateCheck( request.user )
        current_profile= ForumMember.objects.get( owner= request.user )
        page_specifics={
            'page_title': 'Profil forum',
            'change_profile_form': ForumprofileForm( 
                instance= current_profile ),
            'current_profile': current_profile,
        }
        context = {**current_state_data, **page_specifics}
        template= loader.get_template( 
            'forum/forum_profile.html' )
        return HttpResponse( template.render( context, request ) )
    else: # method == post
        form= ForumprofileForm( request.POST, request.FILES )
        if form.is_valid():
            profile= ForumMember.objects.get( owner= request.user )
            profile.name= form.cleaned_data['name']
            profile.signature= form.cleaned_data['signature']
            profile.save()
            return HttpResponseRedirect( '/forum' )
        else:
            return HttpResponseRedirect( '/nope' )

@login_required
#####################################################################
def ReportForumPost( request, post_uid ):
    '''
        Users can report a post they find offensive or unfitting.
    '''
    send_mail( 
        'Post reporté',
        'http://www.vaste.fr/admin/forum/postforum/{}/change/'.format( 
            post_uid ),
        'voxclam.indes@gmail.com',
        ['voxclam.indes@gmail.com'], )
    return HttpResponseRedirect( 'forum/thanks' )

"""
#####################################################################
def ( request ):
    '''
    '''
    current_state_data = CurrentStateCheck( request.user.id )
    page_specifics = {
    }
    context = {**current_state_data, **page_specifics}
    template = loader.get_template( 
    '.html' )
    return HttpResponse( template.render( context, request ) )
"""
