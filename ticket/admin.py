from django.contrib import admin
from .models import *

class TicketMessageInline(admin.TabularInline):
    model = TicketMessage
    extra = 0
    readonly_fields = ['user', 'created_at']
    fields = ['user', 'message', 'is_staff_reply', 'internal_note', 'created_at']

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ['file_size', 'uploaded_at']

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['unique_id', 'user', 'status', 'priority', 'created_at']
    list_filter = ['status', 'priority', 'category']
    search_fields = ['unique_id', 'title', 'user__username']
    inlines = [TicketMessageInline, TicketAttachmentInline]
    readonly_fields = ['unique_id', 'created_at', 'updated_at', 'closed_at']
    actions = ['close_tickets']
    def changelist_view(self, request, extra_context=None):
        # محاسبه تعداد تیکت‌ها و افزودن به عنوان
        count = Ticket.objects.count()
        self.model._meta.verbose_name_plural = f'تیکت‌ها ({count})'
        self.model._meta.verbose_name = f'تیکت ({count})'
        return super().changelist_view(request, extra_context)
    def close_tickets(self, request, queryset):
        queryset.update(status=Ticket.Status.CLOSED, closed_at=timezone.now())
    close_tickets.short_description = "بستن تیکت‌های انتخاب شده"

@admin.register(TicketCategory)
class TicketCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'priority', 'slug']
    ordering = ['-priority']
    prepopulated_fields = {'slug': ('name',)}

