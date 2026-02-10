from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from rest_framework.test import APIClient


CSV_CONTENT = b"""Session ID,Rider Name,Board Type,Wind Speed (km/h),Wave Height (m),Speed (km/h),Duration (minutes),Distance Covered (km),Water Temperature (\xc2\xb0C)\nS001,Alice,Freeride,22,1.2,28,45,21,18\n"""


class AnalyticsApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='demo', password='demo1234')
        token_resp = self.client.post('/api/auth/token/', {'username': 'demo', 'password': 'demo1234'}, format='json')
        token = token_resp.data['token']
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token}')

    def test_upload_and_summary(self):
        file = SimpleUploadedFile('sample.csv', CSV_CONTENT, content_type='text/csv')
        upload_resp = self.client.post('/api/upload/', {'file': file})
        self.assertEqual(upload_resp.status_code, 201)

        summary_resp = self.client.get('/api/summary/')
        self.assertEqual(summary_resp.status_code, 200)
        self.assertEqual(summary_resp.data['summary']['total_sessions'], 1)
