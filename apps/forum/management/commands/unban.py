from optparse import make_option
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from forum.models import Ban


class Command(BaseCommand):
    
    option_list = BaseCommand.option_list + (
        make_option('--all', action='store_true', dest='all', default=False, 
                    help=u'Unban all users'),
        make_option('--in-time', action='store_true', dest='in-time', default=False, 
                    help=u'Unban users in time'),
    )
    help = u'Unban users'
    
    def handle(self, *args, **options):
         if options['all']:
             bans = Ban.objects.all()
             for ban in bans:
                 ban.user.is_active = True
                 ban.user.save()
                 ban.delete()
         elif options['in-time']:
             bans = Ban.objects.all()
             today = datetime.now()
             for ban in bans:
                 ban_end = ban.ban_end.replace(hour=0, minute=0, second=0)
                 if today >= ban_end:
                     ban.user.is_active = True
                     ban.user.save()
                     ban.delete()
         else:
             print 'Invalid options'
