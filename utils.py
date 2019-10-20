# python3
# functions called to get world specific variables.
from .models import *
from .forms import *

#####################################################################
def CurrentStateCheck(user):
    '''
        Returns a dictionary of useful information 
        by taking a request.user object.
    '''
    # Trying to get the current user of the request
    if user == 'AnonymousUser':
        current_user = False
    else:
        current_user = user
    # Pack everything in a dictionary
    current_state_data={
        'current_user': current_user,
    }
    return current_state_data