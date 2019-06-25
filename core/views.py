from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Item, OrderItem, Order
from django.views.generic import ListView, DetailView
from django.utils import timezone
def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'product-page.html', context)

def checkout(request):
    return render(request,'checkout-page.html')

def item_list(request):
    context = {
        "items": Item.objects.all()
    }
    return render(request,"home-page.html", context)
# Create your views here.
class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by=1
    context_object_name = "list_items"

class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'

def add_to_cart(request, slug):
    item = get_object_or_404(Item,slug=slug) #get item in Item that has slug = slug
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False
    ) # item here is a field in OrderItem model
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity +=1
            order_item.save()
            messages.info(request,"item has been added 1 more to your cart")
        else:
            order.items.add(order_item)
            messages.info(request,"item has been added to your cart")
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date= ordered_date)
        order.items.add(order_item)
        messages.info(request,"item has been added to your cart")
    return redirect("core:product",slug=slug)

def remove_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    # item here is a field in OrderItem model
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        #check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "item was removed")
        else:
            #add a message saying the user does not contain this  order item
            messages.info(request,"user does not contain this  order item")
            return redirect("core:product",slug=slug)
    else:
        #add a message saying the user does not have an order
        messages.info(request,"user  does not have an order")
        return redirect("core:product",slug=slug)
    return redirect("core:product",slug=slug)
