# -*- coding: utf-8 -*-

import sha
import random
from os.path import join, realpath, dirname
try:
    import Image
    import ImageFornt
    import ImageDraw
except ImportError:
    from PIL import Image, ImageFont, ImageDraw

from django.conf import settings

from apps.captcha.models import Solution


#TODO: find similar function in stdlib or django utils
def random_word(size=6):
    """
    Generate random alphanumeric word
    """
    
    chars = "abcdefghjkmnpqrstuvwzyz23456789"
    return ''.join(random.choice(chars) for x in xrange(size))


def generate_captcha():
    """
    Generate random solution and save it to database
    """

    solution = random_word()
    hash =  sha.new(solution + settings.SECRET_KEY).hexdigest()
    Solution.objects.create(value=solution, hash=hash)
    return hash


def test_solution(captcha_id, solution):
    """
    Compare the given answer with answer stored in database.
    """
    qs = Solution.objects.filter(hash=captcha_id, value=solution)
    return qs.count() > 0


def delete_solution(captcha_id):
    Solution.objects.filter(hash=captcha_id).delete()

def render(captcha_id, output):
    """
    Generate image and save it to output stream.
    """

    try:
        solution_value = Solution.objects.filter(hash=captcha_id)[0].value
    except IndexError:
        raise ValueError('Invalid captcha ID')

    fgcolor = getattr(settings, 'CAPTCHA_FG_COLOR', '#ffffff')
    bgcolor = getattr(settings, 'CAPTCHA_BG_COLOR', '#000000')
    font = ImageFont.truetype(join(dirname(realpath(__file__)),
                                   'data', 'Vera.ttf'), 25)
    dim = font.getsize(solution_value)
    img = Image.new('RGB', (dim[0] + 20, dim[1] + 10), bgcolor) 
    draw = ImageDraw.Draw(img)
    draw.text((10, 5), solution_value, font=font, fill=fgcolor)
    img.save(output, format='JPEG')
