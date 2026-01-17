from django import forms
from .models import Forms, Branch


QR_CHOICES = [
    ('fonepay','Fonepay'),
    ('nepalpay','Nepalpay'),
]

# Main form
class FormForms(forms.ModelForm):
    submitter_email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    qr_channel = forms.ChoiceField(
        choices=QR_CHOICES,
        widget=forms.RadioSelect(attrs={'class':'form-check-input'}),
        required=True
    )
    signature = forms.CharField(required=False)

    agree_deposits = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'}),
        label="I agree to deposit Rs 1,000/- for Koili integration."
    )

    agree_pay = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'}),
        label="I agree to pay the monthly fee for Koili integration."
    )

    declare = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={'class':'form-check-input'}),
        label="I declare that in case of any damage, the Bank will not be responsible and that all details provided are correct."
    )
    branch = forms.ModelChoiceField(
        queryset=Branch.objects.all().order_by('name'),
        empty_label=None,  # keep None so no default blank
        widget=forms.Select(attrs={
            'class': 'form-control branch-select',
            'data-placeholder': 'Select or type branch'  # placeholder for Select2
        }),
        required=True
    )

    class Meta:
        model = Forms
        fields = [
            'merchant_name', 'account_number', 'mobile_number', 'pan', 'qr_channel',
            'agree_deposits', 'agree_pay', 'declare', 'date', 'name', 'signature',
            'branch', 'branch_staff_contact', 'submitter_email'
        ]
        widgets = {
            'merchant_name': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'account_number': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'mobile_number': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'pan': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'date': forms.TextInput(attrs={'class': 'form-control print-input', 'autocomplete': 'off'}),
            'name': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'signature': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'branch_staff_contact': forms.TextInput(attrs={'class': 'form-control print-input'}),
            'submitter_email': forms.EmailInput(attrs={'class': 'form-control print-input'}),
        }


# Custom widget for multiple files
class MultiFileInput(forms.FileInput):
    allow_multiple_selected = True


class FormAttachmentsForm(forms.Form):
    attachments = forms.FileField(
        widget=MultiFileInput(attrs={
            'class': 'form-control',
            'id': 'attachments_input',
            'multiple': True
        }),
        required=False,
        label="Attachments (max 1MB each)"
    )



