from django import forms
from .models import ContactSubmission

class ContactForm(forms.ModelForm):
    website = forms.CharField(required=False, widget=forms.HiddenInput)  # honeypot
    consent = forms.BooleanField(required=True, label="I consent to the use of my information to respond to this inquiry.")

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "organization", "country", "inquiry_type", "subject", "message", "consent"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 7, "maxlength": 5000}),
        }

    def clean(self):
        cleaned = super().clean()
        if cleaned.get("website"):
            raise forms.ValidationError("Invalid submission.")
        return cleaned

class DOIImportForm(forms.Form):
    doi = forms.CharField(
        max_length=260,
        label="DOI",
        help_text="Example: 10.1000/example or https://doi.org/10.1000/example",
    )
