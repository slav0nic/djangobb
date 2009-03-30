"""
This module contains middlewares for account application:
    * DebugLoginMiddleware
    * OneTimeCodeAuthMiddleware
    * TestCookieMiddleware
"""

from django.http import HttpResponseRedirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.conf import settings                               #PC

from account.util import email_template
from account.auth_key import validate_key, decode_key, decode_key
from account.settings import ACCOUNT_DOMAIN

def login_user(request, user):
    user.backend = 'django.contrib.auth.backends.ModelBackend'
    login(request, user)    


class DebugLoginMiddleware(object):
    """
    This middleware authenticates user with just an
    ID parameter in the URL.
    This is dangerous middleware, use it with caution.
    """

    def process_request(self, request):
        """
        Login user with ID from loginas param of the query GET data.

        Do it only then settings.ACCOUNT_LOGIN_DEBUG is True
        """

        if getattr(settings, 'ACCOUNT_LOGIN_DEBUG', False):
            try:
                id = int(request.GET.get('loginas', 0))
                user = User.objects.get(pk=id)
            except ValueError:
                return
            except User.DoesNotExist:
                return
            else:
                login_user(user)


class AuthKeyMiddleware(object):
    """
    This middleware can authenticate user with auth key in HTTP request.
    """

    def process_request(self, request):

        key = request.REQUEST.get('authkey', None)
        
        if validate_key(key):
            args = decode_key(key)

            try:
                print args
                user = User.objects.get(username=args['username'])
            except User.DoesNotExist:
                return

            action = args.get('action')
            if 'activation' == action:
                if not user.is_active:
                    user.is_active = True
                    user.save()
                    email_template(user.email, 'account/mail/welcome.txt',
                                   **{'login': user.username, 'domain': ACCOUNT_DOMAIN})
            if user.is_active:
                if 'new_password' == action:
                    if args.get('password'):
                        user.set_password(args['password'])
                        user.save()
                
                if 'new_email' == action:
                    if args.get('email'):
                        user.email = args['email']
                        user.save()
                
                login_user(request, user)


class TestCookieMiddleware(object):
    """
    This middleware fixes error that appeares when user try to login
    not from page that was generated with django.contrib.auth.views.login view.
    """

    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Setup test cookie.
        """

        request.session.set_test_cookie()
