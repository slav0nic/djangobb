from django.conf import settings

DEFAULT_MAX_RESULTS = 100000
DEFAULT_WEIGHT = 1

def model_name(model):
    return "%s.%s" % (model._meta.app_label, model._meta.object_name)

def load_indexes():
    from djapian.utils import loading
    for app in settings.INSTALLED_APPS:
        try:
            loading.get_module(app, "index")
        except loading.NoModuleError:
            pass
