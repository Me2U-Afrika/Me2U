from django import forms
from mptt.forms import TreeNodeMultipleChoiceField


class MultipleChoiceTreeField(TreeNodeMultipleChoiceField):
    widget = forms.CheckboxSelectMultiple()

    def label_from_instance(self, obj):
        return obj
