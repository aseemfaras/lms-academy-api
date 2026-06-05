from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import os
from email.mime.image import MIMEImage

def send_welcome_email(user, password, course_name, portal_link):
    subject = f"Welcome to AIDEAS Academy, {user.full_name or user.username}! 🚀"
    from_email = settings.DEFAULT_FROM_EMAIL
    to = user.email

    context = {
        'name': user.full_name or user.username,
        'course': course_name,
        'portal_link': portal_link or "https://lms.aideasacademy.com",
        'email': user.email,
        'password': password,
    }

    # Define the logo path (Cross-project reference)
    logo_path = r"C:\lms react\lms-react\lms\src\assets\logo.png"
    
    # HTML Template matching the user's design
    html_content = f"""
    <div style="font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; max-width: 650px; margin: auto; border: 1px solid #f0f0f0; border-radius: 8px; overflow: hidden; background-color: #ffffff; color: #333;">
        
        <!-- Header with Logo -->
        <div style="padding: 30px 40px 10px 40px;">
            <img src="cid:logo" alt="AIDEAS" style="height: 50px; display: block;">
        </div>

        <div style="padding: 20px 40px 40px 40px;">
            
            <!-- Centered Heading -->
            <h1 style="color: #000000; text-align: center; font-size: 28px; font-weight: 700; margin-bottom: 30px; letter-spacing: -0.5px;">Aideas Academy</h1>

            <!-- Welcome Message -->
            <h2 style="color: #333; font-size: 18px; font-weight: 600; margin-bottom: 15px;">Welcome, {context['name']}! 👋</h2>
            
            <p style="color: #444; font-size: 15px; line-height: 1.6; margin-bottom: 15px;">
                Dear {context['name']},<br>
                Welcome to AIDEAS Academy!
            </p>

            <p style="color: #444; font-size: 15px; line-height: 1.6; margin-bottom: 30px;">
                We're pleased to inform you that your registration has been successfully completed and your LMS account is now active. You have been officially enrolled in the <b>{context['course']}</b> course and can begin your learning journey right away using the login credentials below.
            </p>
            
            <!-- Login Details Box (Light Blue) -->
            <div style="background-color: #effcfc; border: 1px solid #dcfce7; border-radius: 12px; padding: 25px; margin-bottom: 25px;">
                <h3 style="color: #333; margin-top: 0; margin-bottom: 20px; font-size: 16px; display: flex; align-items: center;">
                    📝 Your Login Details
                </h3>
                <table style="width: 100%; border-collapse: collapse;">
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px; width: 140px; font-weight: 500;">LMS Portal</td>
                        <td style="padding: 8px 0; font-size: 14px;"><a href="{context['portal_link']}" style="color: #2563eb; text-decoration: none;">{context['portal_link']}</a></td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px; font-weight: 500;">Registered Email</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px;">{context['email']}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #666; font-size: 14px; font-weight: 500;">Temporary Password</td>
                        <td style="padding: 8px 0; color: #333; font-size: 14px;">{context['password']}</td>
                    </tr>
                </table>
            </div>

            <!-- Important Note Box (Light Yellow/Greenish) -->
            <div style="background-color: #f7fee7; border: 1px solid #d9f99d; border-radius: 12px; padding: 25px; margin-bottom: 30px;">
                <h3 style="color: #3f6212; margin-top: 0; margin-bottom: 10px; font-size: 16px; display: flex; align-items: center;">
                    ⚠️ Important Note
                </h3>
                <p style="color: #3f6212; font-size: 13px; line-height: 1.6; margin: 0;">
                    For security purposes, this password is valid only for your first login. After signing in, please update your password by navigating to Profile -> Security Settings. We strongly recommend keeping your login credentials confidential and not sharing them with anyone.
                    <br><br>
                    If you experience any difficulties accessing your account, our support team will be happy to assist you. We are excited to have you as part of our learning community and wish you great success in your Python course!
                </p>
            </div>

            <!-- Footer Logo & Signoff -->
            <div style="margin-top: 40px;">
                <img src="cid:logo" alt="AIDEAS" style="height: 35px; display: block; margin-bottom: 10px;">
                <p style="color: #000; font-weight: 700; font-size: 14px; margin: 0;">Best Regards,</p>
                <p style="color: #000; font-weight: 700; font-size: 14px; margin: 0;">Team AIDEAS Academy</p>
            </div>
        </div>
        
        <div style="text-align: center; padding: 20px; font-size: 11px; color: #999; border-top: 1px solid #f0f0f0;">
             © 2025 Aideas Tech Solutions & Aideas Academy<br>
             Support: <a href="mailto:hr@aideastech.com" style="color: #999;">hr@aideastech.com</a> | Need help? Reply to this email.
        </div>
    </div>
    """
    
    text_content = strip_tags(html_content)
    
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    
    # Attach Logo
    try:
        with open(logo_path, 'rb') as f:
            logo_data = f.read()
            logo_image = MIMEImage(logo_data)
            logo_image.add_header('Content-ID', '<logo>')
            logo_image.add_header('Content-Disposition', 'inline', filename='logo.png')
            msg.attach(logo_image)
    except FileNotFoundError:
        print(f"Warning: Logo not found at {logo_path}")

    msg.send()
