from .models import SearchTerm
from django import forms
from categories.models import Department


class SearchForm(forms.ModelForm):
    category_searched = forms.ModelChoiceField(queryset=None)

    class Meta:
        model = SearchTerm
        fields = ('q', 'category_searched',)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        default_text = 'Search Products, Brands & Categories'
        self.fields['q'].widget.attrs['value'] = default_text
        self.fields['q'].widget.attrs['onfocus'] = "if (this.value=='" + default_text + "')this.value = ''"
        self.fields['q'].widget.attrs['placeholder'] = default_text

        self.fields['q'].widget.attrs['class'] = "header_search_input"
        # self.fields['category_searched'].widget.attrs['class'] = "header_search_input"

        # self.fields['q'].widget.attrs['class'] = 'form-control'
        queryset_departments = Department.objects.all()

        self.fields['category_searched'].queryset = queryset_departments

    include = ('q',)

