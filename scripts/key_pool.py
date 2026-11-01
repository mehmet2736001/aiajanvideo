import os
import csv
import json
import time
import requests
from typing import List, Dict, Optional, Tuple

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")
CSV_PATH = os.path.join(DATA_DIR, "api_keys.csv")
JSON_PATH = os.path.join(DATA_DIR, "api_keys.json")

DEFAULT_MODEL = "gemini-3.5-flash-lite"

SUPPORTED_MODELS = [
    # --- GEMINI 4 SERİSİ (FLAGSHIP & NEXT-GEN) ---
    {
        "id": "gemini-4-argon",
        "name": "Gemini 4 Argon",
        "series": "Gemini 4",
        "badge": "🪐 4. Nesil Flagship (Argon)",
        "desc": "Google'ın yeni nesil 4. seri Argon mimarisi; ultra derin akıl yürütme ve devasa kurgusal bağlam."
    },
    {
        "id": "gemma-4-31b-it",
        "name": "Gemma 4 31B IT",
        "series": "Gemini 4 / Gemma",
        "badge": "🔬 DeepMind 31B Talimat",
        "desc": "Google DeepMind'ın 31 milyar parametreli açık ağırlıklı 4. nesil talimat ve mantık motoru."
    },
    {
        "id": "gemma-4-26b-a4b-it",
        "name": "Gemma 4 26B A4B IT",
        "series": "Gemini 4 / Gemma",
        "badge": "⚡ Optimize 4. Nesil",
        "desc": "Yüksek verimli multimodal 26B mimarisi, hızlı ve keskin senaryo yapılandırması."
    },

    # --- GEMINI 3.8 & 3.7 SERİSİ (YENİ NESİL ULTRA HIZLI FLASH) ---
    {
        "id": "gemini-3.8-flash",
        "name": "Gemini 3.8 Flash",
        "series": "Gemini 3.8",
        "badge": "⚡ Ultra Hızlı 3.8 Çekirdeği",
        "desc": "Gemini 3 serisinin en yeni 3.8 sürümü, anlık metin ve senaryo analizi için optimize edildi."
    },
    {
        "id": "gemini-3.7-flash",
        "name": "Gemini 3.7 Flash",
        "series": "Gemini 3.7",
        "badge": "💡 Hibrit Düşünme Motoru",
        "desc": "Gelişmiş akıl yürütme yetenekleri ile dinamik Flash hızını birleştiren 3.7 nesli."
    },
    {
        "id": "gemini-3.6-flash",
        "name": "Gemini 3.6 Flash",
        "series": "Gemini 3.6",
        "badge": "🚀 Kararlı Flash 3.6",
        "desc": "Yüksek kurgusal zeka, akıcı Türkçe anlatım ve derin bağlam analizi."
    },

    # --- GEMINI 3.5 & 3 SERİSİ (PRODÜKSİYON STANDARTLARI) ---
    {
        "id": "gemini-3.5-flash-lite",
        "name": "Gemini 3.5 Flash Lite",
        "series": "Gemini 3.5",
        "badge": "⚡ Varsayılan (Ultra Hızlı)",
        "desc": "Google'ın yeni nesil Gemini 3 mimarisi, en düşük gecikme ve anlık JSON kurgu üretimi."
    },
    {
        "id": "gemini-3.5-flash",
        "name": "Gemini 3.5 Flash",
        "series": "Gemini 3.5",
        "badge": "🚀 Dengeli & Güçlü",
        "desc": "Yüksek kurgusal zeka, akıcı Türkçe anlatım ve derin bağlam analizi."
    },
    {
        "id": "gemini-3.1-pro-preview",
        "name": "Gemini 3.1 Pro Preview",
        "series": "Gemini 3.1",
        "badge": "🧠 En Yüksek Akıl Yürütme",
        "desc": "En derin felsefi, bilimsel ve tefekkür çıkarımları için Pro akıl yürütme motoru."
    },
    {
        "id": "gemini-3.1-flash-lite",
        "name": "Gemini 3.1 Flash Lite",
        "series": "Gemini 3.1",
        "badge": "🎯 Hafif & Seri",
        "desc": "Kompakt ve ekonomik 3.1 Flash mimarisi."
    },
    {
        "id": "gemini-3-flash-preview",
        "name": "Gemini 3 Flash Preview",
        "series": "Gemini 3",
        "badge": "🔮 Yeni Nesil Preview",
        "desc": "Gemini 3 serisinin deneysel önizleme sürümü."
    },

    # --- GEMINI OMNI & LATEST SERİSİ ---
    {
        "id": "gemini-omni-1.1-flash",
        "name": "Gemini Omni 1.1 Flash",
        "series": "Omni",
        "badge": "🌐 Çok Modlu Omni",
        "desc": "Görsel, ses ve metin füzyonlu çok modlu Omni modeli."
    },
    {
        "id": "gemini-omni-flash-preview",
        "name": "Gemini Omni Flash Preview",
        "series": "Omni",
        "badge": "🔮 Omni Önizleme",
        "desc": "Gelişmiş multimodal medya analizi sağlayan Omni önizleme motoru."
    },
    {
        "id": "gemini-flash-latest",
        "name": "Gemini Flash Latest",
        "series": "Latest",
        "badge": "🔄 Daima Güncel",
        "desc": "Google Cloud'daki en son kararlı Flash model checkpoint'i."
    },
    {
        "id": "gemini-pro-latest",
        "name": "Gemini Pro Latest",
        "series": "Latest",
        "badge": "🔄 Daima Güncel Pro",
        "desc": "Google Cloud'daki en son kararlı Pro model checkpoint'i."
    },

    # --- GEMINI 2.5 SERİSİ (KLASİK) ---
    {
        "id": "gemini-2.5-pro",
        "name": "Gemini 2.5 Pro",
        "series": "Gemini 2.5",
        "badge": "🏛️ Klasik Pro",
        "desc": "Yüksek doğruluk ve detaylı senaryo kurma yeteneği."
    },
    {
        "id": "gemini-2.5-flash",
        "name": "Gemini 2.5 Flash",
        "series": "Gemini 2.5",
        "badge": "🏛️ Stabil Hızlı",
        "desc": "Klasik ve stabil hızlı üretim motoru."
    },
    {
        "id": "gemini-2.5-flash-lite",
        "name": "Gemini 2.5 Flash-Lite",
        "series": "Gemini 2.5",
        "badge": "🏛️ Hafif Klasik",
        "desc": "Minimum gecikmeli klasik Flash Lite."
    }
]

class KeyPoolManager:
    def __init__(self):
        self.keys: List[Dict] = []
        self.load_keys()

    def load_keys(self):
        # If JSON exists, load it, otherwise load from CSV
        if os.path.exists(JSON_PATH):
            try:
                with open(JSON_PATH, "r", encoding="utf-8") as f:
                    self.keys = json.load(f)
                return
            except Exception as e:
                print("JSON load failed, falling back to CSV:", e)

        if os.path.exists(CSV_PATH):
            with open(CSV_PATH, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    api_key = row.get("api_key", "").strip()
                    is_active = str(row.get("is_active", "true")).lower() == "true"
                    key_type = "gemini_direct" if api_key.startswith("AIzaSy") else "vertex_custom"
                    self.keys.append({
                        "id": row.get("id"),
                        "key_name": row.get("key_name", "Unnamed"),
                        "api_key": api_key,
                        "key_type": key_type,
                        "is_active": is_active,
                        "tier": row.get("tier", "free"),
                        "daily_request_count": int(row.get("daily_request_count", 0)),
                        "success_count": 0,
                        "error_count": 0,
                        "last_used_at": row.get("last_used_at", ""),
                        "last_error_at": row.get("last_error_at", ""),
                        "last_error_message": row.get("last_error_message", ""),
                        "status": "healthy"
                    })
            self.save_keys()

    def save_keys(self):
        os.makedirs(DATA_DIR, exist_ok=True)
        with open(JSON_PATH, "w", encoding="utf-8") as f:
            json.dump(self.keys, f, ensure_ascii=False, indent=2)

    def get_active_keys(self, key_type: Optional[str] = None) -> List[Dict]:
        active = [k for k in self.keys if k.get("is_active", True) and k.get("status") != "permanently_disabled"]
        if key_type:
            active = [k for k in active if k.get("key_type") == key_type]
        # Sort by least recently used and lowest error count
        active.sort(key=lambda k: (k.get("error_count", 0), k.get("daily_request_count", 0)))
        return active

    def test_key(self, key_item: Dict, model: str = DEFAULT_MODEL) -> Tuple[bool, str]:
        api_key = key_item["api_key"]
        selected_model = model or DEFAULT_MODEL
        if key_item["key_type"] == "gemini_direct":
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{selected_model}:generateContent?key={api_key}"
            payload = {"contents": [{"parts": [{"text": "ping"}]}]}
            try:
                res = requests.post(url, json=payload, timeout=6)
                if res.status_code == 200:
                    key_item["status"] = "healthy"
                    key_item["last_error_message"] = ""
                    self.save_keys()
                    return True, "Başarılı (200 OK)"
                else:
                    err = res.json().get("error", {}).get("message", res.text[:80])
                    key_item["last_error_message"] = err
                    key_item["last_error_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                    if res.status_code in [429, 503]:
                        key_item["status"] = "rate_limited"
                    elif res.status_code in [400, 403]:
                        key_item["status"] = "invalid_or_expired"
                    self.save_keys()
                    return False, f"Hata ({res.status_code}): {err[:60]}"
            except Exception as e:
                return False, f"Bağlantı hatası: {str(e)[:50]}"
        else:
            return True, "Vertex/Proxy Key (Doğrudan test desteklenmiyor)"

    def query_with_rotation(self, prompt: str, system_instruction: str = "", model: str = DEFAULT_MODEL) -> Tuple[Optional[str], Optional[str]]:
        """Rotates through active Gemini direct keys until one succeeds, with intelligent fallback cascade"""
        selected_model = model or DEFAULT_MODEL
        active_keys = self.get_active_keys("gemini_direct")
        if not active_keys:
            active_keys = [k for k in self.keys if k.get("key_type") == "gemini_direct"]

        # Models to try in cascade if primary model is rate limited or quota restricted
        models_to_try = [selected_model]
        for m in ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash", "gemini-flash-latest"]:
            if m not in models_to_try:
                models_to_try.append(m)

        for current_model in models_to_try[:3]:  # Try primary and up to 2 fallbacks
            errors = []
            for key_item in active_keys[:8]:  # Try top 8 healthiest keys
                api_key = key_item["api_key"]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{current_model}:generateContent?key={api_key}"
            
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}]
                }
                if system_instruction:
                    payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}

                try:
                    res = requests.post(url, json=payload, timeout=12)
                    if res.status_code == 200:
                        data = res.json()
                        text = data["candidates"][0]["content"]["parts"][0]["text"]
                        key_item["daily_request_count"] += 1
                        key_item["success_count"] = key_item.get("success_count", 0) + 1
                        key_item["last_used_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        key_item["status"] = "healthy"
                        self.save_keys()
                        return text, f"{key_item['key_name']} ({current_model})"
                    else:
                        err = res.json().get("error", {}).get("message", res.text[:80])
                        key_item["error_count"] = key_item.get("error_count", 0) + 1
                        key_item["last_error_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
                        key_item["last_error_message"] = err
                        errors.append(f"{key_item['id']} ({err[:40]})")
                        if res.status_code in [429, 503]:
                            key_item["status"] = "rate_limited"
                        self.save_keys()
                        continue
                except Exception as e:
                    key_item["error_count"] = key_item.get("error_count", 0) + 1
                    key_item["last_error_message"] = str(e)
                    errors.append(f"{key_item['id']} ({str(e)[:40]})")
                    self.save_keys()
                    continue

            print(f"[KeyPool] {current_model} ile tüm anahtarlar denendi, sonuç alınamadı. Hatalar: {len(errors)}")

        return None, None

pool = KeyPoolManager()

if __name__ == "__main__":
    print(f"Toplam Yüklenen Key Sayısı: {len(pool.keys)}")
    gemini_keys = [k for k in pool.keys if k["key_type"] == "gemini_direct"]
    print(f"Gemini AI Studio Key Sayısı: {len(gemini_keys)}")
    print("İlk 3 Gemini key test ediliyor...")
    for k in gemini_keys[:3]:
        ok, msg = pool.test_key(k)
        print(f"Key {k['id']} ({k['key_name']}): {msg}")
