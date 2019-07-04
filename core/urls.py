from django.urls import path
from .views import item_list, products, CheckoutView, HomeView, ItemDetailView, add_to_cart,remove_from_cart, OrderSumary, remove_single_item_from_cart, PaymentView

app_name = 'core'
urlpatterns = [
    path('', HomeView.as_view(), name='item_list' ),
    path('product/<slug>/', ItemDetailView.as_view(), name='product' ),
    path('order-sumary/', OrderSumary.as_view(), name='order-sumary' ),
    path('checkout/', CheckoutView.as_view(), name='checkout' ),
    path('add_to_cart/<slug>/', add_to_cart, name='add_to_cart' ),
    path('remove_from_cart/<slug>/', remove_from_cart, name='remove_from_cart' ),
    path('remove_single_item_from_cart/<slug>/', remove_single_item_from_cart, name='remove_single_item_from_cart' ),
    path('payment/', PaymentView.as_view(), name='payment' )
]