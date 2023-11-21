import logging
import boto3
from botocore.exceptions import ClientError
from django.core.files.uploadedfile import UploadedFile



def upload_file(file: UploadedFile, bucket, object_name=None):
    """Upload a file to an S3 bucket

    :param file: Django UploadedFile object to upload
    :param bucket: Bucket to upload to
    :param object_name: S3 object name. If not specified then file.name is used
    :return: True if file was uploaded, else False
    """

    # If S3 object_name was not specified, use file.name
    if object_name is None:
        object_name = file.name

    # Upload the file
    s3_client = boto3.client('s3')
    try:
        s3_client.upload_fileobj(file, bucket, object_name)
    except ClientError as e:
        logging.error(e)
        return False
    return True