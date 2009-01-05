#!/usr/bin/env python
"""
This module fill project database with objects described in YAML file.
"""

import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

import yaml
import logging
from itertools import chain

from django.contrib.auth.models import User


def parse():
    conf = yaml.load(open('init.ya').read())
    meta = conf.pop('meta')
    objects = {}
    models  = {}

    for model_name, path in meta['models'].iteritems():
        module = __import__(path, globals(), locals(), [model_name])
        model = getattr(module, model_name)
        models[model_name] = model

    for model_name in meta['order']:
        model = models[model_name]

        logging.debug('Deleting all %s instances' % model_name)
        model.objects.all().delete()

        defaults = meta['defaults'].get(model_name, {})

        for item in conf[model_name]:
            if 'ref' in item:
                ref = item.pop('ref')
            else:
                ref = None

            obj = model()
            m2m = {}

            for key, value in chain(item.iteritems(), defaults.iteritems()):
                if isinstance(obj, User) and key == 'password':
                    obj.set_password(value)
                elif isinstance(value, dict):
                    fk_model, fk_ref = value.items()[0]
                    setattr(obj, key, objects[fk_model][fk_ref])
                elif isinstance(value, (dict, list)):
                    for m2m_value in value:
                        fk_model, fk_ref = m2m_value.items()[0]
                        m2m.setdefault(key, []).append(objects[fk_model][fk_ref])
                else:
                    setattr(obj, key, value)
            obj.save()

            logging.debug(u'New %s instance: %s' % (model_name, obj))

            for key, values in m2m.iteritems():
                setattr(obj, key, values)
                #logging.debug('New m2m records %s' % values)
            
            if ref:
                objects.setdefault(model_name, {})[ref] = obj


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    parse()
