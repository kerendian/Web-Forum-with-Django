from django.shortcuts import render, get_object_or_404
from .models import Board
from django.http import Http404

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