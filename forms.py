from django import forms
from .models import *
from django.forms import ModelForm

class OgrelogForm(forms.Form):
    content = forms.CharField(
        widget = forms.Textarea(), label = '')

class ForumReplyForm(ModelForm):
    class Meta:
        model = PostForum
        fields = ['content']
        labels = {
        'content': ''
    }

class ForumprofileForm(ModelForm):
    class Meta:
        model = ForumMember
        fields = ['name', 'signature']
        labels = {
        'name': 'Pseudonyme',
        'signature': 'Signature',
    }

class NewThreadForm(forms.Form):
    name = forms.CharField(
        max_length = 50, 
        label = 'Titre')
    content = forms.CharField(
        widget = forms.Textarea(), label = 'Contenu')