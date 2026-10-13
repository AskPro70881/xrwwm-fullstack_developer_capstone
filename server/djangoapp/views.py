# Uncomment the required imports before adding the code

# from django.shortcuts import render
# from django.http import HttpResponseRedirect, HttpResponse
# from django.contrib.auth.models import User
# from django.shortcuts import get_object_or_404, render, redirect
# from django.contrib.auth import logout
# from django.contrib import messages
# from datetime import datetime

from django.http import JsonResponse
from django.contrib.auth import login, authenticate
import logging
import json
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
# from .populate import initiate


# Get an instance of a logger
logger = logging.getLogger(__name__)


# Create your views here.

# Create a `login_request` view to handle sign in request
@csrf_exempt
def login_user(request):
    # Get username and password from request.POST dictionary
    data = json.loads(request.body)
    username = data['userName']
    password = data['password']
    # Try to check if provide credential can be authenticated
    user = authenticate(username=username, password=password)
    data = {"userName": username}
    if user is not None:
        # If user is valid, call login method to login current user
        login(request, user)
        data = {"userName": username, "status": "Authenticated"}
    return JsonResponse(data)

@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({'status': 'Logged out'})

# Create a `logout_request` view to handle sign out request
# def logout_request(request):
# ...

# Create a `registration` view to handle sign up request
# @csrf_exempt
# def registration(request):
# ...

def get_dealerships(request):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    return JsonResponse({'status': 200, 'dealers': data['dealerships']})


def get_dealer_by_id(request, dealer_id):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    for dealer in data['dealerships']:
        if dealer['id'] == dealer_id:
            return JsonResponse({'status': 200, 'dealer': [dealer]})
    return JsonResponse({'status': 404, 'dealer': []}, status=404)


def get_dealer_reviews(request, dealer_id):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'reviews.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    reviews = [
        r for r in data.get('reviews', [])
        if r.get('dealership') == dealer_id
    ]
    for review in reviews:
        review['sentiment'] = 'neutral'
    return JsonResponse({'status': 200, 'reviews': reviews})

def get_car_makes(request):
    import json
    from pathlib import Path
    from django.http import JsonResponse

    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'car_records.json'

    with open(data_file, 'r') as f:
        data = json.load(f)

    return JsonResponse(data)

@csrf_exempt
def analyze_review(request):
    import json
    from django.http import JsonResponse

    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    data = json.loads(request.body)
    review = data.get('review', '')

    positive_words = ['fantastic', 'great', 'excellent', 'good', 'wonderful', 'amazing', 'love']
    negative_words = ['bad', 'poor', 'terrible', 'awful', 'hate', 'worst']

    text = review.lower()
    score = sum(word in text for word in positive_words) - sum(word in text for word in negative_words)
    sentiment = 'positive' if score > 0 else ('negative' if score < 0 else 'neutral')

    return JsonResponse({'review': review, 'sentiment': sentiment})


def get_dealers_by_state(request, state):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    dealers = [d for d in data['dealerships'] if d.get('state', '').lower() == state.lower()]
    return JsonResponse({'status': 200, 'dealers': dealers})
