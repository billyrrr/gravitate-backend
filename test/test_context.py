from webtest import TestApp
import unittest
import gravitate.main as main

app = TestApp(main.app)
# app.authorization = ('Bearer','')

class HelloWorldTest(unittest.TestCase):
    def test_index(self):
        """Tests that the index page for the application

        The page should be served as: Content-Type: text/html
        The body content should contain the string: Hello World!
        """
        response = app.get('/hello')
        self.assertEqual(response.content_type, 'text/html')
        self.assertIn('Hello World!', response.text)

# class NoAuthTest(unittest.TestCase):
#     def test_reject_auth(self):
#         """Tests that the index page for the application

#         The page should be served as: Content-Type: text/html
#         The body content should contain the string: Hello World!
#         """
#         response = app.post_json('/notes', dict(id=1, value='value'))
#         print(response.request)
#         self.assertEqual(response.content_type, 'text/html')
#         self.assertIn('Hello World!', response.text)
