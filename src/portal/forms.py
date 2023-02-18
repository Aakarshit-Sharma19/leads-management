from django import forms


class DeleteOlderLogEntriesForm(forms.Form):
    timeframe = forms.DateField(required=True, label='Delete entries older than:')

    class Meta:
        widgets = {
            'timeframe': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }