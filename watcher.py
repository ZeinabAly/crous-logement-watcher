import requests
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

URL = "https://trouverunlogement.lescrous.fr/api/fr/search/47?bounds=3.8070597_43.6533542_3.9413208_43.5667088"
STATE_FILE = "last_state.json"
EMAIL_FROM = os.environ["EMAIL_ADDRESS"]
EMAIL_PASSWORD = os.environ["EMAIL_PASSWORD"]
EMAIL_TO = os.environ["EMAIL_ADDRESS"]

def fetch_logements():
    headers = {
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    r = requests.get(URL, headers=headers)
    r.raise_for_status()
    data = r.json()
    items = data.get("data", {}).get("items", [])
    return items

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return []

def save_state(items):
    with open(STATE_FILE, "w") as f:
        json.dump(items, f)

def send_email(new_items):
    msg = MIMEMultipart()
    msg["From"] = EMAIL_FROM
    msg["To"] = EMAIL_TO
    msg["Subject"] = "🏠 Nouveau logement CROUS disponible à Montpellier !"

    body = "Des logements viennent d'apparaître sur le site CROUS :\n\n"
    for item in new_items:
        nom = item.get("title", "Résidence inconnue")
        adresse = item.get("address", "Adresse non disponible")
        lien = f"https://trouverunlogement.lescrous.fr/tools/47/search?bounds=3.8070597_43.6533542_3.9413208_43.5667088"
        body += f"- {nom}\n  {adresse}\n  {lien}\n\n"

    body += "Postule immédiatement sur : https://trouverunlogement.lescrous.fr\n"
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(EMAIL_FROM, EMAIL_PASSWORD)
        server.sendmail(EMAIL_FROM, EMAIL_TO, msg.as_string())

    print("Email envoyé !")

def main():
    print("Vérification en cours...")
    current_items = fetch_logements()
    previous_ids = {item.get("id") for item in load_state()}
    new_items = [item for item in current_items if item.get("id") not in previous_ids]

    if new_items:
        print(f"{len(new_items)} nouveau(x) logement(s) trouvé(s) !")
        send_email(new_items)
    else:
        print("Aucun nouveau logement.")

    save_state(current_items)

if __name__ == "__main__":
    main()
