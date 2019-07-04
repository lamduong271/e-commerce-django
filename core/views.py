from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from .models import Item, OrderItem, Order, BillingAdress, Payment
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, View
from django.utils import timezone
from .forms import CheckoutForm
from django.conf import settings
import stripe
stripe.api_key = settings.STRIPE_KEY

def products(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, 'product-page.html', context)

class CheckoutView(View):
    def get(self, *args, **kwargs):
        checkout_form = CheckoutForm()
        context={
            'checkout_form':checkout_form
        }
        return render(self.request,'checkout-page.html', context)
    def post(self, *args, **kwargs):
        checkout_form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if checkout_form.is_valid():
                stress_address = checkout_form.cleaned_data.get('stress_address')
                apartment_address = checkout_form.cleaned_data.get('apartment_address')
                country = checkout_form.cleaned_data.get('country')
                zip = checkout_form.cleaned_data.get('zip')
                same_billing_address = checkout_form.cleaned_data.get('same_billing_address')
                save_info = checkout_form.cleaned_data.get('save_info')
                payment_option = checkout_form.cleaned_data.get('payment_option')
                billing_address = BillingAdress()(
                    user = self.request.user,
                    stress_address=stress_address,
                    apartment_address=apartment_address,
                    country=country,
                    zip=zip
                )
                billing_address.save()
                order.billing_address=billing_address
                order.save()
                return redirect('core:checkout')
            messages.warning(self.request,"failed checkout ")
            return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.error(self.request,"you dont have an order ")
            return redirect('/')

class PaymentView(View):
    def get(self, *args, **kwargs):
        return render(self.request,'payment.html')
    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        amount = order.get_total() * 100
        try:
            charge = stripe.Charge.create(
            amount = amount,
            currency = "usd",
            source = token, # obtained with Stripe.js
            )
            order.ordered=True
            #create the payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = amount
            payment.save()
            # assign payment to order
            order.ordered = True
            order.payment = payment
            order.save()
            messages.success(self.request, "Your order was successful")
            return redirect('/')
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err  = body.get('error', {})
            messages.error(self.request, f"{err.get('message')}")
            return redirect('/')
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate limit error")
            return redirect('/')
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid parameter")
            return redirect('/')
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication failed")
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network error")
            return redirect('/')
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            messages.error(self.request, "Somethig went wrong, you are not charged, please try again")
            return redirect('/')
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Somethig went wrong")
            return redirect('/')

def item_list(request):
    context = {
        "items": Item.objects.all()
    }
    return render(request,"home-page.html", context)
# Create your views here.
class HomeView(ListView):
    model = Item
    template_name = "home-page.html"
    paginate_by=10
    context_object_name = "list_items"

class OrderSumary(LoginRequiredMixin, View):
    def get(self,*args,**kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context={
                'order':order
            }
            return render(self.request, 'order-sumary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request,"you dont have an order ")
            return redirect('/')


class ItemDetailView(DetailView):
    model = Item
    template_name = 'product-page.html'

@login_required
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
            return redirect("core:order-sumary")
        else:
            order.items.add(order_item)
            messages.info(request,"item has been added to your cart")
            return redirect("core:order-sumary")
    else:
        order_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date= ordered_date)
        order.items.add(order_item)
        messages.info(request,"item has been added to your cart")
    return redirect("core:product",slug=slug)

@login_required
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
            return redirect("core:order-sumary")
        else:
            #add a message saying the user does not contain this  order item
            messages.info(request,"user does not contain this  order item")
            return redirect("core:product",slug=slug)
    else:
        #add a message saying the user does not have an order
        messages.info(request,"user  does not have an order")
        return redirect("core:product",slug=slug)
    return redirect("core:product",slug=slug)

@login_required
def remove_single_item_from_cart(request,slug):
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
            if order_item.quantity > 1:
                order_item.quantity -=1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "item qantity was updated")
            return redirect("core:order-sumary")
        else:
            #add a message saying the user does not contain this  order item
            messages.info(request,"user does not contain this  order item")
            return redirect("core:product",slug=slug)
    else:
        #add a message saying the user does not have an order
        messages.info(request,"user  does not have an order")
        return redirect("core:product",slug=slug)
    return redirect("core:product",slug=slug)
