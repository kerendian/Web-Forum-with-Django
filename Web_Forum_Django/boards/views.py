from audioop import reverse
from django.shortcuts import render,redirect, get_object_or_404
from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView
from django.utils import timezone
from django.views.generic import UpdateView, ListView
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# same like home() function but with using a GCBV for models listing
class BoardListView(ListView):
    model = Board
    # The context_object_name attribute on a generic view specifies the context variable to use instead of using the object_list it will be the same object_list
    #  but with context_object_name that we will pick - it makes the code more readble.
    context_object_name = 'boards'
    template_name = 'home.html'
# here The template will be rendered against a context containing a variable called object_list that contains all the board objects
# def home(request):
#     boards = Board.objects.all() # The result is a QuerySet - We can treat this QuerySet like a list
#     return render(request, 'home.html', {'boards': boards})

'''
Why object_list? This is the name of the variable that ListView returns to us.
You see the object_list above? It is not a very friendly name? To make it more user-friendly, 
we can provide instead an explicit name using context_object_name.
'''
class TopicListView(ListView):
    model = Topic
    context_object_name = 'topics'
    template_name = 'topics.html'
    paginate_by = 20

    '''
    Generally, get_context_data will merge the context data of all parent classes with those of the current class.
    To preserve this behavior in your own classes where you want to alter the context, you should be sure to call get_context_data on the super class
    -------------------------
    get_context_data() - This method is used to populate a dictionary to use as the template context. 
    For example, ListViews will populate the result from get_queryset() as object_list. 
    You will probably be overriding this method most often to add things to display in your templates.
    '''
    def get_context_data(self, **kwargs):
        # Add in the board 
        kwargs['board'] = self.board
        # Call the base implementation first to get a context
        return super().get_context_data(**kwargs)
    '''
    get_context_data() is used to generate dict of variables that are accessible in template. queryset is Django ORM queryset that consists of model instances

    Default implementation of get_context_data() in ListView adds return value of get_queryset() 
    (which simply returns self.queryset by default) to context as objects_list variable.
    ---------------------------
    get_queryset() - Used by ListViews - it determines the list of objects that you want to display. 
    By default, it will just give you all for the model you specify. 
    By overriding this method you can extend or completely replace this logic.
    '''
    def get_queryset(self):
        self.board = get_object_or_404(Board, pk=self.kwargs.get('pk'))
        queryset = self.board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
        return queryset

# def board_topics(request, pk):
#     board = get_object_or_404(Board, pk=pk)
#     queryset = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1)
#     page = request.GET.get('page', 1)
#     # Here we are telling Django to paginate our QuerySet in pages of 20 topics each.
#     paginator = Paginator(queryset, 20)

#     try:
#         topics = paginator.page(page)
#     except PageNotAnInteger:
#         # fallback to the first page
#         topics = paginator.page(1)
#     except EmptyPage:
#         # probably the user tried to add a page number
#         # in the url, so we fallback to the last page
#         topics = paginator.page(paginator.num_pages)

#     return render(request, 'topics.html', {'board': board, 'topics': topics})
# def board_topics(request, pk):
#     board = get_object_or_404(Board, pk=pk) # PK stands for Primary Key. It's a shortcut for accessing a model's primary key.
#     topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1) 
#     return render(request, 'topics.html', {'board': board, 'topics': topics})
class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'topic_posts.html'
    paginate_by = 20
    #  kwargs as being a dictionary that maps each keyword to the value that we pass alongside it
    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True     
        # its a way to update the topic ForeignKey of the Post model 
        kwargs['topic'] = self.topic
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, board__pk=self.kwargs.get('pk'), pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset



@login_required #Django has a built-in view decorator to avoid non-loged in users
def new_topic(request, pk):
    board = get_object_or_404(Board, pk=pk)
    user = User.objects.first()  # TODO: get the currently logged in user
    #  **** the core of the form processing
    # First we check if the request is a POST or a GET
    if request.method == 'POST':
        # instantiate a form instance passing the POST data to the form
        # If the request was a GET, we just initialize a new and empty form using form = NewTopicForm()
        form = NewTopicForm(request.POST)
        # check if the form is valid if we can save it in the database
        if form.is_valid():
            # save the data in the database. The save() method returns an instance of the Model saved into the database. 
            # since this is a Topic form, it will return the Topic that was created:
            topic = form.save(commit=False)
            topic.board = board
            topic.starter = request.user
            topic.save() 
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=request.user
            )
            # Very important: in the view reply_topic we are using topic_pk because we are referring to 
            # the keyword argument of the function, in the view new_topic we are using topic.pk because a topic
            #  is an object (Topic model instance)and .pk we are accessing the pk property of the Topic model instance. 
            return redirect('topic_posts', pk=pk, topic_pk=topic.pk)
    else: # request.method == 'GET'
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})

def topic_posts(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    topic.views += 1
    topic.save()
    return render(request, 'topic_posts.html', {'topic': topic})

# A new view protected by @login_required and with a simple form processing logic:
@login_required
# pk and topic_pk are query arguments from the URL
def reply_topic(request, pk, topic_pk):
    topic = get_object_or_404(Topic, board__pk=pk, pk=topic_pk)
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.created_by = request.user
            post.save()

            topic.last_updated = timezone.now()
            topic.save()

            topic_url = reverse('topic_posts', kwargs={'pk': pk, 'topic_pk': topic_pk})
            topic_post_url = '{url}?page={page}#{id}'.format(
                url=topic_url,
                id=post.pk,
                page=topic.get_page_count()
            )

            return redirect(topic_post_url)
    else:
        form = PostForm()
    return render(request, 'reply_topic.html', {'topic': topic, 'form': form})

@method_decorator(login_required, name='dispatch')
class PostUpdateView(UpdateView):
    model = Post
    fields = ('message', )
    template_name = 'edit_post.html'
    pk_url_kwarg = 'post_pk'
    context_object_name = 'post'
    # The application should only authorize the owner of the post to edit it.
    # The easiest way to solve this problem is by overriding the get_queryset method of the UpdateView.
    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(created_by=self.request.user)
    # override the form_valid() method so as to set some extra fields such as the updated_by and updated_at.
    def form_valid(self, form):
        post = form.save(commit=False)
        post.updated_by = self.request.user
        post.updated_at = timezone.now()
        post.save()
        return redirect('topic_posts', pk=post.topic.board.pk, topic_pk=post.topic.pk)