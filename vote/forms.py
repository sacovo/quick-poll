from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit


class ImportForm(forms.Form):
    first_name = forms.CharField(initial='first_name',
                                 help_text="Column header for the first name")
    last_name = forms.CharField(initial='last_name')
    email = forms.CharField(initial='email')
    delegation = forms.CharField(initial='delegation')
    seperator = forms.CharField(initial=',')

    csv = forms.FileField()
    clear_delegates = forms.BooleanField(
        label="Clear delegates",
        help_text=
        "Delete all non-staff users and all delegates already present.",
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.add_input(Submit('Upload', 'Upload'))
