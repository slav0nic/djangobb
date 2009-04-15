# -*- coding: utf-8 -*-
import re
import os.path
from datetime import datetime

from django import forms
from django.conf import settings
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from forum.models import Topic, Post, Profile, Reputation, Report, PrivateMessage,\
    Forum, Attachment
from forum.markups import mypostmarkup
from forum import settings as forum_settings

SORT_USER_BY_CHOICES = (
    ('username', _(u'Username')),
    ('registered', _(u'Registered')),
    ('num_posts', _(u'No. of posts')),
)

SORT_POST_BY_CHOICES = (
    ('0', _(u'Post time')),
    ('1', _(u'Author')),
    ('2', _(u'Subject')),
    ('3', _(u'Forum')),
)

SORT_DIR_CHOICES = (
    ('ASC', _(u'Ascending')),
    ('DESC', _(u'Descending')),
)

SHOW_AS_CHOICES = (
    ('topics', _(u'Topics')),
    ('posts', _(u'Posts')),
)

SEARCH_IN_CHOICES = (
    ('all', _(u'Message text and topic subject')),
    ('message', _(u'Message text only')),
    ('topic', _(u'Topic subject only')),
)

class AddPostForm(forms.ModelForm):
    name = forms.CharField(label=_('Subject'),
                           widget=forms.TextInput(attrs={'size':'115'}))
    attachment = forms.FileField(label=_('Attachment'), required=False,
                           widget=forms.FileInput(attrs={'size':'115'}))

    class Meta:
        model = Post
        fields = ['body']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.topic = kwargs.pop('topic', None)
        self.forum = kwargs.pop('forum', None)
        self.ip = kwargs.pop('ip', None)
        super(AddPostForm, self).__init__(*args, **kwargs)
        
        if self.topic:
            self.fields['name'].widget = forms.HiddenInput()
            self.fields['name'].required = False
            
        self.fields['body'].widget = forms.Textarea(attrs={'class':'bbcode', 'rows':'20', 'cols':'95'})
        
        if not forum_settings.ATTACHMENT_SUPPORT:
            self.fields['attachment'].widget = forms.HiddenInput()
            self.fields['attachment'].required = False

    def clean_attachment(self):
        if self.cleaned_data['attachment']:
            memfile = self.cleaned_data['attachment']
            if memfile.size > forum_settings.ATTACHMENT_SIZE_LIMIT:
                raise forms.ValidationError(_('Attachment is too big'))
            return self.cleaned_data['attachment']

    

    def save(self):
        if self.forum:
            topic = Topic(forum=self.forum,
                          user=self.user,
                          name=self.cleaned_data['name'])
            topic.save()
        else:
            topic = self.topic

        post = Post(topic=topic, user=self.user, user_ip=self.ip,
                    markup='bbcode',
                    body=self.cleaned_data['body'])
        post.save()
        if forum_settings.ATTACHMENT_SUPPORT:
            self.save_attachment(post, self.cleaned_data['attachment'])

        profile = get_object_or_404(Profile, user=self.user)
        profile.post_count += 1
        profile.save()
        return post
    
    def save_attachment(self, post, memfile):
        if memfile:
            obj = Attachment(size=memfile.size, content_type=memfile.content_type,
                             name=memfile.name, post=post)
            dir = os.path.join(settings.MEDIA_ROOT, forum_settings.ATTACHMENT_UPLOAD_TO)
            fname = '%d.0' % post.id
            path = os.path.join(dir, fname)
            file(path, 'w').write(memfile.read())
            obj.path = fname
            obj.save()

    
class EssentialsProfileForm(forms.ModelForm):
    username = forms.CharField(label=_('Username'))
    email = forms.CharField(label=_('E-mail'))
    
    class Meta:
        model = Profile
        fields = ['time_zone', 'language']
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(EssentialsProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.user.username
        self.fields['email'].initial = self.user.email
        
    def save(self):
        user = get_object_or_404(User, username=self.user)
        profile = get_object_or_404(Profile, user=self.user)
        if self.cleaned_data:
            user.username = self.cleaned_data['username']
            user.email = self.cleaned_data['email']
            profile.time_zone = self.cleaned_data['time_zone']
            profile.language = self.cleaned_data['language']
            user.save()
        return profile
   

class PersonalProfileForm(forms.ModelForm):
    name = forms.CharField(label=_('Real name'))
    
    class Meta:
        model = Profile
        fields = ['status', 'location', 'site']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(PersonalProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = "%s %s" % (self.user.first_name, self.user.last_name)
    
    def save(self):
        user = get_object_or_404(User, username=self.user)
        profile = get_object_or_404(Profile, user=self.user)
        profile.status = self.cleaned_data['status']
        profile.location = self.cleaned_data['location']
        profile.site = self.cleaned_data['site']
        if self.cleaned_data['name']:
            if len(self.cleaned_data['name'].split()) > 1:
                user.first_name, user.last_name = self.cleaned_data['name'].split()
            else:
                user.first_name = self.cleaned_data['name'].split()[0]
                user.last_name = ''
            user.save()
        return profile.save()
        
class MessagingProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['jabber', 'icq', 'msn', 'aim', 'yahoo']

class PersonalityProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['show_avatar', 'signature']
        
    def __init__(self, *args, **kwargs):
        super(PersonalityProfileForm, self).__init__(*args, **kwargs)
        self.fields['signature'].widget = forms.Textarea(attrs={'class':'bbcode', 'rows':'10', 'cols':'75'})
        
    def save(self):
        profile = super(PersonalityProfileForm, self).save(commit=False)
        profile.signature = mypostmarkup.markup(profile.signature, auto_urls=False)
        profile.save()
        return profile
        
class DisplayProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme']
        
class PrivacyProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['privacy_permission']
        
    def __init__(self, *args, **kwargs):
        super(PrivacyProfileForm, self).__init__(*args, **kwargs)
        self.fields['privacy_permission'].widget = forms.RadioSelect(  
                                                    choices=self.fields['privacy_permission'].choices
                                                    )
        
#class AdminProfileForm(forms.Form):
#    forums = forms.CharField(label=_('Forums'))
#    
#    def __init__(self, *args, **kwargs):
#        self.user = kwargs.pop('user', None)
#        super(AdminProfileForm, self).__init__(*args, **kwargs)
#        forums = [(forum, forum) for forum in Forum.objects.all()]
#        self.fields['forums'].widget = forms.CheckboxSelectMultiple(  
#                                                choices=forums
#                                                )
#    
#    def save(self):
#        return self.forums

class UploadAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

class EditPostForm(forms.ModelForm):
    name = forms.CharField(required=False, label=_('Subject'),
                           widget=forms.TextInput(attrs={'size':'115'}))
    
    class Meta:
        model = Post
        fields = ['body']
        
    def __init__(self, *args, **kwargs):
        self.topic = kwargs.pop('topic', None)
        super(EditPostForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = self.topic
        self.fields['body'].widget = forms.Textarea(attrs={'class':'bbcode'})

    def save(self):
        post = super(EditPostForm, self).save(commit=False)
        post.updated = datetime.now()
        post.save()
        return post


class UserSearchForm(forms.Form):
    username = forms.CharField(required=False, label=_('Username'))
    #show_group = forms.ChoiceField(choices=SHOW_GROUP_CHOICES)
    sort_by = forms.ChoiceField(choices=SORT_USER_BY_CHOICES, label=_('Sort by'))
    sort_dir = forms.ChoiceField(choices=SORT_DIR_CHOICES, label=_('Sort order'))

    def filter(self, qs):
        if self.is_valid():
            username = self.cleaned_data['username']
            #show_group = self.cleaned_data['show_group']
            sort_by = self.cleaned_data['sort_by']
            sort_dir = self.cleaned_data['sort_dir']
            if sort_by=='username':
                if sort_dir=='ASC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('username')
                elif sort_dir=='DESC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('-username')
            elif sort_by=='registered':
                if sort_dir=='ASC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('date_joined')
                elif sort_dir=='DESC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('-date_joined')
            elif sort_by=='num_posts':
                if sort_dir=='ASC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('forum_profile__post_count')
                elif sort_dir=='DESC':
                    return qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH).order_by('-forum_profile__post_count')
        else:
            return qs


class PostSearchForm(forms.Form):
    keywords = forms.CharField(required=False, label=_('Keyword search'), 
                               widget=forms.TextInput(attrs={'size':'40', 'maxlength':'100'}))
    author = forms.CharField(required=False, label=_('Author search'),
                             widget=forms.TextInput(attrs={'size':'25', 'maxlength':'25'}))
    forum = forms.CharField(required=False, label=_('Forum'))
    search_in = forms.ChoiceField(choices=SEARCH_IN_CHOICES, label=_('Search in'))
    sort_by = forms.ChoiceField(choices=SORT_POST_BY_CHOICES, label=_('Sort by'))
    sort_dir = forms.ChoiceField(choices=SORT_DIR_CHOICES, label=_('Sort order'))
    show_as = forms.ChoiceField(choices=SHOW_AS_CHOICES, label=_('Show results as'))
        

class ReputationForm(forms.ModelForm):
    
    class Meta:
        model = Reputation
        fields = ['reason', 'topic', 'sign']
        
    def __init__(self, *args, **kwargs):
        self.from_user = kwargs.pop('from_user', None)
        self.to_user = kwargs.pop('to_user', None)
        self.topic = kwargs.pop('topic', None)
        self.sign = kwargs.pop('sign', None)
        super(ReputationForm, self).__init__(*args, **kwargs)
        self.fields['topic'].widget = forms.HiddenInput()
        self.fields['sign'].widget = forms.HiddenInput()
        self.fields['reason'].widget = forms.Textarea(attrs={'class':'bbcode'})
    
    def clean_to_user(self):
        name = self.cleaned_data['to_user']
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User with login %s does not exist') % name)
        else:
            return user
    
    def save(self):
        reputation = super(ReputationForm, self).save(commit=False)
        reputation.from_user = self.from_user
        reputation.to_user = self.to_user
        reputation.time = datetime.now()
        reputation.save()
        return reputation
        
class MailToForm(forms.Form):
    subject = forms.CharField(label=_('Subject'),
                              widget=forms.TextInput(attrs={'size':'75', 'maxlength':'70', 'class':'longinput'}))
    body = forms.CharField(required=False, label=_('Message'), 
                               widget=forms.Textarea(attrs={'rows':'10', 'cols':'75'}))

class ReportForm(forms.ModelForm):
    
    class Meta:
        model = Report
        fields = ['reason', 'post']
        
    def __init__(self, *args, **kwargs):
        self.reported_by = kwargs.pop('reported_by', None)
        self.post = kwargs.pop('post', None)
        super(ReportForm, self).__init__(*args, **kwargs)
        self.fields['post'].widget = forms.HiddenInput()
        self.fields['post'].initial = self.post
        self.fields['reason'].widget = forms.Textarea(attrs={'rows':'10', 'cols':'75'})
        
    def save(self):
        report = super(ReportForm, self).save(commit=False)
        report.created = datetime.now()
        report.reported_by = self.reported_by
        report.save()
        return report
    
class CreatePMForm(forms.ModelForm):
    recipient = forms.CharField(label=_('Recipient'))
    
    class Meta:
        model = PrivateMessage
        fields = ['subject', 'body']
        
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CreatePMForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['recipient', 'subject', 'body']
        self.fields['subject'].widget = widget=forms.TextInput(attrs={'size':'115'})
        self.fields['body'].widget = forms.Textarea(attrs={'class':'bbcode'})
        
    def clean_recipient(self):
        name = self.cleaned_data['recipient']
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User with login %s does not exist') % name)
        else:
            return user

    def save(self):
        pm = PrivateMessage(src_user=self.user, dst_user=self.cleaned_data['recipient'])
        pm = forms.save_instance(self, pm)
        return pm