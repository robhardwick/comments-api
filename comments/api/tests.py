from django.test import TestCase
from django.conf import settings

from rest_framework.test import APIClient

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

    def test_comment_create(self):
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

    def test_comment_update(self):
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
