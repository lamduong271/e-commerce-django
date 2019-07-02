from django_countries.fields import CountryField
from django import forms
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICE = (
    ('S', 'Stripe'),
    ('P','Paypal')
)
class CheckoutForm(forms.Form):
    stress_address = forms.CharField(widget = forms.TextInput(attrs={
        'placeholder':'123 Main st'
    }))
    apartment_address = forms.CharField(required=False, widget = forms.TextInput(attrs={
        'placeholder':'Apartment or suite'
    }))
    country = CountryField(blank_label='(Select country)').formfield(
        widget = CountrySelectWidget(attrs={
        'css':'custom-select d-block w-100'
    }))
    zip = forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control'
    }))
    same_billing_address = forms.BooleanField(widget=forms.CheckboxInput(attrs={
        'css':'custom-control-input'
    }))
    save_info = forms.BooleanField(widget=forms.CheckboxInput())
    payment_option = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICE)
