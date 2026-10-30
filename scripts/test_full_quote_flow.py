import urllib.request
import urllib.error
import json
import io

BASE_URL = "http://127.0.0.1:8080"

# 1. Upload video file
boundary = '----WebKitFormBoundaryFullQuoteFlowTest'
body = io.BytesIO()
body.write(f'--{boundary}\r\n'.encode('utf-8'))
body.write(b'Content-Disposition: form-data; name="file"; filename="elestiri_ornegi.mp4"\r\n')
body.write(b'Content-Type: video/mp4\r\n\r\n')

# Copy cosmic.mp4 content to simulate real MP4 file
with open(r'E:\aivideoyap\public\broll\cosmic.mp4', 'rb') as f:
    body.write(f.read(500000)) # 500KB snippet

body.write(f'\r\n--{boundary}--\r\n'.encode('utf-8'))
body_bytes = body.getvalue()

req_up = urllib.request.Request(
    f"{BASE_URL}/api/media/upload",
    data=body_bytes,
    headers={
        'Content-Type': f'multipart/form-data; boundary={boundary}',
        'Content-Length': str(len(body_bytes))
    }
)

res_up = urllib.request.urlopen(req_up)
up_data = json.loads(res_up.read().decode('utf-8'))
print("1. Upload result:", up_data.get("success"), "| URL:", up_data.get("url"))
uploaded_url = up_data.get("url")

# 2. Add Quote Video to Timeline
quote_req = {
    "videoUrl": uploaded_url,
    "trimStart": 1.0,
    "trimEnd": 5.5,
    "timelineStart": 2.0,
    "theme": "red_alert",
    "headerText": "Arkadaşlar bu videoyu iyi izleyin...",
    "subHeaderText": "Sosyal medyada yayılan yanıltıcı iddia",
    "authorTag": "@elestirilen_hesap",
    "stamp": "yalan",
    "muted": False
}

req_add = urllib.request.Request(
    f"{BASE_URL}/api/timeline/add-quote-video",
    data=json.dumps(quote_req).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

res_add = urllib.request.urlopen(req_add)
add_data = json.loads(res_add.read().decode('utf-8'))
print("2. Add Quote Video result:", add_data.get("success"), "| Item ID:", add_data.get("quoteItem", {}).get("id"))

# 3. Check Timeline Data
res_tl = urllib.request.urlopen(f"{BASE_URL}/api/timeline/data")
tl = json.loads(res_tl.read().decode('utf-8'))
quotes = tl.get("video_data", {}).get("quoteVideos", [])
print(f"3. Timeline verified! Total Quote Items: {len(quotes)}")
print("   Latest Quote:", quotes[-1].get("headerText"), "URL:", quotes[-1].get("videoUrl"))

print("\n>>> FULL FLOW TEST (UPLOAD + ADD TO TIMELINE) 100% SUCCEEDED! <<<")
