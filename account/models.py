from django.contrib.auth.models import AbstractUser
from django.db import models


# Create your models here.
from django.utils.translation import gettext_lazy as _
from iranian_cities.fields import Province as OstanField , County as ShahrestanField 
IRAN_PROVINCES = [
    ("آذربایجان شرقی", _("آذربایجان شرقی")),
    ("آذربایجان غربی", _("آذربایجان غربی")),
    ("اردبیل", _("اردبیل")),
    ("اصفهان", _("اصفهان")),
    ("البرز", _("البرز")),
    ("ایلام", _("ایلام")),
    ("بوشهر", _("بوشهر")),
    ("تهران", _("تهران")),
    ("چهارمحال و بختیاری", _("چهارمحال و بختیاری")),
    ("خراسان رضوی", _("خراسان رضوی")),
    ("خراسان شمالی", _("خراسان شمالی")),
    ("خراسان جنوبی", _("خراسان جنوبی")),
    ("خوزستان", _("خوزستان")),
    ("زنجان", _("زنجان")),
    ("سمنان", _("سمنان")),
    ("سیستان و بلوچستان", _("سیستان و بلوچستان")),
    ("فارس", _("فارس")),
    ("همدان", _("همدان")),
    ("قزوین", _("قزوین")),
    ("قم", _("قم")),
    ("کردستان", _("کردستان")),
    ("کرمان", _("کرمان")),
    ("کرمانشاه", _("کرمانشاه")),
    ("کهگیلویه و بویراحمد", _("کهگیلویه و بویراحمد")),
    ("گلستان", _("گلستان")),
    ("گیلان", _("گیلان")),
    ("لرستان", _("لرستان")),
    ("مرکزی", _("مرکزی")),
    ("مازندران", _("مازندران")),
    ("هرمزگان", _("هرمزگان")),
    ("یزد", _("یزد")),
]
class User(AbstractUser):
    mobile = models.CharField(max_length=20, verbose_name=_('شماره تلفن'),null=True, blank=True)
    legendry_code = models.CharField(max_length=20 , verbose_name=_(' کد ملی '), null=True, blank=True  ) 
    birthday = models.DateField(verbose_name=_(" تاریخ تولد "), null=True, blank=True)
    avatar = models.ImageField(upload_to='images/profile', verbose_name=_('آواتار'), null=True, blank=True)
    about_user = models.TextField(null=True, blank=True, verbose_name=_('درباره کاربر'))
    address = models.TextField(null = True , blank = True , verbose_name = _(' آدرس '))
    state = models.CharField(max_length=50, choices=IRAN_PROVINCES, verbose_name=_("استان"), null=True, blank=True)
    # city = ShahrField(max_length=100, blank=True, null=True, verbose_name=_('شهر'))
    city = ShahrestanField()
    post_code = models.CharField(max_length=100, blank=True, null=True,verbose_name=_('کد پستی'))
    Man =  _('Man')
    Female = _('Female')
    gender_choices = [
        (Man, _('مرد')),
        (Female, _('زن')),
    ]
    gender = models.CharField(max_length=13,choices=gender_choices,default='-----',blank=True, null=True,verbose_name=_('جنسیت'))
    customer = _('customer')
    vendor = _('vendor')
    account_select = [
        (customer, _('مشتری')),
        (vendor, _('فروشنده')),
    ]
    status = models.CharField(max_length=13,choices=account_select,default=customer,blank=True, null=True,verbose_name=_('وضعیت کاربر'))
    
    admission = models.BooleanField(default=False, verbose_name=_("ادمین") , blank=True, null=True)
    job = models.CharField(max_length=200, verbose_name=_(' شغل'), null=True, blank=True)
    class Meta:
        verbose_name = 'کاربر'
        verbose_name_plural = 'کاربران'

    def __str__(self):
        if self.username is not '':
            return self.username

        return self.mobile

    