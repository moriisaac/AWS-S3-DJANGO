# s3storage/urls.py

from django.urls import path
from .views import S3ListBucket, S3CreateBucket, S3UploadFile, S3DownloadFile, S3DeleteFile, S3DeleteBucket

urlpatterns = [
    path('list-buckets/', S3ListBucket.as_view(), name='list-buckets'),
    path('create-bucket/', S3CreateBucket.as_view(), name='create-bucket'),
    path('upload-file/', S3UploadFile.as_view(), name='upload-file'),
    path('download-file/<str:file_name>/', S3DownloadFile.as_view(), name='download-file'),
    path('delete-file/<str:file_name>/', S3DeleteFile.as_view(), name='delete-file'),
    path('delete-bucket/<str:bucket_name>/', S3DeleteBucket.as_view(), name='delete-bucket'),
]
