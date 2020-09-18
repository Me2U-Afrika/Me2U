from django.forms.widgets import Widget


class PlusMinusNumber(Widget):
    template_name = 'widgets/plusMinusNumber.html'

    class Media:
        css = {'all': ('css/plusminusnumber.css',)}
        js = ('js/plusminusnumber.js',)
