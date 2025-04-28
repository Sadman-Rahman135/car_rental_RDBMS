import smtplib
import random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def generate_verification_code(digits=6):
    lower_bound = 10 ** (digits - 1)  # e.g., 100000 for 6 digits
    upper_bound = (10 ** digits) - 1  # e.g., 999999 for 6 digits
    return random.randint(lower_bound, upper_bound)


def send_verification_email(recipient_email, verification_code):
    sender_email = "geminigpt211@gmail.com"  # Replace with your Gmail address
    sender_password = "wawj dpwl kqsx sjpo"  # Replace with your App Password (or regular password if 2FA is off)
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    # Create the email
    subject = "Login Verification Code"
    body = f"Your verification code is: {verification_code}"
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to the SMTP server
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS
        server.login(sender_email, sender_password)

        # Send the email
        server.sendmail(sender_email, recipient_email, msg.as_string())
        print(f"Verification code sent to {recipient_email}")
        server.quit()
        return True
    except Exception as e:
        print(f"Failed to send email: {e}")
        return False


def verify_code(sent_code, user_code):
    try:
        # Convert user input to integer for comparison
        return sent_code == int(user_code)
    except ValueError:
        print("Invalid input: Please enter a numeric code.")
        return False


def main():
    print("Welcome to the Login System")
    email = input("Enter your email address: ")

    # Generate and send verification code
    verification_code = generate_verification_code()
    if not send_verification_email(email, verification_code):
        print("Could not send verification email. Please try again.")
        return

    # Get code from user
    user_code = input("Enter the verification code sent to your email: ")

    # Verify the code
    if verify_code(verification_code, user_code):
        print("Verification successful! You are now logged in.")
    else:
        print("Invalid verification code. Login failed.")


if __name__ == "__main__":
    main()