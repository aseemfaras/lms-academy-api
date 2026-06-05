import smtplib
import ssl

def test_raw_smtp():
    smtp_server = "smtp.gmail.com"
    port = 465  # For SSL
    username = "sharonkommoji@gmail.com"
    password = "xvtltuovclxeyfbz"

    print(f"Connecting to {smtp_server} on port {port}...")
    context = ssl.create_default_context()
    try:
        with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
            print("Connection successful. Attempting login...")
            server.login(username, password)
            print("Login SUCCESSFUL!")
            
            # Try to send a test mail
            msg = f"Subject: Raw SMTP Test\n\nThis is a test from the LMS debugger."
            server.sendmail(username, username, msg)
            print("Test email sent successfully!")
    except Exception as e:
        print(f"FAILED: {e}")

if __name__ == "__main__":
    test_raw_smtp()
