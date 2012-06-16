# -*- coding: utf-8 -*-
import os.path
from datetime import datetime

from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from djangobb_forum.models import Topic, Post, Profile, Reputation, Report, \
    Attachment
from djangobb_forum import settings as forum_settings
from djangobb_forum.util import convert_text_to_html, set_language


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
    name = forms.CharField(label=_('Subject'), max_length=255,
                           widget=forms.TextInput(attrs={'size':'115'}))
    attachment = forms.FileField(label=_('Attachment'), required=False)

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

        self.fields['body'].widget = forms.Textarea(attrs={'class':'markup', 'rows':'20', 'cols':'95'})

        if not forum_settings.ATTACHMENT_SUPPORT:
            self.fields['attachment'].widget = forms.HiddenInput()
            self.fields['attachment'].required = False

    def clean(self):
        '''
        checking is post subject and body contains not only space characters
        '''
        errmsg = _('Can\'t be empty nor contain only whitespace characters')
        cleaned_data = self.cleaned_data
        body = cleaned_data.get('body')
        subject = cleaned_data.get('name')
        if subject:
            if not subject.strip():
                self._errors['name'] = self.error_class([errmsg])
                del cleaned_data['name']
        if body:
            if not body.strip():
                self._errors['body'] = self.error_class([errmsg])
                del cleaned_data['body']
        return cleaned_data

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
                    markup=self.user.forum_profile.markup,
                    body=self.cleaned_data['body'])

        post.save()
        if forum_settings.ATTACHMENT_SUPPORT:
            self.save_attachment(post, self.cleaned_data['attachment'])
        return post


    def save_attachment(self, post, memfile):
        if memfile:
            obj = Attachment(size=memfile.size, content_type=memfile.content_type,
                             name=memfile.name, post=post)
            dir = os.path.join(settings.MEDIA_ROOT, forum_settings.ATTACHMENT_UPLOAD_TO)
            fname = '%d.0' % post.id
            path = os.path.join(dir, fname)
            file(path, 'wb').write(memfile.read())
            obj.path = fname
            obj.save()


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
        self.fields['body'].widget = forms.Textarea(attrs={'class':'markup'})

    def save(self, commit=True):
        post = super(EditPostForm, self).save(commit=False)
        post.updated = datetime.now()
        topic_name = self.cleaned_data['name']
        if topic_name:
            post.topic.name = topic_name
        if commit:
            post.topic.save()
            post.save()
        return post


class EssentialsProfileForm(forms.ModelForm):
    username = forms.CharField(label=_('Username'))
    email = forms.CharField(label=_('E-mail'))

    class Meta:
        model = Profile
        fields = ['time_zone', 'language']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        self.request = extra_args.pop('request', None)
        self.profile = kwargs['instance']
        super(EssentialsProfileForm, self).__init__(*args, **kwargs)
        self.fields['username'].initial = self.profile.user.username
        if not self.request.user.is_superuser:
            self.fields['username'].widget = forms.HiddenInput()
        self.fields['email'].initial = self.profile.user.email

    def save(self, commit=True):
        if self.cleaned_data:
            if self.request.user.is_superuser:
                self.profile.user.username = self.cleaned_data['username']
            self.profile.user.email = self.cleaned_data['email']
            self.profile.time_zone = self.cleaned_data['time_zone']
            self.profile.language = self.cleaned_data['language']
            self.profile.user.save()
            if commit:
                self.profile.save()
        set_language(self.request, self.profile.language)
        return self.profile


class PersonalProfileForm(forms.ModelForm):
    name = forms.CharField(label=_('Real name'), required=False)

    class Meta:
        model = Profile
        fields = ['status', 'location', 'site']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        self.profile = kwargs['instance']
        super(PersonalProfileForm, self).__init__(*args, **kwargs)
        self.fields['name'].initial = "%s %s" % (self.profile.user.first_name, self.profile.user.last_name)

    def save(self, commit=True):
        self.profile.status = self.cleaned_data['status']
        self.profile.location = self.cleaned_data['location']
        self.profile.site = self.cleaned_data['site']
        if self.cleaned_data['name']:
            cleaned_name = self.cleaned_data['name'].strip()
            if  ' ' in cleaned_name:
                self.profile.user.first_name, self.profile.user.last_name = cleaned_name.split(None, 1)
            else:
                self.profile.user.first_name = cleaned_name
                self.profile.user.last_name = ''
            self.profile.user.save()
            if commit:
                self.profile.save()
        return self.profile


class MessagingProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['jabber', 'icq', 'msn', 'aim', 'yahoo']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        super(MessagingProfileForm, self).__init__(*args, **kwargs)


class PersonalityProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['show_avatar', 'signature']
        
    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        self.profile = kwargs['instance']
        super(PersonalityProfileForm, self).__init__(*args, **kwargs)
        self.fields['signature'].widget = forms.Textarea(attrs={'class':'markup', 'rows':'10', 'cols':'75'})

    def save(self, commit=True):
        profile = super(PersonalityProfileForm, self).save(commit=False)
        profile.signature_html = convert_text_to_html(profile.signature, self.profile.markup)
        if commit:
            profile.save()
        return profile


class DisplayProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['theme', 'markup', 'show_smilies']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        super(DisplayProfileForm, self).__init__(*args, **kwargs)


class PrivacyProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['privacy_permission']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        super(PrivacyProfileForm, self).__init__(*args, **kwargs)
        self.fields['privacy_permission'].widget = forms.RadioSelect(  
                                                    choices=self.fields['privacy_permission'].choices
                                                    )


class UploadAvatarForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['avatar']

    def __init__(self, *args, **kwargs):
        extra_args = kwargs.pop('extra_args', {})
        super(UploadAvatarForm, self).__init__(*args, **kwargs)


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
            qs = qs.filter(username__contains=username, forum_profile__post_count__gte=forum_settings.POST_USER_SEARCH)
            if sort_by=='username':
                if sort_dir=='ASC':
                    return qs.order_by('username')
                elif sort_dir=='DESC':
                    return qs.order_by('-username')
            elif sort_by=='registered':
                if sort_dir=='ASC':
                    return qs.order_by('date_joined')
                elif sort_dir=='DESC':
                    return qs.order_by('-date_joined')
            elif sort_by=='num_posts':
                if sort_dir=='ASC':
                    return qs.order_by('forum_profile__post_count')
                elif sort_dir=='DESC':
                    return qs.order_by('-forum_profile__post_count')
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
    sort_dir = forms.ChoiceField(choices=SORT_DIR_CHOICES, initial='DESC', label=_('Sort order'))
    show_as = forms.ChoiceField(choices=SHOW_AS_CHOICES, label=_('Show results as'))



class ReputationForm(forms.ModelForm):

    class Meta:
        model = Reputation
        fields = ['reason', 'post', 'sign']

    def __init__(self, *args, **kwargs):
        self.from_user = kwargs.pop('from_user', None)
        self.to_user = kwargs.pop('to_user', None)
        self.post = kwargs.pop('post', None)
        self.sign = kwargs.pop('sign', None)
        super(ReputationForm, self).__init__(*args, **kwargs)
        self.fields['post'].widget = forms.HiddenInput()
        self.fields['sign'].widget = forms.HiddenInput()
        self.fields['reason'].widget = forms.Textarea(attrs={'class':'markup'})

    def clean_to_user(self):
        name = self.cleaned_data['to_user']
        try:
            user = User.objects.get(username=name)
        except User.DoesNotExist:
            raise forms.ValidationError(_('User with login %s does not exist') % name)
        else:
            return user

    def clean(self):
        try:
            Reputation.objects.get(from_user=self.from_user, post=self.cleaned_data['post'])
        except Reputation.DoesNotExist:
            pass
        else:
            raise forms.ValidationError(_('You already voted for this post'))
        
        # check if this post really belong to `from_user`
        if not Post.objects.filter(pk=self.cleaned_data['post'].id, user=self.to_user).exists():
            raise forms.ValidationError(_('This post does\'t belong to this user'))

        return self.cleaned_data


    def save(self, commit=True):
        reputation = super(ReputationForm, self).save(commit=False)
        reputation.from_user = self.from_user
        reputation.to_user = self.to_user
        if commit:
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

    def save(self, commit=True):
        report = super(ReportForm, self).save(commit=False)
        report.created = datetime.now()
        report.reported_by = self.reported_by
        if commit:
            report.save()
        return report
