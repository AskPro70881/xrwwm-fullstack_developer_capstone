from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views

app_name = 'djangoapp'

urlpatterns = [
    path('analyzereview', views.analyze_review, name='analyzereview'),

    path('login', views.login_user, name='login'),
    path('logout', views.logout_user, name='logout'),
    path('getdealers', views.get_dealerships, name='getdealers'),
    path('getdealersbyState/<str:state>', views.get_dealers_by_state, name='getdealersbystate'),
    path('getdealerbyid/<int:dealer_id>', views.get_dealer_by_id, name='getdealerbyid'),
    path('reviews/dealer/<int:dealer_id>', views.get_dealer_reviews, name='dealerreviews'),
    path('dealer/<int:dealer_id>', views.get_dealer_by_id, name='dealer'),
    path('getallcarmakes', views.get_car_makes, name='getallcarmakes'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
