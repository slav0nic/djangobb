import re
from registration.forms import RegistrationFormUniqueEmail


class RegistrationFormUtfUsername(RegistrationFormUniqueEmail):
    '''
    Allowed UTF8 logins with space
    '''
    def __init__(self, *args, **kwargs):
        super(RegistrationFormUtfUsername, self).__init__(*args, **kwargs)
        self.fields['username'].regex = re.compile(r"^[\w\s-]+$", re.UNICODE)

