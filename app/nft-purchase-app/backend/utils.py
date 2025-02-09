# nft-purchase-app/backend/utils.py
import os
import svgwrite
import json
import hashlib
import secrets
import time
import base64
from dotenv import load_dotenv
from ipfshttpclient import connect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

load_dotenv()

IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_unique_id():
    timestamp = str(int(time.time()))
    random_token = secrets.token_hex(16)
    combined_string = timestamp + random_token
    unique_id = hashlib.sha256(combined_string.encode()).hexdigest()
    return unique_id

def generate_svg(unique_identifier):
    dwg = svgwrite.Drawing(' temp.svg ', profile= ' tiny ')
    x = int(unique_identifier[:2], 16) * 5
    y = int(unique_identifier[2:4], 16) * 5
    radius = int(unique_identifier[4:6], 16) / 8
    color = f"/{unique_identifier[6:12]}"

    dwg.add(dwg.circle((x, y), radius, fill=color))
    dwg.save()
    return ' temp.svg '

def upload_to_ipfs(file_path):
    try:
        client = connect()
        with open(file_path, 'rb') as f:
            response = client.add(f)
            return response['Hash']
    except Exception as e:
        print(f" Error uploading to IPFS: {e} ")
        return None

def generate_nft(user_public_key):
    unique_id = generate_unique_id()
    svg_file = generate_svg(unique_id)

    image_cid = upload_to_ipfs(svg_file)
    if image_cid is None:
        return None

    metadata = {
        " name ": f" My Cool NFT - {unique_id[:8]} ",
        " description ": " A Unique NFT Generated for User ",
        " image ": f"{IPFS_GATEWAY_URL}/ {image_cid} ",
        " attributes ": [
            {" trait_type ": " Generated For ", " value ": user_public_key},
            {" trait_type ": " Unique ID ", " value ": unique_id}
        ],
        " nft_id ": unique_id
    }

    metadata_json = json.dumps(metadata, indent=4).encode('utf-8')

    metadata_cid = upload_to_ipfs(metadata_json)
    if metadata_cid:
        metadata[" metadata_url "] = f"{IPFS_GATEWAY_URL}/ {metadata_cid} "
    else:
        print(" Warning: Could not upload metadata to IPFS ")

    os.remove(svg_file)

    return metadata

def send_email(recipient, subject, body, html=None, image_path=None):
    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print(" Email credentials not set.  Cannot send email. ")
        return False

    msg = MIMEMultipart(' alternative ')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, ' plain '))

    if html:
        if image_path:
            try:
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    html = html.replace(' cid:image1 ', f ' data:image/svg+xml;base64,{img_base64} ')
            except Exception as e:
                print(f" Error embedding image: {e} ")

        msg.attach(MIMEText(html, ' html '))

    try:
        with smtplib.SMTP_SSL(' smtp.gmail.com ', 465) as server:
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        print(" Email sent successfully! ")
        return True
    except Exception as e:
        print(f" Email sending failed: {e} ")
        return False