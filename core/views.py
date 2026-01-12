from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .forms import FormForms, FormAttachmentsForm
from .models import FormAttachment,Branch
from django.contrib.auth.decorators import login_required
from .models import Forms

def open_form(request):
    if request.method == 'POST':
        form = FormForms(request.POST)
        attachments_form = FormAttachmentsForm()  # ← FIX
        files = request.FILES.getlist('attachments')

        # file size check (keep exactly as-is)
        too_large_files = [f.name for f in files if f.size > 1*1024*1024]
        if too_large_files:
            messages.error(
                request,
                "The following files exceed 1MB: " + ", ".join(too_large_files)
            )
            return render(request, 'core/form.html', {
                'form': form,
                'attachments_form': attachments_form
            })

        if form.is_valid():
            form_instance = form.save()

            for f in files:
                FormAttachment.objects.create(form=form_instance, file=f)

            # SEND EMAIL ON SUBMISSION
            if form_instance.submitter_email:
                send_mail(
                    subject="Koili Integration Form Submitted",
                    message=(
                        "Dear Applicant,\n\n"
                        "Your Koili Integration Application Form has been successfully submitted.\n\n"
                        "Current Status: Pending\n\n"
                        "You will be notified once the status is updated.\n\n"
                        "Regards,\n"
                        "Agricultural Development Bank Ltd"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[form_instance.submitter_email],
                    fail_silently=False,
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


@login_required(login_url='admin_login')
def admin_forms_view(request):
    # Get the admin's profile
    user_profile = getattr(request.user, 'adminprofile', None)

    if user_profile and user_profile.qr_channel:
        # Filter forms by the admin's QR channel
        forms = Forms.objects.filter(qr_channel=user_profile.qr_channel).order_by('-submitted_at')
    else:
        forms = Forms.none()  # admin not assigned a QR channel

    return render(request, 'core/admin_forms.html', {'forms': forms})


@login_required(login_url='admin_login')
def view_form(request, form_id):
    form_instance = Forms.objects.get(id=form_id)
    user_profile = getattr(request.user, 'adminprofile', None)

    # Only allow admins to view forms for their assigned QR channel
    if not user_profile or form_instance.qr_channel != user_profile.qr_channel:
        return HttpResponse("Unauthorized", status=403)

    attachments = form_instance.attachments.all()
    return render(request, 'core/view_form.html', {
        'form': form_instance,
        'attachments': attachments
    })
