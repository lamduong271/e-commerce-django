from django.urls import path
from .views import item_list, products, checkout, HomeView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='item_list' ),
    path('products/', products, name='product' ),
    path('checkout/', checkout, name='checkout' )  
]