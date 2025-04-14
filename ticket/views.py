from django.shortcuts import render
from django.shortcuts import render, redirect , get_object_or_404
from django.utils import timezone
from django.urls import reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import View
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from .models import Ticket, TicketMessage, TicketAttachment
from .forms import TicketCreateForm, TicketMessageForm

class TicketListView(LoginRequiredMixin, ListView):
    model = Ticket
    template_name = 'tickets/ticket_list.html'
    context_object_name = 'tickets'

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)

class TicketCreateView(LoginRequiredMixin, CreateView):
    model = Ticket
    form_class = TicketCreateForm
    template_name = 'tickets/ticket_create.html'
    success_url = reverse_lazy('tickets:list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

class TicketDetailView(LoginRequiredMixin, DetailView):
    model = Ticket
    template_name = 'tickets/ticket_detail.html'
    context_object_name = 'ticket'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['message_form'] = TicketMessageForm()
        return context

    def get_queryset(self):
        return Ticket.objects.filter(user=self.request.user)
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = self.get_form()
        
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def form_valid(self, form):
        # ذخیره پیام
        message = form.save(commit=False)
        message.ticket = self.object
        message.user = self.request.user
        message.save()

        # ذخیره فایل‌های پیوست
        files = self.request.FILES.getlist('attachments')
        for f in files:
            TicketAttachment.objects.create(
                ticket=self.object,
                message=message,
                file=f,
                file_size=f.size
            )
        
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('tickets:detail', kwargs={'pk': self.object.pk})
class TicketMessageCreateView(LoginRequiredMixin, CreateView):
    model = TicketMessage
    form_class = TicketMessageForm
    http_method_names = ['post']

    def form_valid(self, form):
        ticket = get_object_or_404(Ticket, pk=self.kwargs['pk'], user=self.request.user)
        message = form.save(commit=False)
        message.ticket = ticket
        message.user = self.request.user
        message.save()

        # مدیریت فایل‌های پیوست
        files = self.request.FILES.getlist('attachments')
        for file in files:
            TicketAttachment.objects.create(
                ticket=ticket,
                message=message,
                file=file,
                file_size=file.size
            )

        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('tickets:detail', kwargs={'pk': self.kwargs['pk']})

class CloseTicketView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        ticket = get_object_or_404(Ticket, pk=kwargs['pk'], user=request.user)
        ticket.status = Ticket.Status.CLOSED
        ticket.closed_at = timezone.now()
        ticket.save()
        return redirect('tickets:detail', pk=ticket.pk)