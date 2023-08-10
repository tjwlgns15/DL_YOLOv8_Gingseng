from django import forms

class UploadImageForm(forms.Form):
    image_files = forms.ImageField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    state = forms.CharField(max_length=20)
    category_variety = forms.CharField(max_length=20)
    category_age = forms.CharField(max_length=10)
    category_grade = forms.CharField(max_length=10)