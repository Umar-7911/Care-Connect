"""
Utility functions for sending emails
"""
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def send_otp_email(email, otp_code, purpose='email_verification'):
    """
    Send OTP code via email
    
    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: Purpose of OTP ('email_verification' or 'password_reset')
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    try:
        if purpose == 'password_reset':
            subject = 'CareConnect - Password Reset OTP'
            message_plain = f"""
Hello,

You have requested to reset your password for your CareConnect account.

Your OTP code is: {otp_code}

This OTP will expire in 15 minutes.

If you did not request this password reset, please ignore this email.

Best regards,
CareConnect Team
"""
        else:
            subject = 'CareConnect - Email Verification OTP'
            message_plain = f"""
Hello,

Thank you for registering with CareConnect!

Your OTP code for email verification is: {otp_code}

This OTP will expire in 10 minutes.

If you did not create an account with CareConnect, please ignore this email.

Best regards,
CareConnect Team
"""
        
        # Send email
        send_mail(
            subject=subject,
            message=message_plain,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )
        
        return True
        
    except Exception as e:
        print(f"Error sending email to {email}: {str(e)}")
        return False


def send_email_with_fallback(email, otp_code, purpose='email_verification'):
    """
    Send email via SMTP, with console fallback for development
    
    Args:
        email: Recipient email address
        otp_code: 6-digit OTP code
        purpose: Purpose of OTP
    
    Returns:
        bool: True if email sent successfully or fallback used, False otherwise
    """
    # If using console backend, print OTP
    if settings.EMAIL_BACKEND == 'django.core.mail.backends.console.EmailBackend':
        purpose_text = "Password Reset" if purpose == 'password_reset' else "Email Verification"
        print(f"\n{'='*50}")
        print(f"{purpose_text} OTP for {email}: {otp_code}")
        print(f"{'='*50}\n")
        return True
    
    # Try to send via SMTP
    return send_otp_email(email, otp_code, purpose)
