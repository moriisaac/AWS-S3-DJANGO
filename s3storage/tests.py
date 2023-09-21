from django.test import TestCase

# s3storage/tests.py

import json
import os
from django.test import TestCase, override_settings
from rest_framework import status
from rest_framework.test import APIClient
from moto import mock_s3

@mock_s3
@override_settings(AWS_STORAGE_BUCKET_NAME='chamahub')
class S3ViewsTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_list_buckets(self):
        response = self.client.get('/list-buckets/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = json.loads(response.content)
        self.assertIn('buckets', data)

    def test_create_bucket(self):
        data = {'bucket_name': 'testbucket'}
        response = self.client.post('/create-bucket/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_upload_file(self):
        # Create a test file to upload
        file_path = os.path.join(os.path.dirname(__file__), 'test_file.txt')
        with open(file_path, 'w') as f:
            f.write('This is a test file.')

        with open(file_path, 'rb') as file:
            data = {'file': file}
            response = self.client.post('/upload-file/', data, format='multipart')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_download_file(self):
        # Upload a test file first
        self.test_upload_file()

        response = self.client.get('/download-file/test_file.txt/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delete_file(self):
        # Upload a test file first
        self.test_upload_file()

        response = self.client.delete('/delete-file/test_file.txt/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_bucket(self):
        data = {'bucket_name': 'testbucket'}
        response = self.client.post('/create-bucket/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.delete('/delete-bucket/testbucket/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

