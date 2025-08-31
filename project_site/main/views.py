from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import MessageBoard, Message
from django.db import connection
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

# flaw-1, A03:2021 - INJECTION: SQL Injection via direct string concatenation
def search_boards(request):
    query = request.GET.get('q', '')
    if query:
        cursor = connection.cursor()
        sql = f"SELECT * FROM main_messageboard WHERE title LIKE '%{query}%'"
        cursor.execute(sql)
        results = cursor.fetchall()
        return render(request, 'main/search_results.html', {'results': results, 'query': query})
    return render(request, 'main/search_results.html', {'results': [], 'query': query})

# flaw-1 fix
#@login_required
#def search_boards(request):
#    query = request.GET.get('q', '')
#    results = []
#    
#    if query:
#        messageboards = MessageBoard.objects.filter(
#            Q(title__icontains=query)
#        ).select_related('created_by')[:20]
#        
#        results = []
#        for board in messageboards:
#            result_tuple = (
#                board.id,
#                board.title,
#                board.created_at,
#                board.created_by.id if board.created_by else None,
#            )
#            results.append(result_tuple)
#        
#    return render(request, 'main/search_results.html', {
#        'results': results, 
#        'query': query
#    })


# flaw-2, A05:2021 - SECURITY MISCONFIGURATION: Exposing sensitive configuration data
def home(request):
    message_boards = MessageBoard.objects.all()
    debug_info = {
        'django_settings': {
            'SECRET_KEY': 'django-insecure-#ldh%#(g@4gh0ay!v*z85ku-5muuxp(c!3=y5ikq)sm3$(=r#_',
            'DEBUG': True,
            'DATABASE_PASSWORD': 'password'
        },
        'system_info': {
            'python_path': '/usr/bin/python',
            'server_version': 'Django 5.2.5'
        }
    }
    
    return render(request, 'main/home.html', {
        'message_boards': message_boards, 
        'debug_info': debug_info
    })

# flaw-2 fix
#def home(request):
#    message_boards = MessageBoard.objects.all()
#    return render(request, 'main/home.html', {
#        'message_boards': message_boards
#    })

@login_required
def create_board(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        if title:
            MessageBoard.objects.create(title=title, created_by=request.user)
            messages.success(request, 'Message board created successfully!')
        return redirect('home')

# flaw-3, A01:2021 - BROKEN ACCESS CONTROL: Missing authentication requirement
def board_detail(request, board_id):
    board = get_object_or_404(MessageBoard, id=board_id)
    board_messages = board.messages.all()
    
    if request.method == 'POST':
        content = request.POST.get('content')
        if content and request.user.is_authenticated:
            Message.objects.create(board=board, content=content, author=request.user)
            messages.success(request, 'Message posted successfully!')
            return redirect('board_detail', board_id=board_id)
    
    return render(request, 'main/board_detail.html', {
        'board': board,
        'board_messages': board_messages
    })
# flaw-3 fix, add @login_required decorator
#@login_required
#def board_detail(request, board_id):
#    board = get_object_or_404(MessageBoard, id=board_id)
#    board_messages = board.messages.all()
#    
#    if request.method == 'POST':
#        content = request.POST.get('content')
#        if content:  # request.user.is_authenticated ei tarvita, @login_required varmistaa
#            Message.objects.create(board=board, content=content, author=request.user)
#            messages.success(request, 'Message posted successfully!')
#            return redirect('board_detail', board_id=board_id)
#    
#    return render(request, 'main/board_detail.html', {
#        'board': board,
#        'board_messages': board_messages
#    })

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'main/login.html')

# flaw-4, A07:2021 - IDENTIFICATION AND AUTHENTICATION FAILURES
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        # No password strength validation
        if password1 != password2:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'main/register.html')
        
        # No username validation
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'main/register.html')
        
        # Accepting weak passwords
        user = User.objects.create_user(username=username, password=password1)
        
        # Auto-login without verification
        login(request, user)
        messages.success(request, 'Registration successful! You are now logged in.')
        return redirect('home')
    
    return render(request, 'main/register.html')

# flaw-4 fix, add validation and verification
#def register_view(request):
#    if request.method == 'POST':
#        username = request.POST.get('username', '').strip()
#        password1 = request.POST.get('password1', '')
#        password2 = request.POST.get('password2', '')
#        
#        if not all([username, password1, password2]):
#            messages.error(request, 'All fields are required.')
#            return render(request, 'main/register.html')
#        
#        if len(username) < 3 or len(username) > 30:
#            messages.error(request, 'Username must be between 3-30 characters.')
#            return render(request, 'main/register.html')
#        
#        if not username.isalnum():
#            messages.error(request, 'Username must contain only letters and numbers.')
#            return render(request, 'main/register.html')
#        
#        if password1 != password2:
#            messages.error(request, 'Passwords do not match.')
#            return render(request, 'main/register.html')
#        
#        if User.objects.filter(username=username).exists():
#            messages.error(request, 'Username already exists.')
#            return render(request, 'main/register.html')
#        
#        try:
#            validate_password(password1)
#        except ValidationError as e:
#            for error in e.messages:
#                messages.error(request, error)
#            return render(request, 'main/register.html')
#        
#        try:
#            user = User.objects.create_user(username=username, password=password1)
#            messages.success(request, 'Registration successful! Please log in.')
#            return redirect('login')
#        except Exception as e:
#            messages.error(request, 'Registration failed. Please try again.')
#            return render(request, 'main/register.html')
#    
#    return render(request, 'main/register.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out.')
    return redirect('home')

# flaw-5, A02:2021 - CRYPTOGRAPHIC FAILURES: Exposing sensitive user data without encryption
@login_required
def profile(request):
    user_data = {
        'username': request.user.username,
        'password': request.user.password,
        'email': request.user.email,
        'user_id': request.user.id,
        'is_superuser': request.user.is_superuser,
        'session_key': request.session.session_key
    }
    return render(request, 'main/profile.html', {'user_data': user_data})

# flaw-5 fix, remove sensitive data exposure
#@login_required
#def profile(request):
#    user_data = {
#        'username': request.user.username,
#        'date_joined': request.user.date_joined,
#        'last_login': request.user.last_login
#    }
#    
#    return render(request, 'main/profile.html', {'user_data': user_data})
