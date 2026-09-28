import os
import requests
from bs4 import BeautifulSoup
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ##########################################
# 1. ASETUKSET (Luetaan ympäristömuuttujista)
# ##########################################
URL = "https://www.tankille.fi/suomi/"

LAEHETTAJAE_EMAIL = os.environ.get("EMAIL_USER", "kaapo.villikka@gmail.com")
LAEHETTAJAE_SALASANA = os.environ.get("EMAIL_PASS", "boom haeq crno nymx")
VASTAANOTTAJA_EMAIL = os.environ.get("EMAIL_RECEIVER", "kaapo.villikka@hotmail.com")

# Hintaraja float-muodossa
try:
    HINTARAJA = float(os.environ.get("PRICE_LIMIT", 2.000))
except ValueError:
    HINTARAJA = 2.000

SMTP_PALVELIN = "smtp.gmail.com"
SMTP_PORTTI = 587


# ##########################################
# 2. HINNAN HAKEMINEN
# ##########################################
def hae_halvin_hinta():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Virhe sivua haettaessa: {e}")
        return None, None

    soup = BeautifulSoup(response.text, "html.parser")
    koko_teksti = soup.get_text()

    # Etsitään ensimmäinen hinnan muotoinen merkkijono
    match = re.search(r'(\d[.,]\d{3})', koko_teksti)

    if match:
        hinta_str = match.group(1).replace(",", ".")
        try:
            hinta = float(hinta_str)
            return hinta, "Suomen halvin asema (Tankille.fi)"
        except ValueError:
            print(f"Hinnan muuntaminen epäonnistui: {hinta_str}")
            return None, None
            
    print("Hintoja ei löytynyt sivustolta.")
    return None, None


# ##########################################
# 3. SÄHKÖPOSTIN LÄHETYS
# ##########################################
def laheta_sahkoposti(hinta, asema):
    msg = MIMEMultipart()
    msg['From'] = LAEHETTAJAE_EMAIL
    msg['To'] = VASTAANOTTAJA_EMAIL
    msg['Subject'] = f"🚨 Hintahälytys! 95-bensa alle {HINTARAJA:.3f} €/l"

    body = (
        f"95-oktaanisen bensiinin hinta on tippunut alle raja-arvon!\n\n"
        f"Halvin hinta: {hinta:.3f} €/l\n"
        f"Asema / Sijainti: {asema}\n\n"
        f"Katso tiedot sivustolta: {URL}"
    )
    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP(SMTP_PALVELIN, SMTP_PORTTI)
        server.starttls()
        server.login(LAEHETTAJAE_EMAIL, LAEHETTAJAE_SALASANA)
        server.send_message(msg)
        server.quit()
        print("Sähköposti lähetetty onnistuneesti!")
    except Exception as e:
        print(f"Sähköpostin lähetys epäonnistui: {e}")


# ##########################################
# 4. PÄÄOHJELMA
# ##########################################
def main():
    hinta, asema = hae_halvin_hinta()
    
    if hinta is not None:
        print(f"Löydetty halvin 95-hinta: {hinta:.3f} €/l")
        if hinta < HINTARAJA:
            print(f"Hinta alittaa raja-arvon {HINTARAJA:.3f} €/l. Lähetetään sähköposti...")
            laheta_sahkoposti(hinta, asema)
        else:
            print(f"Hinta ei alita raja-arvoa {HINTARAJA:.3f} €/l.")

if __name__ == "__main__":
    main()