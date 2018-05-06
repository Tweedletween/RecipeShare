#!/usr/bin/python
import sys
import logging
#import os
logging.basicConfig(stream=sys.stderr)
sys.path.insert(0,"/home/ubuntu/RecipeShare/")

from application import app as application
application.secret_key = 'super_secret_key'
#logger = logging.getLogger('wsgi')
#logger.error('Pwd %s', os.getcwd())
