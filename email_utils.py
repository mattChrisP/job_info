import os
import json
from dotenv import load_dotenv
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from utils import get_date_range
from firebase_admin import functions

# Load environment variables
load_dotenv()

# Gmail credentials
SENDER_EMAIL = os.getenv("GMAIL_ADDRESS")                      

APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")                     


def send_email_with_gmail(sender_email, app_password, recipient_email, subject, body_html, attachment_path=None):
    """
    Send an email using Gmail's SMTP server with CSS-styled content.
    """
    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        
        # Add the email body (HTML format)
        msg.attach(MIMEText(body_html, "html"))

        # Attach a file, if provided
        if attachment_path:
            with open(attachment_path, "rb") as attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename={os.path.basename(attachment_path)}",
                )
                msg.attach(part)

        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()
            server.login(sender_email, app_password)
            server.send_message(msg)

        print(f"Email sent successfully to {recipient_email}!")
    except Exception as e:
        print(f"Failed to send email: {e}")


def send_generated_cover_letters(cover_letters_file, recipient_email):
    """
    Send emails with generated cover letters.
    """
    with open(cover_letters_file, "r") as file:
        cover_letters = json.load(file)
    
    date_range = get_date_range()

    for cover_letter in cover_letters:
        body_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ width: 100%; max-width: 600px; margin: 20px auto; background-color: #ffffff; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0px 2px 10px rgba(0, 0, 0, 0.1); }}
                .header {{ background-color: #4CAF50; color: #ffffff; padding: 20px; text-align: center; font-size: 20px; font-weight: bold; border-top-left-radius: 8px; border-top-right-radius: 8px; }}
                .content {{ padding: 20px; }}
                .job-title {{ font-size: 24px; font-weight: bold; color: #007BFF; text-align: center; }}
                .section-title {{ font-size: 18px; font-weight: bold; margin-top: 20px; color: #333; }}
                .keywords {{ list-style-type: none; padding: 0; }}
                .keywords li {{ display: inline-block; background-color: #e7f3fe; color: #31708f; margin: 5px; padding: 8px 12px; border-radius: 5px; font-size: 14px; }}
                .missing-keywords li {{ background-color: #ffebe6; color: #d9534f; }}
                .footer {{ background-color: #f1f1f1; color: #333; text-align: center; padding: 10px; font-size: 12px; border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; }}
                a.button {{ display: inline-block; background-color: #4CAF50; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin-top: 10px; }}
                a.button:hover {{ background-color: #45a049; }}
            </style>
            </head>
            <body>
            <div class="container">
                <div class="header">Job Notification</div>
                <div class="content">
                <p class="job-title">{cover_letter['job_title']}</p>
                <p>Job opportunities for you today ;)</p>
                <p class="section-title">Job Details:</p>
                <ul>
                    <li><strong>Employment Type:</strong> {cover_letter['employment_type']}</li>
                    <li><strong>Published Since:</strong> {cover_letter['published_since']}</li>
                    <li><strong>Job URL:</strong> <a href="{cover_letter['url']}" class="button">View Job Posting</a></li>
                </ul>
                <p class="section-title">Matched Keywords:</p>
                <ul class="keywords">
                    {''.join(f'<li>{kw}</li>' for kw in cover_letter['matched_keywords'])}
                </ul>
                <p class="section-title">Missing Keywords:</p>
                <ul class="keywords missing-keywords">
                    {''.join(f'<li>{kw}</li>' for kw in cover_letter['missing_keywords'])}
                </ul>
                <p>Please find your cover letter attached for your reference.</p>
            </div>
            </body>
            </html>
            """

        send_email_with_gmail(
            sender_email=SENDER_EMAIL,
            app_password=APP_PASSWORD,
            recipient_email=recipient_email,
            subject=f"Job Opportunity ({date_range})",
            body_html=body_html,
            attachment_path=cover_letter["cover_letter_path"],
        )




