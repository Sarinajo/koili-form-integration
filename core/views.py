from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.http import require_POST

from .forms import FormForms, FormAttachmentsForm
from .models import Forms, FormAttachment


# ===============================
# PUBLIC FORM SUBMISSION
# ===============================
def open_form(request):
    if request.method == 'POST':
        form = FormForms(request.POST)
        attachments_form = FormAttachmentsForm()
        files = request.FILES.getlist('attachments')

        # File size check (keep exactly)
        too_large = [f.name for f in files if f.size > 1 * 1024 * 1024]
        if too_large:
            messages.error(request, "Files over 1MB: " + ", ".join(too_large))
            return render(request, 'core/form.html', {
                'form': form,
                'attachments_form': attachments_form
            })

        if form.is_valid():
            form_instance = form.save()

            for f in files:
                FormAttachment.objects.create(form=form_instance, file=f)

            # Email on submission
            if form_instance.submitter_email:
                send_mail(
                    "Koili Integration Form Submitted",
                    "Your form has been submitted.\n\nStatus: Pending",
                    settings.DEFAULT_FROM_EMAIL,
                    [form_instance.submitter_email],
                )

            messages.success(request, "Form submitted successfully.")
            return redirect('form')

    else:
        form = FormForms()
        attachments_form = FormAttachmentsForm()

    return render(request, 'core/form.html', {
        'form': form,
        'attachments_form': attachments_form
    })


# ===============================
# ADMIN AUTH
# ===============================
def admin_login(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect('admin_forms')
        messages.error(request, "Invalid credentials")

    return render(request, 'core/admin_login.html')


@require_POST
@login_required(login_url='admin_login')
def admin_logout(request):
    logout(request)
    return redirect('admin_login')


# ===============================
# ADMIN: PENDING FORMS
# ===============================
@login_required(login_url='admin_login')
def admin_forms_view(request):
    profile = getattr(request.user, 'adminprofile', None)

    if not profile or not profile.qr_channel:
        return HttpResponse("Unauthorized", status=403)

    forms = Forms.objects.filter(
        qr_channel=profile.qr_channel,
        status='pending'
    ).order_by('-submitted_at')

    return render(request, 'core/admin_forms.html', {'forms': forms})


# ===============================
# ADMIN: PROCESSED FORMS
# ===============================
@login_required(login_url='admin_login')
def processed_forms_view(request):
    profile = getattr(request.user, 'adminprofile', None)

    if not profile or not profile.qr_channel:
        return HttpResponse("Unauthorized", status=403)

    forms = Forms.objects.filter(
        qr_channel=profile.qr_channel,
        status__in=['approved', 'rejected']
    ).order_by('-submitted_at')

    return render(request, 'core/processed_forms.html', {'forms': forms})


# ===============================
# VIEW SINGLE FORM
# ===============================
@login_required(login_url='admin_login')
def view_form(request, form_id):
    form_instance = get_object_or_404(Forms, id=form_id)
    profile = getattr(request.user, 'adminprofile', None)

    if not profile or form_instance.qr_channel != profile.qr_channel:
        return HttpResponse("Unauthorized", status=403)

    attachments = form_instance.attachments.all()

    return render(request, 'core/view_form.html', {
        'form': form_instance,
        'attachments': attachments
    })


# ===============================
# UPDATE STATUS (PENDING ONLY)
# ===============================
@require_POST
@login_required(login_url='admin_login')
def update_form_status(request, form_id):
    form_instance = get_object_or_404(Forms, id=form_id)
    profile = getattr(request.user, 'adminprofile', None)

    if not profile or form_instance.qr_channel != profile.qr_channel:
        return HttpResponse("Unauthorized", status=403)

    # Prevent updates if already processed
    if form_instance.status != 'pending':
        messages.error(request, "This form is already processed.")
        return redirect('admin_forms')

    new_status = request.POST.get('status')
    if new_status not in ['approved', 'rejected']:
        messages.error(request, "Invalid status.")
        return redirect('admin_forms')

    old_status = form_instance.status
    form_instance.status = new_status
    form_instance.save()

    # Email notification
    if form_instance.submitter_email:
        send_mail(
            "Koili Integration Form Status Update",
            f"Your form status changed from {old_status} to {new_status}.",
            settings.DEFAULT_FROM_EMAIL,
            [form_instance.submitter_email],
        )

    messages.success(request, f"Form {new_status}.")
    return redirect('admin_forms')
def home(request):
    return render(request, 'core/home.html')
