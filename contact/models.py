from django.db import models

# Create your models here.

class contact_us(models.Model):
    title = models.CharField(max_length = 300, verbose_name = ' عنوان ')
    full_name = models.CharField(max_length = 300, verbose_name = ' نام و نام خانوادگی ')
    email = models.EmailField(max_length = 300, verbose_name = ' ایمیل ')
    message = models.TextField(max_length = 300, verbose_name = ' متن تماس با ما ')
    created_date = models.DateField(verbose_name = ' تاریح ایجاد ', auto_now_add = True) #The auto_now_add command gives us the date of adding that item
    response = models.TextField(max_length = 300, verbose_name = ' متن پاسخ تماس با ما ' , null=True , blank=True)
    is_read_by_admin = models.BooleanField(verbose_name = ' مشاهده شده توسط ادمین ', default=False)
    class Meta:
        verbose_name = ' نماس با ما '
        verbose_name_plural = ' لیست تماس با ما '

    def __str__(self) -> str:
        return self.title
    

class UserProfile(models.Model):
    image = models.ImageField(upload_to= 'images')