from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json

from .models import Job, Application


# ================= AUTH =================

# Signup
def signup_page(request):
    if request.method == "POST":
        username = request.POST['username'].replace(" ", "")
        email = request.POST['email']
        password = request.POST['password']

        User.objects.create_user(username=username, email=email, password=password)
        return redirect('/login/')

    return render(request, 'login/signup.html')


# Login
def login_page(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return render(request, 'login/login.html', {'error': 'Invalid credentials'})

    return render(request, 'login/login.html')


# ================= MAIN PAGES =================

# Dashboard
@login_required
def dashboard(request):
    jobs = Job.objects.all()
    return render(request, 'login/dashboard.html', {'jobs': jobs})


# Jobs Page
@login_required
def jobs(request):
    jobs = Job.objects.all()
    return render(request, 'login/jobs.html', {'jobs': jobs})


# Apply Job (WORKING VERSION)
@login_required
def apply_job(request, job_id):
    if request.method == "POST":
        job = get_object_or_404(Job, id=job_id)

        # prevent duplicate applications
        already_applied = Application.objects.filter(
            user=request.user, job=job
        ).exists()

        if not already_applied:
            Application.objects.create(user=request.user, job=job)

        print("APPLIED:", request.user.username, job.title)

    return redirect('/dashboard/')


# ================= OTHER PAGES =================

def home(request):
    return render(request, 'login/home.html')


@login_required
def profile(request):
    return render(request, 'login/profile.html')


@login_required
def applications(request):
    apps = Application.objects.filter(user=request.user)
    return render(request, 'login/applications.html', {'apps': apps})


def index(request):
    return render(request, 'login/index.html')


# ================= API (POSTMAN) =================

# GET Jobs API
def jobs_api(request):
    jobs = Job.objects.all()

    data = []
    for job in jobs:
        data.append({
            "id": job.id,
            "title": job.title,
            "company": job.company,
            "description": job.description,
            "eligibility": job.eligibility,
        })

    return JsonResponse(data, safe=False)


# POST Login API
@csrf_exempt
def login_api(request):
    if request.method == "POST":
        data = json.loads(request.body)

        username = data.get("username")
        password = data.get("password")

        user = authenticate(request, username=username, password=password)

        if user:
            return JsonResponse({
                "status": "success",
                "message": "Login successful"
            })
        else:
            return JsonResponse({
                "status": "error",
                "message": "Invalid credentials"
            })