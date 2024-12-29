from django.shortcuts import render, redirect
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm


def loginPage(request):
    page = 'login'
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method=="POST":
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, 'User does not exist!')
            
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Username or password does not exist')
        
    context={'page':page}
    
    return render(request, 'base/login_register.html', context)
    
    
def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    page = 'register'
    form = UserCreationForm
    context = {'page':page, 'form':form}
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Something went wrong!")
            
    return render(request, 'base/login_register.html', context)
    
    
def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q)|
        Q(name__icontains=q)|
        Q(description__icontains=q)|
        Q(host__username__icontains=q)
    )
    
    room_comments = Message.objects.filter(
        Q(room__topic__name__icontains=q)|
        Q(room__name__icontains=q)
    ).order_by('-created')
    
    room_count = rooms.count()
    topics = Topic.objects.all()
    context = {
        'rooms':rooms,
        'topics': topics, 
        'room_count':room_count,
        'room_comments':room_comments
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk) 
    comments = room.message_set.all().order_by('-created')  
    participants = room.participants.all()
    
    if request.method == "POST":
        comment = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body')
        ) 
        room.participants.add(request.user)
        return redirect('room', pk=room.id)
    
    context = {
        'room':room, 
        'comments':comments,
        'participants':participants,
    }
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    topics = Topic.objects.all()
    room_comments = user.message_set.all()
    context = {
        'user':user,
        'rooms':rooms,
        'room_comments':room_comments,
        'topics':topics
    }
    return render(request, 'base/profile.html', context)


@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()
    
    if request.method=='POST':
        print(request.POST)
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')
            
    context = {'form':form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)
    
    if request.user != room.host:
        return HttpResponse('You can not update the room!')
    
    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
        return redirect('home')
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)


@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)
    
    if request.user != room.host:
        return HttpResponse('You can not update the room!')
    
    if request.method == 'POST':
        room.delete()
        return redirect('home') 
    return render(request, 'base/delete.html', {'obj':room})


@login_required(login_url='login')
def deleteComment(request, pk):
    comment = Message.objects.get(id=pk)
    room_id = comment.room.id
    print(f"This is the room : {room_id}")
    if request.user != comment.user:
        return HttpResponse('You can not delete the comment!')
    
    if request.method == 'POST':
        comment.delete()
        return redirect('home') 
    
    return render(request, 'base/delete.html', {'obj':comment})

