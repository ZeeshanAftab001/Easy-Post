import requests
import os
from ...core.config import settings


ACCESS_TOKEN = settings.ACCESS_TOKEN
PHONE_NUMBER_ID = settings.PHONE_NUMBER_ID
VERIFY_TOKEN = settings.VERIFY_TOKEN

MEDIA_DIR = "media"
os.makedirs(MEDIA_DIR, exist_ok=True)

# Supported MIME types for WhatsApp
MIME_EXTENSIONS = {
    ".mp3": "audio/mpeg",
    ".ogg": "audio/ogg",
    ".aac": "audio/aac",
    ".mp4": "video/mp4",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
    ".pdf": "application/pdf",
}


# ========================
# TEXT HANDLER
# ========================
async def handle_text(message, sender):
    text = message["text"]["body"]
    print("Text:", text)

    # Send audio when a text message is received
    # audio_file = os.path.join(MEDIA_DIR, "audio.mp3")  # ensure this file exists
    # send_audio(sender, audio_file)

    # Optional: also send text confirmation
    await send_text(sender, f"You said: {text}")

# ========================
# MEDIA HANDLER (for downloading incoming media)
# ========================
async def handle_media(media_obj, media_type, sender):
    media_id = media_obj["id"]
    mime_type = media_obj.get("mime_type", "")
    extension = os.path.splitext(media_obj.get("filename", media_id))[1] or ""
    filename = f"{media_type}_{media_id}{extension}"

    print(f"{media_type.upper()} | ID: {media_id} | MIME: {mime_type}")

    media_url = get_media_url(media_id)
    if media_url:
        await download_media(media_url, filename)
        await send_text(sender, f"✅ {media_type.capitalize()} received")
    else:
        await send_text(sender, f"⚠ Failed to download {media_type}")

# ========================
# GET MEDIA URL
# ========================
async def get_media_url(media_id):
    url = f"https://graph.facebook.com/v22.0/{media_id}"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        return r.json().get("url")
    print("Failed to fetch media URL:", r.text)
    return None

# ========================
# DOWNLOAD MEDIA
# ========================
async def download_media(media_url, filename):
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    path = os.path.join(MEDIA_DIR, filename)
    r = requests.get(media_url, headers=headers, stream=True)
    if r.status_code == 200:
        with open(path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Saved:", path)
        return path
    else:
        print("Download failed:", r.text)
        return None

# ======================== #
#         SEND TEXT        #
# ======================== #
async def send_text(to, text):
    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "text",
        "text": {"body": text}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Text send response:", r.json())

# ========================
# UPLOAD AUDIO
# ========================
async def upload_audio(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    mime_type = MIME_EXTENSIONS.get(ext)
    if not mime_type:
        raise ValueError(f"Unsupported audio format: {ext}")

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/media"
    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    files = {"file": (os.path.basename(file_path), open(file_path, "rb"), mime_type)}
    data = {"messaging_product": "whatsapp", "type": "audio"}

    r = requests.post(url, headers=headers, files=files, data=data)
    result = r.json()
    media_id = result.get("id")
    if not media_id:
        print("Upload failed:", result)
        return None
    return media_id

# ========================
# SEND AUDIO
# ========================
async def send_audio(to, file_path):
    media_id = upload_audio(file_path)
    if not media_id:
        print("Audio upload failed")
        return

    url = f"https://graph.facebook.com/v22.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to,
        "type": "audio",
        "audio": {"id": media_id}
    }
    r = requests.post(url, headers=headers, json=payload)
    print("Audio send response:", r.json())
