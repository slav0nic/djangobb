from django.core.management.base import NoArgsCommand
from djangobb_forum.models import PostStatus


class Command(NoArgsCommand):
    help = u'Process unfiltered posts for spam.'

    def handle_noargs(self, **options):
        PostStatus.objects.review_new_posts()
