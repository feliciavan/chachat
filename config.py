import os
from decouple import config

S3_BUCKET = 'thesis-image'
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_S3_CUSTOM_DOMAIN = '%s.s3.amazonaws.com' % S3_BUCKET
AWS_LOCATION = 'chat'
S3_LOCATION = 'https://%s/%s/' % (AWS_S3_CUSTOM_DOMAIN, AWS_LOCATION)

SECRET_KEY = os.urandom(32)
DEBUG = True
PORT  = 5000
