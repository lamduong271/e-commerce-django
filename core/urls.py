from django.urls import path
from .views import item_list, products, checkout, HomeView, ItemDetailView, add_to_cart,remove_from_cart

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='item_list' ),
    path('product/<slug>/', ItemDetailView.as_view(), name='product' ),
    path('checkout/', checkout, name='checkout' ),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart' ),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart' )  
]