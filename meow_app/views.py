from django.db.models import Count
from django.http import Http404
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from .forms import AuthenticateForm, RegistrationForm, MeowForm
from .models import Meow

# Create your views here.


def index(request, auth_form=None, user_form=None):
    if request.user.is_authenticated():
        meow_form = MeowForm()
        user = request.user
        meows_self = Meow.objects.filter(user=user.id)
        # meows_buddies = Meow.objects.filter(user__userprofile__in=user.profile.follows.all)
        meows = meows_self # | meows_buddies

        return render(request,
                      'buddies.html',
                      {'meow_form': meow_form,
                       'user': user,
                       'meows': meows,
                       'next_url': '/',
                      })
    else:
        auth_form = auth_form or AuthenticateForm()
        user_form = user_form or RegistrationForm()

        return render(request,
                      'home.html',
                      {'auth_form': auth_form,
                       'user_form': user_form,
                      })


def login_view(request):
    if request.method == 'POST':
        form = AuthenticateForm(data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect('/')
        else:
            return index(request, auth_form=form)
    return redirect('/')


def logout_view(request):
    logout(request)
    return redirect('/')


def signup(request):
    user_form = RegistrationForm(data=request.POST)
    if request.method == 'POST':
        if user_form.is_valid():
            a = user_form.cleaned_data
            username = a['username']
            password = a['password2']
            user_form.save()
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('/')
        else:
            return index(request, user_form=user_form)
    return redirect('/')


@login_required
def public(request, meow_form=None):
    meow_form = meow_form or MeowForm()
    meows = Meow.objects.reverse()[:10]
    return render(request,
                  'public.html',
                  {'meow_form': meow_form,
                   'next_url': '/meows',
                   'meows': meows,
                   'username': request.user.username}
                  )


@login_required
def submit(request):
    if request.method == 'POST':
        meow_form = MeowForm(data=request.POST)
        next_url = request.POST.get('next_url', '/')
        if meow_form.is_valid():
            meow = meow_form.save(commit=False)
            meow.user = request.user
            meow.save()
            return redirect(next_url)
        else:
            return public(request, meow_form)
    return redirect('/')


def get_latest(user):
    try:
        return user.meow_set.order_by('-id')[0]
    except IndexError:
        return ""


@login_required
def users(request, username="", meow_form=None):
    if username:
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise Http404
        meows = Meow.objects.filter(user=user.id)
        if username == request.user.username or request.user.profile.follows.filter(user__username=username):
            # Self Profile or buddies' profile
            return render(request, 'user.html', {'user': user, 'meows': meows, })
        return render(request, 'user.html', {'user': user, 'meows': meows, 'follow': True, })
    users = User.objects.all().annotate(meow_count=Count('meow'))
    meows = map(get_latest, users)
    obj = zip(users, meows)
    meow_form = meow_form or MeowForm()
    return render(request,
                  'profiles.html',
                  {'obj': obj, 'next_url': '/users/',
                   'meow_form': meow_form,
                   'username': request.user.username, })


@login_required
def follow(request):
    if request.method == "POST":
        follow_id = request.POST.get('follow', False)
        if follow_id:
            try:
                user = User.objects.get(id=follow_id)
                request.user.profile.follows.add(user.profile)
            except ObjectDoesNotExist:
                return redirect('/users/')
    return redirect('/users/')
