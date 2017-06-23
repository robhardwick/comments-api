import json
from unittest.mock import patch

from django.test import TestCase
from django.conf import settings

import requests
from rest_framework.test import APIClient

from .tasks import fetch_tone

class AppTestCase(TestCase):
    """ API tests """
    fixtures = ('comments.json', 'comment-tones.json',)

    def setUp(self):
        self.client = APIClient()

    def _test_first_comment(self, comment):
        """ Test the provided comment matches the content of the first comment from the fixtures """
        self.assertIn('url', comment)
        self.assertEqual(comment['url'], 'http://testserver/api/1/')

        self.assertIn('sku', comment)
        self.assertEqual(comment['sku'], 'TEST0001')

        self.assertIn('content', comment)
        self.assertEqual(comment['content'], 'I really love this product, it\'s the best!')

        self.assertIn('tone', comment)
        self.assertEqual(comment['tone'], 'joy')

    def test_comment_list(self):
        """ Test comments list"""

        # Perform request
        response = self.client.get('/api/', format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check the correct total number of results are returned
        self.assertIn('count', data)
        self.assertEqual(data['count'], 15)

        # Check the returned results list is correct
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        self.assertEqual(len(data['results']), settings.REST_FRAMEWORK['PAGE_SIZE'])

        # Check the first returned comment is correct
        self._test_first_comment(data['results'][0])

    def test_comment_retrieve(self):
        """ Test comment retrieval """

        # Perform request that should succeed
        response = self.client.get('/api/1/', format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check the returned comment is correct
        self._test_first_comment(data)

        # Perform request that should fail
        response = self.client.get('/api/9999/', format='json')
        self.assertEqual(response.status_code, 404)

    @patch('comments.api.tasks.fetch_tone')
    def test_comment_create(self, mock_task):
        """ Test comment creation """

        # Perform request that should succeed
        response = self.client.post('/api/', {'sku': 'TEST1234', 'content': 'Test 1234'}, format='json')
        self.assertEqual(response.status_code, 201)
        data = response.json()

        # Check the returned comment is correct
        self.assertIn('sku', data)
        self.assertEqual(data['sku'], 'TEST1234')

        self.assertIn('content', data)
        self.assertEqual(data['content'], 'Test 1234')

        self.assertIn('tone', data)
        self.assertIsNone(data['tone'])

        # Perform request that should fail
        response = self.client.post('/api/', {'sku': 'SKUTHATISTOOLONG', 'content': ''}, format='json')
        self.assertEqual(response.status_code, 400)
        data = response.json()

        # Check validation errors
        self.assertIn('sku', data)
        self.assertListEqual(data['sku'], ['Ensure this field has no more than 8 characters.'])

        self.assertIn('content', data)
        self.assertListEqual(data['content'], ['This field may not be blank.'])

    @patch('comments.api.tasks.fetch_tone')
    def test_comment_update(self, mock_task):
        """ Test comment updating """

        # Perform request that should succeed
        response = self.client.put('/api/1/', {'sku': 'TEST1234', 'content': 'Test 1234'}, format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check the returned comment is correct
        self.assertIn('sku', data)
        self.assertEqual(data['sku'], 'TEST1234')

        self.assertIn('content', data)
        self.assertEqual(data['content'], 'Test 1234')

        # Perform request that should fail
        response = self.client.put('/api/1/', {'sku': 'SKUTHATISTOOLONG', 'content': ''}, format='json')
        self.assertEqual(response.status_code, 400)
        data = response.json()

        # Check validation errors
        self.assertIn('sku', data)
        self.assertListEqual(data['sku'], ['Ensure this field has no more than 8 characters.'])

        self.assertIn('content', data)
        self.assertListEqual(data['content'], ['This field may not be blank.'])

    def test_comment_delete(self):
        """ Test comment deletion """

        # Perform request that should succeed
        response = self.client.delete('/api/1/', format='json')
        self.assertEqual(response.status_code, 204)

        # Perform request that should fail
        response = self.client.put('/api/9999/', format='json')
        self.assertEqual(response.status_code, 404)

    @patch('comments.api.tasks.logger')
    def test_comment_tone_unknown(self, mock_logger):
        """ Test comment tone creation for an unknown comment object """
        fetch_tone(9999)
        mock_logger.error.assert_called_with('Unknown comment object in fetch tone task: 9999')

    @patch('requests.get', side_effect=requests.exceptions.HTTPError())
    @patch('comments.api.tasks.logger')
    def test_comment_tone_request_failure(self, mock_logger, mock_requests):
        """ Test comment tone request failure """
        fetch_tone(1)
        mock_logger.error.assert_called_with('Error response received from Watson API: ')

    @patch('requests.get', side_effect=requests.exceptions.RequestException())
    @patch('comments.api.tasks.logger')
    def test_comment_tone_request_connection_failure(self, mock_logger, mock_requests):
        """ Test comment tone request connection failure """
        fetch_tone(1)
        mock_logger.error.assert_called_with('Error requesting from Watson API: ')

    @patch('requests.get')
    @patch('comments.api.tasks.logger')
    def test_comment_tone(self, mock_logger, mock_requests):
        """ Test comment tone creation """
        mock_requests.return_value.json.return_value = {
            "document_tone": {
                "tone_categories": [{
                    "tones": [
                        {"score": 0.24748, "tone_id": "anger"},
                        {"score": 0.322559, "tone_id": "disgust"},
                        {"score": 0.108639, "tone_id": "fear"},
                        {"score": 0.105358, "tone_id": "joy"},
                        {"score": 0.083174, "tone_id": "sadness"}
                    ],
                    "category_id": "emotion_tone",
                }]
            }
        }

        # Check fetch tone task succeeds
        fetch_tone(1)
        mock_logger.error.assert_not_called()

        # Perform request that should succeed
        response = self.client.get('/api/1/', format='json')
        self.assertEqual(response.status_code, 200)
        data = response.json()

        # Check the returned tone is correct
        self.assertIn('tone', data)
        self.assertEqual(data['tone'], 'disgust')
