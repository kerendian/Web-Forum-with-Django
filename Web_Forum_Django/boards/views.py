from django.shortcuts import render,redirect, get_object_or_404
from .models import Board, Topic, Post
from .forms import NewTopicForm, PostForm
from django.http import Http404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.db.models import Count
from django.views.generic import UpdateView
from django.utils import timezone
from django.utils.decorators import method_decorator

def home(request):
    boards = Board.objects.all() # The result is a QuerySet - We can treat this QuerySet like a list
    return render(request, 'home.html', {'boards': boards})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk) # PK stands for Primary Key. It's a shortcut for accessing a model's primary key.
    topics = board.topics.order_by('-last_updated').annotate(replies=Count('posts') - 1) 
    return render(request, 'topics.html', {'board': board, 'topics': topics})

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
            return redirect('topic_posts', pk=pk, topic_pk=topic_pk)
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