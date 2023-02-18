from django import forms

from authentication.models import PortalUser
from document_spaces.validators import validate_google_xlsx_type, get_max_size_validator
from leads_data.models import DocumentSpace, Student


class SpaceCreationConfirmationForm(forms.Form):
    confirmation_text = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'pattern': 'create space', 'placeholder': 'create space'}))

    def clean_confirmation_text(self):
        if self.cleaned_data.get('confirmation_text').lower() != 'create space':
            raise forms.ValidationError('Please type in the correct message')


class SpaceUploadFileForm(forms.Form):
    error_messages = {
        'document_name_not_unique': 'File with the same name already exists.'
                                    '\nPlease choose different file'
    }

    def __init__(self, *args, **kwargs):
        self.user: PortalUser = kwargs.pop('user')
        self.space: DocumentSpace = kwargs.pop('space')
        super().__init__(*args, **kwargs)

    document = forms.FileField(widget=forms.ClearableFileInput(
        attrs={'class': 'form-control', 'placeholder': 'Excel file not more than 24 MB in size'}),
        validators=[validate_google_xlsx_type, get_max_size_validator(24 * 1024 * 1024)])

    def clean_document(self):
        if self.space.files.filter(file_name=self.cleaned_data['document'].name).exists():
            raise forms.ValidationError(self.error_messages['document_name_not_unique'],
                                        code='document_name_not_unique')


class SpaceDeleteFileForm(forms.Form):
    error_messages = {
        'name_not_correct': 'The file name is not correct'
    }

    def __init__(self, *args, **kwargs):
        self.expected_file_name = kwargs.pop('expected_file_name')
        super().__init__(*args, **kwargs)
        self.fields['file_name'].widget.attrs['pattern'] = self.expected_file_name

    file_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'placeholder': 'Enter the name of the file to delete'}))
    confirmation = forms.BooleanField(required=True, label='Are you sure you want to delete this file')

    def clean_file_name(self):
        if self.expected_file_name != self.cleaned_data['file_name']:
            raise forms.ValidationError(self.error_messages['name_not_correct'], code='name_not_correct')


class SpaceResponseSubmitForm(forms.Form):
    response = forms.CharField(required=True,
                               widget=forms.Textarea(
                                   attrs={'class': 'form-control', 'placeholder': 'Enter student\'s response'}))
    status = forms.ChoiceField(required=True,
                               choices=Student.STATUS_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))


class SpaceResponseUpdateForm(SpaceResponseSubmitForm):
    pass


class CreateSpaceUserForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.space: 'DocumentSpace' = kwargs.pop('space')
        super().__init__(*args, **kwargs)

    def save_user(self):
        user: PortalUser = super().save(commit=False)
        user.set_unusable_password()
        user.save()
        return user

    class Meta:
        model = PortalUser
        fields = ('first_name', 'last_name', 'email')
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter First Name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Last Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}),
        }


class CreateUserAsManagerForm(CreateSpaceUserForm):
    def save(self, commit=True):
        self.space.managers.add(self.save_user())


class CreateUserAsWriterForm(CreateSpaceUserForm):
    def save(self, commit=True):
        self.space.writers.add(self.save_user())


class ResolveEntryForm(forms.Form):
    confirmation = forms.BooleanField(initial=True, widget=forms.HiddenInput())
