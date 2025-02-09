# nft-purchase-app/backend/utils.py
import os
import svgwrite
import json
import hashlib
import secrets
import time # Import time
from dotenv import load_dotenv
from ipfshttpclient import connect
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import base64

load_dotenv()

IPFS_GATEWAY_URL = os.getenv("IPFS_GATEWAY_URL")
EMAIL_ADDRESS = os.getenv("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

def generate_unique_id():
    """Generates a unique identifier using a combination of timestamp and random token."""
    timestamp = str(int(time.time()))  # Current timestamp as a string
    random_token = secrets.token_hex(16)  # 16 bytes of random data (32 hex characters)
    combined_string = timestamp + random_token
    unique_id = hashlib.sha256(combined_string.encode()).hexdigest()
    return unique_id

def generate_svg(unique_identifier):
    """Generates a simple SVG image based on a unique identifier."""
    dwg = svgwrite.Drawing('temp.svg', profile='tiny')
    # Use the hash to determine the circle's color and position.
    x = int(unique_identifier[:2], 16) * 5  # First two characters for X position
    y = int(unique_identifier[2:4], 16) * 5  # Next two for Y position
    radius = int(unique_identifier[4:6], 16) / 8  # Next two for radius
    color = f"#{unique_identifier[6:12]}"  # Next six for color

    dwg.add(dwg.circle((x, y), radius, fill=color))
    dwg.save()
    return 'temp.svg'

def upload_to_ipfs(file_path):
    """Uploads a file to IPFS and returns the CID."""
    try:
        client = connect() #Connects to local
        with open(file_path, 'rb') as f:
            response = client.add(f)
            return response['Hash']
    except Exception as e:
        print(f"Error uploading to IPFS: {e}")
        return None

def generate_nft(user_public_key):
    """Generates a unique NFT, uploads it to IPFS, and returns the metadata."""
    unique_id = generate_unique_id()
    svg_file = generate_svg(unique_id)

    #Upload to IPFS
    image_cid = upload_to_ipfs(svg_file)
    if image_cid is None:
        return None

    #Construct metadata
    metadata = {
        "name": f"My Cool NFT - {unique_id[:8]}",  #Shortened ID
        "description": "A Unique NFT Generated for User",
        "image": f"{IPFS_GATEWAY_URL}/{image_cid}",  #IPFS Gateway
        "attributes": [
            {"trait_type": "Generated For", "value": user_public_key},
            {"trait_type": "Unique ID", "value": unique_id}
        ],
        "nft_id": unique_id #Good to store unique IDs for retrieval later in the database
    }

    #Optionally Upload Metadata to IPFS - Recommended
    metadata_json = json.dumps(metadata, indent=4).encode('utf-8') #Properly format JSON

    metadata_cid = upload_to_ipfs(metadata_json) #UTF-8 Encoding!
    if metadata_cid:
       metadata["metadata_url"] = f"{IPFS_GATEWAY_URL}/{metadata_cid}" #Store this in database
    else:
        print("Warning: Could not upload metadata to IPFS")


    #Clean up temporary SVG file
    os.remove(svg_file)

    return metadata

def send_email(recipient, subject, body, html=None, image_path=None):
    """Sends an email using SMTP."""

    if not EMAIL_ADDRESS or not EMAIL_PASSWORD:
        print("Email credentials not set.  Cannot send email.")
        return False #Indicate failure

    msg = MIMEMultipart('alternative')
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = recipient
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if html:
        # If an image path is provided, embed the image in the HTML
        if image_path:
            try:
                with open(image_path, 'rb') as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    html = html.replace('cid:image1', f'data:image/svg+xml;base64,{img_base64}') #Reference Image
            except Exception as e:
                print(f"Error embedding image: {e}")

        msg.attach(MIMEText(html, 'html'))


    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server: #Adjust for your provider
            server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
            server.sendmail(EMAIL_ADDRESS, recipient, msg.as_string())
        print("Email sent successfully!")
        return True  #Indicate Success

    except Exception as e:
        print(f"Email sending failed: {e}")
        return False  #Indicate Failure