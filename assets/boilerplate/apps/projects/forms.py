from django import forms

from .models import Project


class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ("name",)
        widgets = {"name": forms.TextInput(attrs={"autofocus": True, "autocomplete": "off"})}


class ProjectFilterForm(forms.Form):
    q = forms.CharField(required=False, max_length=120, label="Cari nama proyek")
    status = forms.ChoiceField(
        required=False, choices=[("", "Semua status"), *Project.Status.choices], label="Status"
    )
