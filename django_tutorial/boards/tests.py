from django.urls import resolve, reverse
from django.test import TestCase
from .views import home
from .views import home, board_topics
from .models import Board

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
