from django.shortcuts import render,redirect, get_object_or_404
from .models import Board, Topic, Post
from .forms import NewTopicForm
from django.http import Http404
from django.contrib.auth.models import User

def home(request):
    boards = Board.objects.all() # The result is a QuerySet - We can treat this QuerySet like a list
    return render(request, 'home.html', {'boards': boards})

def board_topics(request, pk):
    try:
        board = Board.objects.get(pk=pk) # PK stands for Primary Key. It's a shortcut for accessing a model's primary key.
    except Board.DoesNotExist:
        raise Http404
    return render(request, 'topics.html', {'board': board})

def board_topics(request, pk):
    board = get_object_or_404(Board, pk=pk) # PK stands for Primary Key. It's a shortcut for accessing a model's primary key.
    return render(request, 'topics.html', {'board': board})

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
            topic.starter = user
            topic.save() 
            post = Post.objects.create(
                message=form.cleaned_data.get('message'),
                topic=topic,
                created_by=user
            )
            return redirect('board_topics', pk=board.pk)  # TODO: redirect to the created topic page
    else: # request.method == 'GET'
        form = NewTopicForm()
    return render(request, 'new_topic.html', {'board': board, 'form': form})