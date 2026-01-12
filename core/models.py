from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

QR_CHOICES = [
    ('fonepay', 'Fonepay'),
    ('nepalpay', 'Nepalpay'),
]

STATUS_CHOICES = [
    ('pending', 'Pending'),
    ('approved', 'Approved'),
    ('rejected', 'Rejected'),
]

class Branch(models.Model):
    name = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.name

class Forms(models.Model):
    merchant_name = models.CharField(max_length=150)
    account_number = models.CharField(max_length=50)
    mobile_number = models.CharField(max_length=20)
    pan = models.CharField(max_length=20)
    qr_channel = models.CharField(max_length=20, choices=QR_CHOICES)
    agree_deposits = models.BooleanField(default=False)
    agree_pay = models.BooleanField(default=False)
    declare = models.BooleanField(default=False)
    date = models.DateField()
    name = models.CharField(max_length=100)
    signature = models.CharField(max_length=100)
    branch = models.ForeignKey(Branch, on_delete=models.SET_NULL, null=True, blank=True)
    branch_staff_contact = models.CharField(max_length=50)
    submitter_email = models.EmailField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.merchant_name} - {self.account_number}"

class FormAttachment(models.Model):
    form = models.ForeignKey(Forms, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='uploads/')

    def __str__(self):
        return f"{self.file.name} for {self.form.merchant_name}"

class AdminProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    qr_channel = models.CharField(max_length=20, choices=QR_CHOICES, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} ({self.qr_channel})"

@receiver(post_save, sender=User)
def create_admin_profile(sender, instance, created, **kwargs):
    if created:
        AdminProfile.objects.create(user=instance)
