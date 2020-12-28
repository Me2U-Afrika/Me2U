from storages.backends.s3boto3 import S3Boto3Storage
from whitenoise.storage import CompressedManifestStaticFilesStorage


class MediaStorage(S3Boto3Storage):
    bucket_name = 'afrikame2u'
    file_overwrite = False


class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
    manifest_strict = False
