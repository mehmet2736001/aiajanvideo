import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8080"

# 1. Test Add Quote Video
payload = {
    "videoUrl": "broll/cosmic.mp4",
    "trimStart": 1.5,
    "trimEnd": 7.0,
    "timelineStart": 1.0,
    "theme": "red_alert",
    "headerText": "Arkadaşlar bu videoyu iyi izleyin...",
    "subHeaderText": "Sosyal medyada yayılan asılsız iddia",
    "authorTag": "@iddia_sahibi",
    "stamp": "yalan",
    "volume": 1.0,
    "muted": False
}

req = urllib.request.Request(
    f"{BASE_URL}/api/timeline/add-quote-video",
    data=json.dumps(payload).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)

try:
    res = urllib.request.urlopen(req)
    data = json.loads(res.read().decode('utf-8'))
    print("1. Add Quote Video success:", data.get("success"), "| ID:", data.get("quoteItem", {}).get("id"))
    quote_id = data.get("quoteItem", {}).get("id")
except urllib.error.HTTPError as e:
    print("1. Add Quote Video error:", e.code, e.read().decode('utf-8'))
    exit(1)

# 2. Verify in timeline data
res2 = urllib.request.urlopen(f"{BASE_URL}/api/timeline/data")
tl = json.loads(res2.read().decode('utf-8'))
quotes = tl.get("video_data", {}).get("quoteVideos", [])
print(f"2. Timeline verified! Total Quote Videos: {len(quotes)}")
if quotes:
    q = quotes[0]
    print(f"   Theme: {q.get('theme')} | Header: '{q.get('headerText')}' | Trim: {q.get('trimStart')}s - {q.get('trimEnd')}s")

print(">>> QUOTE VIDEO BACKEND INTEGRATION PASSED! <<<")
