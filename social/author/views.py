from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from author.models import Author
from post.models import Post
from django.contrib.auth.models import User
from django.db.models import Q
from . import forms
import sys


# Create your views here.


@login_required(login_url='/author/')
def index(request):
    # This page displays the author's stream/post feed.
    # https://docs.djangoproject.com/en/1.10/topics/db/queries/
    author = Author.objects.get(id=request.user)
    context = {'author': author}
    # Get all post objects that are public and private
    # TODO: Add to the query to expand the feed.
    try:
        posts = Post.objects.all().order_by('-publishDate')
    except:
        return HttpResponse(sys.exc_info[0])

    try:
        if (len(posts) > 0):
            context['posts'] = posts
            return render(request, 'author/index.html', context)
    except:
        return HttpResponse(sys.exc_info[0])

    return render(request, 'author/index.html', context)


@login_required(login_url='/author_post/')
def author_post(request):
    # Only process the author's post if it is a POST request
    if (request.method != 'POST'):
        return HttpResponseRedirect('/author/')

    if (request.POST['post_content'] is None):
        return

    try:
        # Get the logged in user and the associated author object.
        # userContext = User.objects.get(username=request.user.username)
        # post_body = request.POST['post_content']

        authorContext = Author.objects.get(id=request.user)

        # Create and save a new post.
        newPost = Post(author=authorContext,
                       content=request.POST['post_content'],
                       privacyLevel=request.POST['privacy_level'])
        newPost.save()
    except:
        return HttpResponse(sys.exc_info[0])

    return HttpResponseRedirect('/author/')


# Implementation based upon the code found here
# http://stackoverflow.com/questions/19754103/django-how-to-delete-an-object-using-a-view
@login_required(login_url='/author_delete_post/')
def author_delete_post(request, postpk):
    # Only process the request if it is in fact a request to delete the post

    if (request.method != 'POST'):
        return HttpResponseRedirect('/author/')

    try:
        # Get the post object that the user is trying to delete.
        the_post = Post.objects.get(id=postpk)
        user = request.user
        postauthor = the_post.author

        # Verify that the user was the author of that post
        if user.id != postauthor.id.id:
            return HttpResponseForbidden()

        # Delete the post
        the_post.delete()
    except:
        HttpResponse(sys.exc_info[0])

    return HttpResponseRedirect('/profile/')


@login_required(login_url='/profile/')
def profile(request, id):
    # This page displays the author's profile.
    user = User.objects.get(id=id)
    author = Author.objects.get(id=user)
    context = {'author': author}

    try:
        posts = Post.objects.filter(
            Q(author__id=author.id)
            ).order_by('-publishDate')
    except:
        return HttpResponse(sys.exc_info[0])

    try:
       if (len(posts) > 0):
           context['posts'] = posts
    except:
        return HttpResponse(sys.exc_info[0])

    return render(request, 'author/profile.html', context)

@login_required(login_url='/edit/')
def edit(request):
    authorContext = Author.objects.get(id=request.user)
    return render(request, 'author/edit.html', {'author':authorContext})



@login_required(login_url='/edit_post/')
def edit_post(request):
    # This page edits the author's profile

    if (request.method != 'POST'):
        return HttpReponseRedirect('/edit/')

    editForm = forms.EditForm(request.POST)


    if (not editForm.is_valid()):
        return HttpResponse('<h1>Form not valid</h1>')

    authorContext = Author.objects.get(id=request.user)


    try:
        authorContext.firstname = editForm.cleaned_data['firstname']
        authorContext.lastname = editForm.cleaned_data['lastname']
        authorContext.phone = editForm.cleaned_data['phone']
        authorContext.dob = editForm.cleaned_data['dob']
        authorContext.gender = editForm.cleaned_data['gender']
        authorContext.gitURL = editForm.cleaned_data['gitURL']

        authorContext.save()

    except:
        return HttpResponse(sys.exc_info[0])

    return HttpResponseRedirect('/author/')
