from conversations.models import Message
from django import forms


class AddMessageForm(forms.Form):

    message = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Enter your message"}),
    )
