import os


AWS_DEFAULT_ACL = None
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = os.getenv('AWS_STORAGE_BUCKET_NAME')
AWS_S3_REGION_NAME = os.getenv('AWS_S3_REGION_NAME', 'eu-central-003')
AWS_S3_SIGNATURE_VERSION = 's3v4'
AWS_S3_ADDRESSING_STYLE = 'virtual'
AWS_S3_ENDPOINT_URL = os.getenv(
    'AWS_S3_ENDPOINT_URL',
    f'https://s3.{AWS_S3_REGION_NAME}.backblazeb2.com',
)

AWS_S3_OBJECT_PARAMETERS = {
    'CacheControl': 'public, max-age=31536000, immutable'
}
AWS_S3_CUSTOM_DOMAIN = os.getenv(
    'CDN_DOMAIN',
    f'{AWS_STORAGE_BUCKET_NAME}.s3.{AWS_S3_REGION_NAME}.backblazeb2.com',
)
STATIC_LOCATION = 'static'
STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/{STATIC_LOCATION}/'

COLLECTFAST_STRATEGY = 'collectfast.strategies.boto3.Boto3Strategy'