from django.shortcuts import render

# appname/views.py

import logging
import os
from django.http import JsonResponse
from django.core.files.base import ContentFile
from rest_framework.views import APIView

from rest_framework.response import Response
from rest_framework import status
import boto3

from empins2023.settings import AWS_STORAGE_BUCKET_NAME, BASE_DIR


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

class S3UploadFile(APIView):
    def post(self, request):
        file = request.FILES.get('file')
        if file:
            s3_client = boto3.client('s3')
            object_name = file.name
            try:
                s3_client.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, object_name)
                return Response({'message': f'File {object_name} uploaded successfully'}, status=status.HTTP_201_CREATED)
            except Exception as e:
                logging.error(e)
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

