from .models import CarMake, CarModel
from .populate import initiate

from django.http import JsonResponse
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
import logging
import json
from pathlib import Path
from urllib.parse import unquote

logger = logging.getLogger(__name__)


@csrf_exempt
def login_user(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body or b'{}')
        username = data.get('userName', '')
        password = data.get('password', '')
    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    user = authenticate(username=username, password=password)

    if user is not None:
        login(request, user)
        return JsonResponse({
            'userName': username,
            'status': 'Authenticated'
        })

    return JsonResponse({
        'userName': username,
        'status': 'Invalid credentials'
    }, status=401)


@csrf_exempt
def logout_user(request):
    logout(request)
    return JsonResponse({
        "userName": "",
        "status": "Logged out"
    })


def registration(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body or b'{}')
        username = data.get('userName', data.get('username', ''))
        password = data.get('password', '')
        email = data.get('email', '')

        if not username or not password:
            return JsonResponse({'error': 'Username and password required'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        return JsonResponse({
            'userName': user.username,
            'status': 'Registered'
        }, status=201)

    except (json.JSONDecodeError, UnicodeDecodeError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)


def get_dealerships(request):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    return JsonResponse({
        'status': 200,
        'dealers': data['dealerships']
    })


def get_dealer_by_id(request, dealer_id):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)

    for dealer in data['dealerships']:
        if dealer['id'] == dealer_id:
            return JsonResponse({
                'status': 200,
                'dealer': [dealer]
            })

    return JsonResponse({
        'status': 404,
        'dealer': []
    }, status=404)


def get_dealer_reviews(request, dealer_id):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'reviews.json'
    with open(data_file, 'r') as f:
        data = json.load(f)

    reviews = [
        review for review in data.get('reviews', [])
        if review.get('dealership') == dealer_id
    ]

    for review in reviews:
        review.setdefault('sentiment', 'neutral')

    return JsonResponse({
        'status': 200,
        'reviews': reviews
    })


def get_car_makes(request):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'car_records.json'
    with open(data_file, 'r') as f:
        data = json.load(f)
    return JsonResponse(data)


@csrf_exempt
def analyze_review(request, review=None):
    if request.method == 'GET':
        review = unquote(review or '')
    elif request.method == 'POST':
        try:
            data = json.loads(request.body or b'{}')
            review = data.get('review', '')
        except (json.JSONDecodeError, UnicodeDecodeError):
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
    else:
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    positive_words = [
        'fantastic', 'great', 'excellent', 'good',
        'wonderful', 'amazing', 'love'
    ]
    negative_words = [
        'bad', 'poor', 'terrible', 'awful',
        'hate', 'worst'
    ]

    text = review.lower()
    score = (
        sum(word in text for word in positive_words)
        - sum(word in text for word in negative_words)
    )

    sentiment = (
        'positive' if score > 0
        else 'negative' if score < 0
        else 'neutral'
    )

    return JsonResponse({
        'review': review,
        'sentiment': sentiment
    })


def get_dealers_by_state(request, state):
    data_file = Path(__file__).resolve().parent.parent / 'database' / 'data' / 'dealerships.json'
    with open(data_file, 'r') as f:
        data = json.load(f)

    dealers = [
        dealer for dealer in data['dealerships']
        if dealer.get('state', '').lower() == state.lower()
    ]

    return JsonResponse({
        'status': 200,
        'dealers': dealers
    })


def get_cars(request):
    count = CarMake.objects.filter().count()
    if count == 0:
        initiate()
    car_models = CarModel.objects.select_related('car_make')
    cars = []
    for car_model in car_models:
        cars.append({"CarModel": car_model.name, "CarMake": car_model.car_make.name})
    return JsonResponse({"CarModels": cars})
