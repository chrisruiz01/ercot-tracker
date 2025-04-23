import subprocess
import smtplib
from email.message import EmailMessage
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

LOG_FILE = f"logs/{datetime.now().strftime('%Y%m%d')}.log"

def run_step(step_name, cmd):
    with open(LOG_FILE, "a") as log:
        log.write(f"\n--- Running {step_name} ---\n")
        try:
            subprocess.run(cmd, check=True, stdout=log, stderr=log)
            log.write(f"{step_name} completed successfully.\n")
        except subprocess.CalledProcessError:
            log.write(f"ERROR in {step_name}\n")
            send_email_alert(step_name)
            raise  # Optonal: re-raise to halt script

def send_email_alert(failed_step):
    EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
    EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

    msg = EmailMessage()
    msg["Subject"] = f"ERCOT Pipeline FAILED: {failed_step}"
    msg["From"] = EMAIL_ADDRESS
    msg["To"] = "chrisruiz01@gmail.com"
    msg.set_content(f"The ERCOT pipeline failed during step: {failed_step}\n\nSee log: {LOG_FILE}")

    with open(LOG_FILE, "r") as f:
        msg.add_attachment(f.read(), filename=os.path.basename(LOG_FILE), subtype="plain")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)

# RUN PIPELINE
try:
    run_step("fetch_data", ["python", "scripts/fetch_data.py"])
    run_step("load_to_db", ["python", "scripts/load_to_db.py"])
    run_step("query_rolling_avg", ["python", "scripts/query_rolling_avg.py"])
except Exception as e:
    print("Pipeline failed. See log.")