from optparse import make_option
import os

from django.core.management.base import BaseCommand, CommandError

import forum

class Command(BaseCommand):
    option_list = BaseCommand.option_list + ( 
        make_option('-l', '--list', dest='list', action='store_true', default=False,
            help='Show all available migrations'),
        make_option('-e', '--exec', dest='migration', help='Execute the migration')
    )   
    help = 'Execute migration scripts.'

    def handle(self, *args, **kwargs):
        if kwargs['list']:
            self.command_list()
        elif kwargs['migration']:
            self.command_migrate(kwargs['migration'])
        else:
            print 'Invalid options'


    def command_list(self):
        root = os.path.dirname(os.path.realpath(forum.__file__))
        dir = os.path.join(root, 'migrations')
        migs = []
        for fname in os.listdir(dir):
            if fname.endswith('.py'):
                mod_name = fname[:-3]
                mod = __import__('forum.migrations.%s' % mod_name,
                                 globals(), locals(), ['foobar'])
                if hasattr(mod, 'migrate'):
                    migs.append((mod_name, mod))

        migs = sorted(migs, lambda a, b: cmp(a[0], b[0]))
        for name, mig in migs:
            print '%s - %s' % (name, mig.DESCRIPTION)


    def command_migrate(self, mod_name):
        mod = __import__('forum.migrations.%s' % mod_name,
                         globals(), locals(), ['foobar'])
        mod.migrate()
