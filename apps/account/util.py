# -*- coding: utf-8
"""
Useful utilities for account application.
"""

import re
import os.path
from datetime import datetime

from django.conf import settings
from django.template.loader import get_template
from django.template import Context, RequestContext
from django.shortcuts import render_to_response
from django.core.mail import send_mail
from django.conf import settings

# TODO: this module needs i18n

def build_redirect_url(request, default_url):
    """
    Retrieve redirect url from session.
    
    Use default if retrieved one is broken or not safe.
    """

    url = request.session.get('login_redirect_url')
    if not url or '//' in url or ' ' in url:
        url = default_url
    try:
        del request.session['login_redirect_url']
    except KeyError:
        pass
    return url


def parse_template(template_path, **kwargs):
    """
    Load and render template.

    First line of template should contain the subject of email.
    Return tuple with subject and content.
    """

    template = get_template(template_path)
    context = Context(kwargs)
    data = template.render(context).strip()
    subject, content = re.split(r'\r?\n', data, 1)
    return (subject.strip(), content.strip())


def email_template(rcpt, template_path, **kwargs):
    """
    Load, render and email template.

    **kwargs may contain variables for template rendering.
    """

    subject, content = parse_template(template_path, **kwargs)
    count = send_mail(subject, content, settings.DEFAULT_FROM_EMAIL,
                      [rcpt], fail_silently=True)
    mail_dir = getattr(settings, 'ACCOUNT_DEBUG_MAIL_DIR', False)

    if mail_dir:
        # TODO: could rcpt countain symbols restricted for file paths?
        fname = '%s_%s' % (rcpt, datetime.now().strftime('%H_%M'))
        fname = os.path.join(mail_dir, fname)
        # TODO: should we use encoding from conf.settings?
        data = (u'Subject: %s\n%s' % (subject, content)).encode('utf-8')
        file(fname, 'w').write(data)

    return bool(count)


def render_to(template_path):
    """
    Decorate the django view.

    Wrap view that return dict of variables, that should be used for
    rendering the template.
    Dict returned from view could contain special keys:
     * MIME_TYPE: mimetype of response
     * TEMPLATE: template that should be used insted one that was
                 specified in decorator argument
    """

    def decorator(func):
        def wrapper(request, *args, **kwargs):
            output = func(request, *args, **kwargs)
            if not isinstance(output, dict):
                return output
            kwargs = {'context_instance': RequestContext(request)}
            if 'MIME_TYPE' in output:
                kwargs['mimetype'] = output.pop('MIME_TYPE')

            template = template_path
            if 'TEMPLATE' in output:
                template = output.pop('TEMPLATE')
            return render_to_response(template, output, **kwargs)
        return wrapper
    return decorator
