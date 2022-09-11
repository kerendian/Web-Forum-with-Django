from django.contrib.auth.models import User
from ..models import Board, Topic, Post
from django.urls import resolve, reverse
from django.test import TestCase
from ..views import home
from ..views import home, board_topics,new_topic
from ..forms import NewTopicForm

class HomeTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(name='Django', description='Django board.')
        url = reverse('home')
        self.response = self.client.get(url)
    '''
    This is a very simple test case but extremely useful. We are testing the status code of the response. The status code 200 means success.
    '''
    def test_home_view_status_code(self):
        self.assertEquals(self.response.status_code, 200)
    '''
    we are making use of the resolve function. Django uses it to match a requested URL with a list of URLs listed in the urls.py module. 
    This test will make sure the URL /, which is the root URL, is returning the home view.
    '''
    def test_home_url_resolves_home_view(self):
        view = resolve('/')
        self.assertEquals(view.func, home)
    #  testing if the response body has the text href="/boards/1/"
    def test_home_view_contains_link_to_topics_page(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': self.board.pk})
        self.assertContains(self.response, 'href="{0}"'.format(board_topics_url)) # method to test if the response body contains a given text

class BoardTopicsTests(TestCase):
    '''
     In the setup method, we created a Board instance to use in the tests. We have to do that because the Django testing suite doesn't 
     run your tests against the current database. To run the tests Django creates a new database on the fly, applies all the model migrations, 
     runs the tests, and when done, destroys the testing database.
     **** So in the setUp method, we prepare the environment to run the tests, so to simulate a scenario.
    '''
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')

    # testing if Django is returning a status code 200 (success) for an existing Board.
    def test_board_topics_view_success_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 1}) # reverses the 
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)

    # testing if Django is returning a status code 404 (page not found) for a Board that doesn’t exist in the database.
    def test_board_topics_view_not_found_status_code(self):
        url = reverse('board_topics', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    # testing if Django is using the correct view function to render the topics.
    def test_board_topics_url_resolves_board_topics_view(self):
        view = resolve('/boards/1/')
        self.assertEquals(view.func, board_topics)

    def test_board_topics_view_contains_navigation_links(self):
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        homepage_url = reverse('home')
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})

        response = self.client.get(board_topics_url)

        self.assertContains(response, 'href="{0}"'.format(homepage_url))
        self.assertContains(response, 'href="{0}"'.format(new_topic_url))

class NewTopicTests(TestCase):
    # creates a Board instance to be used during the tests. included the User.objects.create_user to create a User instance to be used in the tests.
    def setUp(self):
        Board.objects.create(name='Django', description='Django board.')
        User.objects.create_user(username='john', email='john@doe.com', password='123')

    # check if the request to the view is successful
    def test_new_topic_view_success_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 200)
    
    # check if the view is raising a 404 error when the Board does not exist
    def test_new_topic_view_not_found_status_code(self):
        url = reverse('new_topic', kwargs={'pk': 99})
        response = self.client.get(url)
        self.assertEquals(response.status_code, 404)

    # check if the right view is being used
    def test_new_topic_url_resolves_new_topic_view(self):
        view = resolve('/boards/1/new/')
        self.assertEquals(view.func, new_topic)

    # ensure the navigation back to the list of topics
    def test_new_topic_view_contains_link_back_to_board_topics_view(self):
        new_topic_url = reverse('new_topic', kwargs={'pk': 1})
        board_topics_url = reverse('board_topics', kwargs={'pk': 1})
        response = self.client.get(new_topic_url)
        self.assertContains(response, 'href="{0}"'.format(board_topics_url))

    # since the CSRF Token is a fundamental part of processing POST requests, we have to make sure our HTML contains the token.
    def test_csrf(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        self.assertContains(response, 'csrfmiddlewaretoken')

    # sends a valid combination of data and check if the view created a Topic instance and a Post instance.
    def test_new_topic_valid_post_data(self):
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': 'Test title',
            'message': 'Lorem ipsum dolor sit amet'
        }
        response = self.client.post(url, data)
        self.assertTrue(Topic.objects.exists())
        self.assertTrue(Post.objects.exists())
    
    # here we are sending an empty dictionary to check how the application is behaving.
    def test_new_topic_invalid_post_data(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        self.assertEquals(response.status_code, 200)

    # similar to the previous test, but this time we are sending some data. The application is expected to validate and reject empty subject and message.
    def test_new_topic_invalid_post_data_empty_fields(self):
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        data = {
            'subject': '',
            'message': ''
        }
        response = self.client.post(url, data)
        self.assertEquals(response.status_code, 200)
        self.assertFalse(Topic.objects.exists())
        self.assertFalse(Post.objects.exists())

    def test_contains_form(self):  # <- new test
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.get(url)
        form = response.context.get('form')
        self.assertIsInstance(form, NewTopicForm) #Basically we are grabbing the form instance in the context data, and checking if it is a NewTopicForm

    def test_new_topic_invalid_post_data(self):  # <- updated this one
        '''
        Invalid post data should not redirect
        The expected behavior is to show the form again with validation errors
        '''
        url = reverse('new_topic', kwargs={'pk': 1})
        response = self.client.post(url, {})
        form = response.context.get('form')
        self.assertEquals(response.status_code, 200)
        self.assertTrue(form.errors) #to make sure the form is showing errors when the data is invalid