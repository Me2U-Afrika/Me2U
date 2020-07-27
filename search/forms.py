from .models import SearchTerm
from django import forms


class SearchForm(forms.ModelForm):
    class Meta:
        model = SearchTerm
        fields = ('q',)

    def __init__(self, *args, **kwargs):
        super(SearchForm, self).__init__(*args, **kwargs)
        default_text = 'Search Products, Brands & Categories'
        self.fields['q'].widget.attrs['value'] = default_text
        self.fields['q'].widget.attrs['onfocus'] = "if (this.value=='" + default_text + "')this.value = ''"
        self.fields['q'].widget.attrs['placeholder'] = default_text
        self.fields['q'].widget.attrs['class'] = 'input-group'
        self.fields['q'].widget.attrs['class'] = 'form-control'


#         < div
#
#         class ="input-group" >
#
#         < input
#         type = "text"
#
#         class ="form-control" placeholder="Search Order" name="article" >
#
#         < div
#
#         class ="input-group-btn" >
#
#         < button
#
#         class ="btn btn-default" type="submit" > Search < i class ="glyphicon glyphicon-search" > < / i > < / button >
#
#     < / div >
#
# < / div >


    include = ('q',)
