# appname/views.py

import logging
import os

import boto3
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, FileUploadParser
from rest_framework.response import Response
from rest_framework.views import APIView

from empins2023 import settings
from empins2023.settings import AWS_STORAGE_BUCKET_NAME, BASE_DIR
from .utils import upload_file


@swagger_auto_schema(
    manual_parameters=[
        openapi.Parameter(
            name="Authorization",
            in_=openapi.IN_HEADER,
            type=openapi.TYPE_STRING,
            description="API key in the format 'X-Api-Key <your-api-key>'",
            required=True,
        ),
    ],
)
class S3ListBucket(APIView):
    def get(self, request):
        try:
            s3 = boto3.client('s3')
            response = s3.list_buckets()
            buckets = [bucket['Name'] for bucket in response['Buckets']]

            return Response({'buckets': buckets}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to list buckets'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class S3CreateBucket(APIView):
    def post(self, request):
        bucket_name = request.data.get('bucket_name')
        region = request.data.get('region', None)

        try:
            if region is None:
                s3_client = boto3.client('s3')
                s3_client.create_bucket(Bucket=bucket_name)
            else:
                s3_client = boto3.client('s3', region_name=region)
                location = {'LocationConstraint': region}
                s3_client.create_bucket(Bucket=bucket_name, CreateBucketConfiguration=location)
            return Response({'message': 'Bucket created successfully'}, status=status.HTTP_201_CREATED)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to create bucket'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class S3UploadFile(APIView):
#     def post(self, request):
#         File = request.FILES.get('File')
#         if File:
#             s3_client = boto3.client('s3')
#             object_name = File.name
#             try:
#                 s3_client.upload_fileobj(File, AWS_STORAGE_BUCKET_NAME, object_name)
#                 return Response({'message': f'File {object_name} uploaded successfully'}, status=status.HTTP_201_CREATED)
#             except Exception as e:
#                 logging.error(e)
#                 return Response({'error': 'Failed to upload file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
#         else:
#             return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)

# Import the modified upload_file function
class S3UploadFile(APIView):
    def post(self, request, *args, **kwargs):
        # Replace with your own values or retrieve them from settings
        aws_access_key_id = settings.AWS_ACCESS_KEY_ID
        aws_secret_access_key = settings.AWS_SECRET_ACCESS_KEY
        bucket_name = settings.AWS_STORAGE_BUCKET_NAME

        s3 = boto3.client(
            's3',
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )

        try:
            folder_name = 'Tours'
            for file in request.FILES.getlist('file'):
                s3_key = f"{folder_name}/{file.name}"
                s3.upload_fileobj(file, bucket_name, s3_key)

            return Response({'message': 'Files uploaded successfully'},
                            status=status.HTTP_201_CREATED)




        except Exception as e:
            return Response({'error': f'Failed to upload file to S3: {e}'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# class S3DownloadFile(APIView):
#     def get(self, request, file_name):
#         s3_client = boto3.client('s3')
#         try:
#             s3_client.download_file(AWS_STORAGE_BUCKET_NAME, file_name, file_name)
#             # Provide a download link to the file
#             file_path = os.path.join(BASE_DIR, file_name)
#             return Response({'file_path': file_path}, status=status.HTTP_200_OK)
#         except Exception as e:
#             logging.error(e)
#             return Response({'error': 'Failed to download file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class S3DownloadFile(APIView):
#     def get(self, request, file_name):
#         s3_client = boto3.client('s3')
#         try:
#             folder_name = 'Tours'  # Specify the folder name here
#             s3_key = f"{folder_name}/{file_name}"
#
#             # Specify the local file path where you want to save the downloaded file
#             local_file_path = os.path.join(BASE_DIR, file_name)
#
#             s3_client.download_file(AWS_STORAGE_BUCKET_NAME, s3_key, local_file_path)
#
#             # Provide a download link to the file
#             return Response({'file_path': local_file_path}, status=status.HTTP_200_OK)
#         except Exception as e:
#             logging.error(e)
#             return Response({'error': 'Failed to download file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
# class S3DownloadFile(APIView):
#     def get(self, request, file_name):
#         s3_client = boto3.client('s3')
#         try:
#             folder_name = 'Tours'  # Specify the folder name here
#             s3_key = f"{folder_name}/{file_name}"
#
#             # Create a presigned URL for the file
#             presigned_url = s3_client.generate_presigned_url(
#                 'get_object',
#                 Params={'Bucket': settings.AWS_STORAGE_BUCKET_NAME, 'Key': s3_key},
#                 ExpiresIn=3600,  # Set the expiration time for the URL (in seconds)
#             )
#
#             return Response({'download_url': presigned_url}, status=status.HTTP_200_OK)
#         except Exception as e:
#             logging.error(e)
#             return Response({'error': 'Failed to generate download link'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class S3DownloadFile(APIView):
    def get(self, request, folder_name):
        try:
            # Use temporary AWS credentials from your IAM role
            sts_client = boto3.client('sts')
            assumed_role = sts_client.assume_role(
                RoleArn=settings.AWS_ROLE_ARN,
                RoleSessionName='AssumeRoleSession'
            )

            s3_client = boto3.client(
                's3',
                aws_access_key_id=assumed_role['Credentials']['AccessKeyId'],
                aws_secret_access_key=assumed_role['Credentials']['SecretAccessKey'],
                aws_session_token=assumed_role['Credentials']['SessionToken']
            )

            # Specify your S3 bucket name
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME

            # List objects in the specified folder
            response = s3_client.list_objects_v2(
                Bucket=bucket_name,
                Prefix=f"{folder_name}/"
            )

            # Extract file keys from the response
            file_keys = [obj['Key'] for obj in response.get('Contents', [])]

            # Generate presigned URLs for each file
            presigned_urls = []
            for file_key in file_keys:
                presigned_url = s3_client.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': bucket_name, 'Key': file_key},
                    ExpiresIn=3600  # Set the expiration time for the URL (in seconds)
                )
                presigned_urls.append({'file_key': file_key, 'download_url': presigned_url})

            return Response({'download_urls': presigned_urls}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to generate download links'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
class S3ListFiles(APIView):
    def get(self, request):
        try:
            # Replace 'your-bucket-name' with your actual S3 bucket name
            bucket_name = settings.AWS_STORAGE_BUCKET_NAME
            s3 = boto3.client('s3')

            # List objects in the specified bucket
            response = s3.list_objects_v2(Bucket=bucket_name)

            # Extract file keys from the response
            files = [obj['Key'] for obj in response.get('Contents', [])]

            return Response({'Files': files}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to list files'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class S3DeleteFile(APIView):
    def delete(self, request, file_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.delete_object(Bucket=AWS_STORAGE_BUCKET_NAME, Key=file_name)
            return Response({'message': f'File {file_name} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to delete file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class S3DeleteBucket(APIView):
    def delete(self, request, bucket_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.delete_bucket(Bucket=bucket_name)
            return Response({'message': f'Bucket {bucket_name} deleted successfully'},
                            status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to delete bucket'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
