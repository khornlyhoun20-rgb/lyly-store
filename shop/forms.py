from django import forms
from django.conf import settings

from .models import ContactMessage, Order, Review
from .utils import normalize_phone


class BootstrapMixin:
    def _style_widgets(self):
        for field in self.fields.values():
            widget = field.widget
            if isinstance(widget, forms.RadioSelect):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.CheckboxInput):
                widget.attrs.setdefault("class", "form-check-input")
            elif isinstance(widget, forms.Select):
                widget.attrs.setdefault("class", "form-select")
            else:
                widget.attrs.setdefault("class", "form-control")


class CheckoutForm(BootstrapMixin, forms.Form):
    name = forms.CharField(label="Full name", min_length=2, max_length=120)
    phone = forms.CharField(
        label="Phone number",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "012 345 678", "type": "tel"}),
    )
    city = forms.ChoiceField(label="City / Province")
    address = forms.CharField(
        label="Street address",
        min_length=4,
        max_length=255,
        widget=forms.TextInput(attrs={"placeholder": "House no., street, landmark"}),
    )
    note = forms.CharField(
        label="Note (optional)", required=False, widget=forms.Textarea(attrs={"rows": 2})
    )
    payment = forms.ChoiceField(
        label="Payment",
        choices=Order.PAYMENT_CHOICES,
        initial="cod",
        widget=forms.RadioSelect,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["city"].choices = [("", "Select...")] + [
            (city, city) for city, _rate in settings.SHIPPING_RATES
        ]
        self._style_widgets()

    def clean_phone(self):
        return normalize_phone(self.cleaned_data["phone"])


class TrackOrderForm(BootstrapMixin, forms.Form):
    order_number = forms.CharField(
        label="Order number",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "LY-1234567"}),
    )
    phone = forms.CharField(
        label="Phone number",
        max_length=20,
        widget=forms.TextInput(attrs={"placeholder": "012 345 678", "type": "tel"}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_widgets()

    def clean_order_number(self):
        return self.cleaned_data["order_number"].strip().upper()

    def clean_phone(self):
        return normalize_phone(self.cleaned_data["phone"])


class ContactForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        labels = {"name": "Full name", "email": "Email address"}
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "Your name"}),
            "email": forms.EmailInput(attrs={"placeholder": "Your email"}),
            "message": forms.Textarea(attrs={"rows": 5, "placeholder": "How can we help?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_widgets()


class ReviewForm(BootstrapMixin, forms.ModelForm):
    class Meta:
        model = Review
        fields = ["name", "location", "rating", "text"]
        labels = {"name": "Your name", "location": "City (optional)", "text": "Your review"}
        widgets = {"text": forms.Textarea(attrs={"rows": 4})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._style_widgets()


class SubscribeForm(forms.Form):
    email = forms.EmailField()
