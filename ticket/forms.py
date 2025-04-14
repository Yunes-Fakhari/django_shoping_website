from django import forms
from .models import Ticket, TicketMessage, TicketAttachment

class TicketCreateForm(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['title', 'category', 'priority']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

class TicketMessageForm(forms.ModelForm):
    attachments = forms.FileField(
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control'}),
        label='پیوست‌ها (چند فایل قابل انتخاب است)',
        help_text='با نگه داشتن Ctrl می‌توانید چند فایل انتخاب کنید'
    )

    class Meta:
        model = TicketMessage
        fields = ['message', 'internal_note']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'متن پیام خود را وارد کنید...'
            }),
            'internal_note': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['attachments'].widget.attrs.update({'multiple': True})