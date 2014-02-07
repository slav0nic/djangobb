import django
__all__ = ['User']

# Pattern taken from django-cms see ticket https://github.com/divio/django-cms/issues/1798

if django.VERSION >= (1, 5):
    from django.contrib.auth import get_user_model
    User = get_user_model()
else:
    from django.contrib.auth.models import User
    get_user_model = lambda: User



