from crispy_forms.helper import FormHelper
from crispy_forms import layout, bootstrap
from django import forms
from mptt.forms import TreeNodeMultipleChoiceField

from .models import *


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['product', 'title', 'content', 'image']

