import requests
import hashlib
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://trouverunlogement.lescrous.fr/tools/47/search?bounds=3.8070597_43.6533542_3.9413208_43.5667088&locationName=Montpellier"
STATE_FILE = "last_hash.txt"
EMAIL_FROM = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_ADDRESS"]

def fetch_page_hash():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "fr-FR,fr;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    }
    r = requests.get(URL, headers=headers, timeout=15)
    r.raise_for_status()
    return hashlib.md5(r.text.encode()).hexdigest(), r.text

def load_hash():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return f.read().strip()
    return None

def save_hash(h):
    with open(STATE_FILE, "w") as f:
        f.write(h)

def send_email(page_text):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = "🏠 CROUS Montpellier — La page a changé !"

    body = (
        "La page CROUS de Montpellier vient de changer.\n\n"
        "Va vérifier immédiatement :\n"
        "https://trouverunlogement.lescrous.fr/tools/47/search?"
        "bounds=3.8070597_43.6533542_3.9413208_43.5667088&locationName=Montpellier\n\n"
        "Postule sans attendre !"
    )
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print("Email envoyé !")

def main():
    print("Vérification en cours...")
    current_hash, page_text = fetch_page_hash()
    previous_hash = load_hash()

    print(f"Hash actuel   : {current_hash}")
    print(f"Hash précédent: {previous_hash}")

    if previous_hash is None:
        print("Premier lancement — hash sauvegardé.")
    elif current_hash != previous_hash:
        print("Changement détecté !")
        send_email(page_text)
    else:
        print("Aucun changement.")

    save_hash(current_hash)

if __name__ == "__main__":
    main()
