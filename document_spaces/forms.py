from django import forms


class SpaceCreationConfirmationForm(forms.Form):
    confirmation_text = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'pattern': 'create space', 'placeholder': 'create space'}))

    def clean_confirmation_text(self):
        if self.cleaned_data.get('confirmation_text').lower() != 'create space':
            raise forms.ValidationError('Please type in the correct message')
