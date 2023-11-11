# s3storage/urls.py

from django.urls import path, include
from .views import S3ListBucket, S3CreateBucket, S3UploadFile, S3DownloadFile, S3DeleteFile, S3DeleteBucket
# from rest_framework_swagger.views import get_swagger_view
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

schema_view = get_schema_view(
    openapi.Info(
        title="AWS-S3 Amazon Storage Bucket API",
        default_version='v1',
        description="Store Your Files Securely using AWS-S3-Django API",
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/swagger', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),

    path('admin/doc/', include('django.contrib.admindocs.urls')),
    path('list-buckets/', S3ListBucket.as_view(), name='list-buckets'),
    path('create-bucket/', S3CreateBucket.as_view(), name='create-bucket'),
    path('upload-file/', S3UploadFile.as_view(), name='upload-file'),
    path('download-file/<str:file_name>/', S3DownloadFile.as_view(), name='download-file'),
    path('delete-file/<str:file_name>/', S3DeleteFile.as_view(), name='delete-file'),
    path('delete-bucket/<str:bucket_name>/', S3DeleteBucket.as_view(), name='delete-bucket'),
]
