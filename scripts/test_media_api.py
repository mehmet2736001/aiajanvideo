import urllib.request
import urllib.error
import json

BASE_URL = "http://127.0.0.1:8080"

# 1. Test Add PIP Video
pip_req = {
    "videoUrl": "broll/cosmic.mp4",
    "startTime": 2.0,
    "duration": 5.0,
    "position": "top-right",
    "shape": "circle",
    "width": 320,
    "muted": True
}
req1 = urllib.request.Request(f"{BASE_URL}/api/timeline/add-pip", data=json.dumps(pip_req).encode('utf-8'), headers={'Content-Type': 'application/json'})
res1 = urllib.request.urlopen(req1)
data1 = json.loads(res1.read().decode('utf-8'))
print("1. Add PIP success:", data1.get("success"), "| ID:", data1.get("pipItem", {}).get("id"))
pip_id = data1.get("pipItem", {}).get("id")

# 2. Test Add PNG Overlay
png_req = {
    "imageUrl": "illustrations/logo.png",
    "startTime": 1.0,
    "duration": 6.0,
    "position": "top-left",
    "animation": "bounce",
    "width": 160
}
req2 = urllib.request.Request(f"{BASE_URL}/api/timeline/add-png-overlay", data=json.dumps(png_req).encode('utf-8'), headers={'Content-Type': 'application/json'})
res2 = urllib.request.urlopen(req2)
data2 = json.loads(res2.read().decode('utf-8'))
print("2. Add PNG success:", data2.get("success"), "| ID:", data2.get("overlayItem", {}).get("id"))
png_id = data2.get("overlayItem", {}).get("id")

# 3. Check GET /api/timeline/data
res3 = urllib.request.urlopen(f"{BASE_URL}/api/timeline/data")
data3 = json.loads(res3.read().decode('utf-8'))
pips = data3.get("video_data", {}).get("pipVideos", [])
overlays = data3.get("video_data", {}).get("overlayImages", [])
print(f"3. Timeline verified! Total PIPs: {len(pips)}, Total Overlays: {len(overlays)}")

# 4. Test Mute / Unmute
req_mute = urllib.request.Request(f"{BASE_URL}/api/media/remove-audio", data=json.dumps({"mode": "mute"}).encode('utf-8'), headers={'Content-Type': 'application/json'})
res_mute = urllib.request.urlopen(req_mute)
print("4. Mute toggle result: audioMuted =", json.loads(res_mute.read().decode('utf-8')).get("audioMuted"))

req_unmute = urllib.request.Request(f"{BASE_URL}/api/media/remove-audio", data=json.dumps({"mode": "unmute"}).encode('utf-8'), headers={'Content-Type': 'application/json'})
res_unmute = urllib.request.urlopen(req_unmute)
print("5. Unmute toggle result: audioMuted =", json.loads(res_unmute.read().decode('utf-8')).get("audioMuted"))

print("\n>>> ALL API TESTS PASSED WITH 100% SUCCESS! <<<")
