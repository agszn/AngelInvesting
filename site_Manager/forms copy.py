from django import forms
from django.forms import inlineformset_factory
from unlisted_stock_marketplace.models import *

class CustomFieldDefinitionForm(forms.ModelForm):
    class Meta:
        model = CustomFieldDefinition
        fields = ['stock', 'table_title', 'model_type', 'custom_model_name', 'unit']

CustomFieldValueFormSet = inlineformset_factory(
    CustomFieldDefinition,
    CustomFieldValue,
    fields=['name', 'description', 'int_value', 'dec_value', 'char_value', 'date_value', 'text_style', 'table_header', 'parent_field_value'],
    extra=5,
    can_delete=True
)


from django import forms
from .models import Broker, Advisor

from django import forms
from .models import Broker

class BrokerForm(forms.ModelForm):
    class Meta:
        model = Broker
        fields = ['broker_id', 'name', 'email', 'contact']
        widgets = {
            'broker_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter unique broker ID (e.g., BRK001)'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter broker name'
            }),
            # 'pan': forms.TextInput(attrs={
            #     'class': 'form-control',
            #     'placeholder': 'Enter PAN number (optional)'
            # }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address'
            }),
            'contact': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter contact number'
            }),
        }


from django import forms
from .models import Advisor

class AdvisorForm(forms.ModelForm):
    class Meta:
        model = Advisor
        fields = ['advisor_type']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['advisor_type'].widget.attrs.update({'class': 'form-control'})

# StockData
from django import forms
from django.forms import inlineformset_factory


CATEGORY_CHOICES = [
    ("Unlisted", "Unlisted"),
    ("Pre-IPO", "Pre-IPO"),
    ("Delisted", "Delisted"),
]

DEPOSITORY_CHOICES = [
    ("NSDL", "NSDL"),
    ("CDSL", "CDSL"),
    ("NSDL/CDSL", "NSDL/CDSL"),
]

class StockDataForm(forms.ModelForm):
    # Render DRHP as a dropdown (Yes/No) but store as boolean
    drhp_filed = forms.ChoiceField(
        choices=(("True", "Yes"), ("False", "No")),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Category dropdown
    category = forms.ChoiceField(
        choices=[("", "---------")] + CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    # Available On dropdown
    available_on = forms.ChoiceField(
        choices=[("", "---------")] + DEPOSITORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={"class": "form-select"})
    )

    class Meta:
        model = StockData
        fields = "__all__"
        widgets = {
            # Column 5
            "company_name": forms.TextInput(attrs={"class": "form-control"}),
            "scrip_name": forms.TextInput(attrs={"class": "form-control"}),
            "logo": forms.ClearableFileInput(attrs={"class": "form-control"}),

            # Column 6
            "pan_no": forms.TextInput(attrs={"class": "form-control"}),
            "isin_no": forms.TextInput(attrs={"class": "form-control"}),
            "cin": forms.TextInput(attrs={"class": "form-control"}),

            # Column 7
            "sector": forms.TextInput(attrs={"class": "form-control"}),

            # Column 8
            "registration_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"),

            # Read-only groups (Cols 1–3) + Column 4 editable
            "share_price": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),   # Yesterday Price
            "ltp": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),           # Today Price
            "partner_price": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),

            "outstanding_shares": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "market_capitalization": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),

            "pe_ratio": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "ps_ratio": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "pbv": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),
            "eps": forms.NumberInput(attrs={"class": "form-control", "readonly": "readonly"}),

            "face_value": forms.NumberInput(attrs={"class": "form-control"}),
            "book_value": forms.NumberInput(attrs={"class": "form-control"}),

            # Other existing fields (unchanged)
            "profit": forms.NumberInput(attrs={"class": "form-control"}),
            "profit_percentage": forms.NumberInput(attrs={"class": "form-control"}),
            "week_52_high": forms.NumberInput(attrs={"class": "form-control"}),
            "week_52_low": forms.NumberInput(attrs={"class": "form-control"}),
            "lifetime_high": forms.NumberInput(attrs={"class": "form-control"}),
            "lifetime_high_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"),
            "lifetime_low": forms.NumberInput(attrs={"class": "form-control"}),
            "lifetime_low_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}, format="%Y-%m-%d"),
            "day_high": forms.NumberInput(attrs={"class": "form-control"}),
            "day_low": forms.NumberInput(attrs={"class": "form-control"}),
            "lot": forms.NumberInput(attrs={"class": "form-control"}),
            "quantity": forms.NumberInput(attrs={"class": "form-control"}),
            "conviction_level": forms.Select(attrs={"class": "form-select"}),
            "number_of_times_searched": forms.NumberInput(attrs={"class": "form-control"}),
            "gst_no": forms.TextInput(attrs={"class": "form-control"}),

            "description": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "company_overview": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "registered_office_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
            "transfer_agent_address": forms.Textarea(attrs={"class": "form-control", "rows": 2}),

            "stock_type": forms.Select(attrs={"class": "form-select"}),
            "youtube_video_link": forms.URLInput(attrs={"class": "form-control", "placeholder": "https://youtube.com/..."}),
        }
        labels = {
            "company_name": "Brand Name",
            "isin_no": "ISIN",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Pre-select dropdowns from instance values (ModelForm does this,
        # but we normalize boolean->string for drhp_filed dropdown)
        if self.instance and self.instance.pk is not None:
            self.fields["drhp_filed"].initial = "True" if bool(self.instance.drhp_filed) else "False"

    def clean_drhp_filed(self):
        # Convert dropdown string back to boolean for the model
        val = self.cleaned_data.get("drhp_filed")
        return val == "True"


# ===================== Inline Formsets =====================

ReportFormSet = inlineformset_factory(
    StockData,
    Report,
    fields=("title", "summary"),
    extra=1,
    can_delete=True,
    widgets={
        "title": forms.TextInput(attrs={"class": "form-control"}),
        "summary": forms.Textarea(attrs={"class": "form-control", "rows": 2}),
    }
)

ShareholdingPatternFormSet = inlineformset_factory(
    StockData,
    ShareholdingPattern,
    fields=("shareholder_name", "number_of_shares", "percentage_of_total"),
    extra=1,
    can_delete=True,
    widgets={
        "shareholder_name": forms.TextInput(attrs={"class": "form-control"}),
        "number_of_shares": forms.NumberInput(attrs={"class": "form-control"}),
        "percentage_of_total": forms.NumberInput(attrs={"class": "form-control"}),
    }
)

CompanyRelationFormSet = inlineformset_factory(
    StockData,
    CompanyRelation,
    fields=("company_name", "relation_type", "percentage_shares_held"),
    extra=1,
    can_delete=True,
    widgets={
        "company_name": forms.TextInput(attrs={"class": "form-control"}),
        "relation_type": forms.Select(attrs={"class": "form-select"}),
        "percentage_shares_held": forms.NumberInput(attrs={"class": "form-control"}),
    }
)

PrincipalBusinessActivityFormSet = inlineformset_factory(
    StockData,
    PrincipalBusinessActivity,
    fields=("product_service_name", "nic_code", "turnover_percentage"),
    extra=1,
    can_delete=True,
    widgets={
        "product_service_name": forms.TextInput(attrs={"class": "form-control"}),
        "nic_code": forms.TextInput(attrs={"class": "form-control"}),
        "turnover_percentage": forms.NumberInput(attrs={"class": "form-control"}),
    }
)


from django import forms
from .models import Blog

class BlogForm(forms.ModelForm):
    class Meta:
        model = Blog
        fields = ['banner', 'date', 'heading', 'subtitle', 'short_description', 'full_description']
        widgets = {
            'date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'  # Ensure correct format for HTML5
            ),
            'short_description': forms.Textarea(attrs={'rows': 3}),
            'full_description': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super(BlogForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.date:
            self.fields['date'].initial = self.instance.date.strftime('%Y-%m-%d')


# stock history
# app/forms.py

class StockHistoryForm(forms.ModelForm):
    class Meta:
        model = StockHistory
        fields = ["stock", "price", "timestamp"]
        widgets = {
            "timestamp": forms.DateInput(attrs={"type": "date"}),
        }

# events forms
from django import forms
from .models import Event

from django import forms
from .models import Event

from django import forms
from .models import Event
from django import forms
from .models import Event
# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from .models import Event
# forms.py
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import Event

# Accept common PDF MIME variants (some browsers use octet-stream)
PDF_MIME_TYPES = {
    "application/pdf",
    "application/x-pdf",
    "application/acrobat",
    "applications/vnd.pdf",
    "text/pdf",
    "text/x-pdf",
}


def _looks_like_pdf(f) -> bool:
    """
    Peek at the first bytes to verify PDF signature %PDF-
    """
    try:
        pos = f.tell()
    except Exception:
        pos = None
    try:
        head = f.read(5)
        return head == b"%PDF-"
    finally:
        try:
            if pos is not None:
                f.seek(pos)
        except Exception:
            pass


class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = [
            "stock",
            "title",
            "subtitle",
            "paragraph",
            "date_time",
            "image",
            "document",
            "show",
        ]
        widgets = {
            "stock": forms.Select(attrs={"class": "form-control"}),
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter event title"}),
            "subtitle": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter event subtitle"}),
            "paragraph": forms.Textarea(attrs={"class": "form-control", "rows": 5, "placeholder": "Enter event details"}),
            "date_time": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "image": forms.ClearableFileInput(attrs={"class": "form-control"}),
            "document": forms.ClearableFileInput(attrs={"class": "form-control", "accept": "application/pdf"}),
            "show": forms.CheckboxInput(attrs={"class": "form-check-input"}),
        }

    def clean_document(self):
        doc = self.cleaned_data.get("document")
        if not doc:
            return doc

        # Content-type check (be permissive with variants and octet-stream)
        ctype = getattr(doc, "content_type", None)
        if ctype and ctype not in PDF_MIME_TYPES and ctype != "application/octet-stream":
            raise ValidationError("Only PDF files are allowed.")

        # Magic header check (reliable verification)
        try:
            if not _looks_like_pdf(doc.file):
                raise ValidationError("The uploaded file is not a valid PDF.")
        except Exception:
            # Storage wrappers can vary; if we can't read, treat as invalid for safety
            raise ValidationError("The uploaded file is not a valid PDF.")

        return doc

    def clean_date_time(self):
        dt = self.cleaned_data.get("date_time")
        # Ensure timezone-aware datetime
        if dt and timezone.is_naive(dt):
            dt = timezone.make_aware(dt, timezone.get_current_timezone())
        return dt
