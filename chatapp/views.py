from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password, check_password
from .utils import generateID
from datetime import datetime
from .models import Room, Message, RoomUser
from django.http import JsonResponse, HttpResponse, Http404
from functools import wraps


# Create your views here.


def prevent_direct_access(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        # Check if the request has a referer header
        referer = request.META.get('HTTP_REFERER')

        # If referer is not present or it's from an external source, redirect
        if not referer or not referer.startswith(request.build_absolute_uri('/')[:-1]):
            messages.error(request, 'You cannot access that page!')
            # Redirect to the home page or any other page
            return redirect('home')

        # If the request came from a valid source, proceed with the original view
        return view_func(request, *args, **kwargs)

    return _wrapped_view


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def home(request):
    context = {
        'title': 'SimpleChat - Home'
    }
    return render(request, 'home.html', context)


def login_user(request):
    context = {
        'title': 'Login'
    }
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')

        if not User.objects.filter(username=username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/login/')

        user = authenticate(username=username, password=password)

        if user is None:
            messages.error(request, 'Wrong Password')
            return redirect('/login/')

        else:
            login(request, user)
            return redirect('/')

    return render(request, 'login.html', context)


@prevent_direct_access
def logout_user(request):
    logout(request)
    return redirect('/login/')


def signup_user(request):
    context = {
        'title': 'Sign Up'
    }
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        username = username.lower()
        password = request.POST.get('password')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.error(request, 'Username Already Taken')
            return redirect('/signup/')
        else:
            user = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                email=email,
                username=username)

            user.set_password(password)
            user.save()
            messages.success(request, 'Account Created Successfully!')

            return render(request, 'login.html', {'title': 'Login'})

    return render(request, 'signup.html', context)


@login_required(login_url='/login/')
def createRoom(request):
    if request.method == "POST":
        roomID = request.POST.get('room_id')
        creator = request.user.username
        name = request.POST.get('roomname')
        password = request.POST.get('password')
        created = datetime.now()

        password = make_password(password)

        newroom = Room.objects.create(
            creator=creator,
            roomID=roomID,
            name=name,
            created=created,
            admin=creator,
            password=password
        )

        newroom.save()

        user = RoomUser.objects.create(
            user=creator,
            room=roomID,
            joined=datetime.now()
        )

        user.save()

        return redirect(f'/room/{roomID}')

    context = {
        'title': 'Create Room',
        "generated_room_id": generateID()
    }
    return render(request, 'createRoom.html', context=context)


@login_required(login_url='/login/')
def joinRoom(request):
    context = {
        'title': 'Join Room'
    }
    if request.method == "POST":
        roomID = request.POST.get('roomID')
        password = request.POST.get('password')

        if not Room.objects.filter(roomID=roomID).exists():
            messages.error(request, 'Room Does Not Exist!')
            return redirect('/joinRoom/')

        room = Room.objects.filter(roomID=roomID)[0]

        flag = check_password(password, room.password)

        if not flag:
            messages.error(request, 'Wrong Password')
            return redirect('/joinRoom/')

        if RoomUser.objects.filter(user=request.user.username, room=roomID):
            return redirect(f'/room/{roomID}/')

        user = RoomUser.objects.create(
            user=request.user.username,
            room=roomID,
            joined=datetime.now()
        )

        user.save()

        return redirect(f'/room/{roomID}/')

    return render(request, 'joinRoom.html', context)


@login_required(login_url='/login/')
def room(request, roomID):
    if not RoomUser.objects.filter(user=request.user.username, room=roomID).exists():
        messages.error(
            request, 'You cannot open a room that you have not joined!')
        messages.error(
            request, 'If you want to join the room, join it through password')
        return redirect('/')
    room = Room.objects.filter(roomID=roomID)[0]
    if not room:
        messages(request, 'The room was deleted by the creator')
        return redirect('/')
    name = room.name

    context = {
        'title': f'Room - {room.roomID}',
        'room': roomID,
        'room_name': name
    }
    return render(request, 'room.html', context)


@prevent_direct_access
def send(request):
    if request.method == 'POST':
        user = request.POST.get('user')
        content = request.POST.get('content')
        room = request.POST.get('room')

        if content:
            new_message = Message.objects.create(
                user=user,
                content=content,
                time=datetime.now(),
                room=room
            )
            new_message.save()

            return HttpResponse('Sent')
        return HttpResponse('Failed')

    return HttpResponse('Done')


@prevent_direct_access
def getMessages(request, roomID):
    msgs = Message.objects.filter(room=roomID)
    msgs = list(msgs.values())

    for i in range(len(msgs)):
        if (msgs[i]['user'] == request.user.username):
            msgs[i]['user'] = 'You'

    return JsonResponse({"messages": msgs})


@login_required(login_url='/login/')
def userProfile(request):
    context={
        'title':request.user.username
    }
    roomuser = RoomUser.objects.filter(user=request.user.username)

    if not roomuser:
        return render(request, 'userProfile.html', context)

    roomuser = list(RoomUser.objects.filter(user=request.user.username))
    rooms = []
    for i in range(len(roomuser)):
        roomID = roomuser[i].room
        room = Room.objects.filter(roomID=roomID)[0]
        rooms.append(room)

    context = {
        'title': request.user.username,
        'rooms': rooms
    }

    return render(request, 'userProfile.html', context)


@login_required(login_url='/login/')
def roomDetails(request, roomID):
    if not RoomUser.objects.filter(user=request.user.username, room=roomID).exists():
        messages.error(
            request, 'You cannot open a room that you have not joined!')
        messages.error(
            request, 'If you want to join the room, join it through password')
        return redirect('/')
    if request.method == 'POST':
        name = request.POST.get('name')
        room = Room.objects.filter(roomID=roomID)[0]

        room.name = name
        room.save()
        messages.success(request, f'Name changed to {name}')
        return redirect(f'/roomDetails/{roomID}/')

    room = Room.objects.filter(roomID=roomID)[0]
    if not room:
        messages(request, 'The room was deleted by the creator')
        return redirect('/')
    members = RoomUser.objects.filter(room=roomID)
    members = list(members)

    context = {
        'room': room,

        'title': f'Room Details - {roomID}',
        'members': members,
        'thisUser': request.user.username


    }

    return render(request, 'roomDetails.html', context)


@prevent_direct_access
@login_required(login_url='/login/')
def editProfile(request):
    context = {
        'title': f'Edit Profile - {request.user.username}'
    }
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')

        user = request.user

        if username != request.user.username and User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('/editProfile/')

        if email != request.user.email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already taken')
            return redirect('/editProfile/')

        if email != request.user.email and User.objects.filter(email=email).exists():
            messages.error(request, 'Email already taken')
            return redirect('/editProfile/')

        user.save()

        messages.success(request, 'Information updated successfully!')
        return redirect('/userProfile/')

    return render(request, 'editProfile.html', context)


@prevent_direct_access
@login_required(login_url='/login/')
def changePassword(request):
    context = {
        'title': f'Change Password - {request.user.username}'
    }
    if request.method == 'POST':
        oldPassword = request.POST.get('oldPassword')
        newPassword = request.POST.get('newPassword')
        confirmPassword = request.POST.get('confirmPassword')

        user = request.user

        if not check_password(oldPassword, user.password):
            messages.error(request, 'Old password is wrong')
            return redirect('/changePassword/')

        if newPassword != confirmPassword:
            messages.error(
                request, 'Passwords do not match. Please confirm the password again')
            return redirect('/changePassword/')

        # Update the password
        user.set_password(newPassword)
        user.save()

        messages.success(request, 'Password changed successfully')
        messages.success(request, 'Please Login With Your Password')
        return redirect('/userProfile/')

    return render(request, 'changePassword.html', context)


@prevent_direct_access
@login_required(login_url='/login/')
def deleteAccount(request):
    user = User.objects.get(username=request.user.username)

    rooms = RoomUser.objects.filter(user=user.username)

    if not rooms:
        logout(request)
        user.delete()
        messages.success(request, 'Your Account Has Been Deleted Successfully')
        return redirect('/login/')

    for room in rooms:
        room.delete()

    logout(request)
    user.delete()
    messages.success(request, 'Your Account Has Been Deleted Successfully')
    return redirect('/login/')


@prevent_direct_access
@login_required(login_url='/login/')
def deleteRoom(request, roomID):
    room = Room.objects.get(roomID=roomID)
    members = list(RoomUser.objects.filter(room=roomID))
    msgs = list(Message.objects.filter(room=roomID))

    for member in members:
        member.delete()

    for msg in msgs:
        msg.delete()

    room.delete()
    messages.success(request, 'Room Has Been Deleted Successfully!')
    return redirect('/')


@prevent_direct_access
@login_required(login_url='/login/')
def leaveRoom(request, roomID):
    room = Room.objects.get(roomID=roomID)
    memberToBeDeleted = RoomUser.objects.filter(
        room=roomID, user=request.user.username)[0]
    members = list(RoomUser.objects.filter(
        room=roomID))

    if len(members) == 1:
        Allmembers = list(RoomUser.objects.filter(room=roomID))
        msgs = list(Message.objects.filter(room=roomID))

        for member in Allmembers:
            member.delete()

        for msg in msgs:
            msg.delete()

        room.delete()
        messages.success(request, 'Room Has Been Deleted Successfully!')
        return redirect('/')

    if request.user.username == room.admin:
        room.admin = members[1].user
        room.save()

    memberToBeDeleted.delete()
    messages.success(
        request, f"You have successfully left the room '{room.name}'")
    return redirect('/')


@prevent_direct_access
@login_required(login_url='/login/')
def removeMember(request, roomID, member):
    room = Room.objects.get(roomID=roomID)
    user = RoomUser.objects.filter(room=roomID, user=member)[0]

    user.delete()
    messages.success(
        request, f"You have successfully removed {member} from the room ")
    return redirect(f'/roomDetails/{roomID}/')


@prevent_direct_access
@login_required(login_url='/login/')
def check_membership(request, roomID):
    is_member = RoomUser.objects.filter(
        user=request.user.username, room=roomID).exists()
    if not is_member:
        messages.error(request, 'You have been removed by the admin')
    return JsonResponse({'is_member': is_member})
