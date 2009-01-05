# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseNotFound

from apps.captcha import util

def captcha_image(request, captcha_id):
    """
    Generate and save image to response.
    """

    response = HttpResponse(mimetype='image/jpeg')
    try:
        util.render(captcha_id, response)
    except ValueError:
        return HttpResponseNotFound('Invalid captcha ID')
    else:
        return response
