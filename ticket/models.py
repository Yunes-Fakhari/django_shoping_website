from django.db import models

# Create your models here.
from django.db import models
from django.utils import timezone
from account.models import User
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
class TicketCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='نام دسته‌بندی')
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name='توضیحات')
    priority = models.PositiveSmallIntegerField(default=0, verbose_name='اولویت نمایش')
    
    class Meta:
        verbose_name = 'دسته‌بندی تیکت'
        verbose_name_plural = 'دسته‌بندی تیکت‌ها'
        ordering = ['-priority', 'name']
    
    def __str__(self):
        return self.name
# سیگنال برای به‌روزرسانی تعداد هنگام تغییرات

class Ticket(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'باز'
        IN_PROGRESS = 'in_progress', 'در حال بررسی'
        WAITING_USER = 'waiting_user', 'منتظر کاربر'
        CLOSED = 'closed', 'بسته شده'
        REOPENED = 'reopened', 'بازگشایی شده'
    
    class Priority(models.TextChoices):
        LOW = 'low', 'کم'
        MEDIUM = 'medium', 'متوسط'
        HIGH = 'high', 'بالا'
        CRITICAL = 'critical', 'ضروری'
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tickets',
        verbose_name='کاربر'
    )
    category = models.ForeignKey(
        TicketCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='دسته‌بندی'
    )
    title = models.CharField(max_length=200, verbose_name='عنوان تیکت')
    unique_id = models.CharField(max_length=20, unique=True, editable=False, verbose_name='شناسه یکتا')
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.OPEN,
        verbose_name='وضعیت'
    )
    priority = models.CharField(
        max_length=20,
        choices=Priority.choices,
        default=Priority.MEDIUM,
        verbose_name='اولویت'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='آخرین بروزرسانی')
    closed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاریخ بسته شدن')
    is_read = models.BooleanField(default=False, verbose_name='خوانده شده')
    last_replied = models.DateTimeField(null=True, blank=True, verbose_name='آخرین پاسخ')

    class Meta:
        verbose_name = 'تیکت'
        verbose_name_plural = 'تیکت‌ها'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['status']),
            models.Index(fields=['priority']),
            models.Index(fields=['unique_id']),
        ]
    
    # متد برای نمایش تعداد در عنوان
    @classmethod
    def get_verbose_name(cls):
        count = cls.objects.count()
        return f'تیکت‌ها ({count})'
    
    def __str__(self):
        return f"{self.unique_id} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.unique_id:
            self.unique_id = self.generate_unique_id()
        super().save(*args, **kwargs)
    
    def generate_unique_id(self):
        return f"TKT-{timezone.now().strftime('%Y%m%d')}-{self.user.id:04d}-{self.pk:06d}"
    
@receiver([post_save, post_delete], sender=Ticket)
def update_verbose_name(sender, **kwargs):
        from django.apps import apps
        model = apps.get_model('holding', 'ticket')
        model._meta.verbose_name_plural = model.get_verbose_name()


class TicketMessage(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='messages',
        verbose_name='تیکت'
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='ارسال کننده'
    )
    message = models.TextField(verbose_name='متن پیام')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ارسال')
    is_staff_reply = models.BooleanField(default=False, verbose_name='پاسخ پشتیبانی')
    internal_note = models.BooleanField(default=False, verbose_name='یادداشت داخلی')

    class Meta:
        verbose_name = 'پیام تیکت'
        verbose_name_plural = 'پیام‌های تیکت'
        ordering = ['created_at']

    def __str__(self):
        return f"پیام برای {self.ticket.unique_id}"

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(
        Ticket,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='تیکت'
    )
    message = models.ForeignKey(
        TicketMessage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='پیام مرتبط'
    )
    file = models.FileField(
        upload_to='tickets/attachments/%Y/%m/%d/',
        verbose_name='فایل پیوست'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ آپلود')
    file_size = models.PositiveIntegerField(editable=False, verbose_name='حجم فایل')

    class Meta:
        verbose_name = 'پیوست تیکت'
        verbose_name_plural = 'پیوست‌های تیکت'
    
    def __str__(self):
        return f"پیوست {self.file.name}"
    
    def save(self, *args, **kwargs):
        if self.file and not self.file_size:
            self.file_size = self.file.size
        super().save(*args, **kwargs)