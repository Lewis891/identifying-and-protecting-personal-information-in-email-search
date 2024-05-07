from decimal import Decimal
from django.db.models import Q
from django.forms import TextInput, NumberInput
import django_filters
from .models import EmailDataTable

class EmailFilter(django_filters.FilterSet):
    File = django_filters.CharFilter(label="File...", lookup_expr="icontains", widget=TextInput(attrs=
        {
            "class": "filter-form",
        }))
    To = django_filters.CharFilter(label="To...", lookup_expr="icontains", widget=TextInput(attrs=
        {
            "class": "filter-form",
        }))
    From = django_filters.CharFilter(label="From...", lookup_expr="icontains", widget=TextInput(attrs=
        {
            'class': 'filter-form',
        }))
    Body = django_filters.CharFilter(label="Body...", lookup_expr="icontains", widget=TextInput(attrs=
        {
            'class': 'filter-form',
        }))
    preds_rf = django_filters.CharFilter(label="RF Predicted...",  widget=TextInput(attrs=
        {
            'class': 'filter-form',
        }))
    topic = django_filters.CharFilter(label="Tm Predicted...", widget=TextInput(attrs=
        {
            'class': 'filter-form',
        }))
    class Meta:
        model = EmailDataTable
        fields = ["File","To","From","Body","preds_rf","topic"]

    def filter_decimal(self, queryset, name, value):
        lower_bound = "__".join([name, "gte"])
        upper_bound = "__".join([name, "lt"])
        upper_value = math.floor(value) + Decimal(1)

        return queryset.filter(**{lower_bound: value, upper_bound: upper_value})