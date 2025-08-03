
from .base import *
import os

environment = os.environ.get('ENVIRONMENT', 'development')

if environment == 'local':
    from .local import *
elif environment == 'development':
   from .development import *
elif environment == 'uat':
   from .uat import *
elif environment == 'production':
   from .production import *
