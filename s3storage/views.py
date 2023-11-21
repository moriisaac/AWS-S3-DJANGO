from django.shortcuts import render

# appname/views.py

import logging
import os
from django.http import JsonResponse
from django.core.files.base import ContentFile
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
import boto3
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.response import Response
from rest_framework_api_key.permissions import HasAPIKey
from empins2023.settings import AWS_STORAGE_BUCKET_NAME, BASE_DIR

import logging
import boto3
from botocore.exceptions import ClientError
from django.core.files.uploadedfile import UploadedFile

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.core.files.uploadedfile import UploadedFile
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
    def post(self, request):
        file = request.FILES.get('file')
        if file:
            # Specify your S3 bucket name
            bucket_name = AWS_STORAGE_BUCKET_NAME

            if upload_file(file, bucket_name):
                return Response({'message': f'File {file.name} uploaded successfully'}, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Failed to upload file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({'error': 'No file provided'}, status=status.HTTP_400_BAD_REQUEST)


class S3DownloadFile(APIView):
    def get(self, request, file_name):
        s3_client = boto3.client('s3')
        try:
            s3_client.download_file(AWS_STORAGE_BUCKET_NAME, file_name, file_name)
            # Provide a download link to the file
            file_path = os.path.join(BASE_DIR, file_name)
            return Response({'file_path': file_path}, status=status.HTTP_200_OK)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to download file'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
            return Response({'message': f'Bucket {bucket_name} deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logging.error(e)
            return Response({'error': 'Failed to delete bucket'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

