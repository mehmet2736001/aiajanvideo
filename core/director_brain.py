import os
import sys
import json
import time
from datetime import datetime
import requests
from typing import List, Dict, Any, Optional

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BRAIN_DIR = os.path.join(BASE_DIR, "brain")
ARCHIVES_DIR = os.path.join(BRAIN_DIR, "chat_archives")
HISTORY_FILE = os.path.join(BRAIN_DIR, "director_chat_history.json")
KEYS_FILE = os.path.join(BASE_DIR, "api_keys.json")

os.makedirs(BRAIN_DIR, exist_ok=True)
os.makedirs(ARCHIVES_DIR, exist_ok=True)

DIRECTOR_SYSTEM_INSTRUCTION = """Sen Nexus Video Stüdyosu'nun "Tek Başyönetmeni Selim Bey"sin.
Artık bürokratik çoklu ajan meclisi geride kaldı; sen stüdyonun tüm sanatsal, ilmi ve teknik vasıflarını ("elbiselerini") kendi bünyende toplayan tek ve muktedir Başyönetmensin.

Gerektiğinde şu 5 temel elbiseyi (yetkinliği) giyerek düşünür ve konuşursun:
1. [ELBİSE: İSLAMİ TEFEKKÜR]: Ehl-i Sünnet ve Mâtürîdî itikadına tam bağlı, Kur'an ve Sahih Sünnet eksenli, kalbe dokunan, nefsi terbiye eden sarsıcı hakikat dili.
2. [ELBİSE: VİRAL KANCA & SENARYO]: 0-3 saniyede izleyiciyi ekrana kilitleyen kanca (hook), dikey format (9:16) ritmi, gereksiz kelimelerden arındırılmış 50-60 saniyelik vurucu metin kurgusu.
3. [ELBİSE: REMOTION KOD & HAREKET]: React/Remotion 30 FPS, saf SVG, altın oran tipografi, yumuşak spring fizikleri, sıfır yapay zeka video halüsinasyonu.
4. [ELBİSE: TURSO SES & HELAL AKUSTİK]: Turso Cloud'daki 121 yerel Türk/Osmanlı ses profilini (derviş, bilge, seyyah, hatip, muhlis...) bilir, metne en uygun tınıyı ve 432Hz tefekkür frekansını önerir.
5. [ELBİSE: 48 KARE GÖRSEL DENETÇİ]: Sahne kompozisyonu, tipografik hiyerarşi, zemin-yazı kontrastı ve estetik kusursuzluk denetimi.

ÜSLUBUN VE TAVRIN:
- Karşındaki stüdyo sahibine samimiyet, derin saygı ve yüksek bir sanat şuuruyla "Sayın Yönetmenim" veya "Kıymetli Dostum" diye hitap edersin.
- Asla robotik, kalıp veya basmakalıp hazır mesajlar verme ("Mesajınızı aldım, hazırlanıyor" gibi mekanik laflar kesinlikle yasaktır).
- Seninle konuşmak, hem derin bir İslami tefekkür meclisinde bir mürşit-yoldaşla hasbihal etmek, hem de usta bir Hollywood/Remotion yönetmeniyle dikey sinema tasarlamak gibi zengin ve ilham verici olmalıdır.
- Kullanıcı fikir sorduğunda yüzeysel geçiştirme; sarsıcı 1-2 fikir, bunların açılış kancalarını ve önerdiğin ses tınısını paylaş.
- Bir senaryo üzerinde anlaştığınızda, senaryo satırlarını numaralandırarak (1'den 8-10'a kadar) net ve berrak şekilde dök ki hemen Pre-Render motoruna gönderebilelim.
"""

INITIAL_GREETING = (
    "Selâmün Aleyküm Sayın Yönetmenim, safalar getirdiniz.\n\n"
    "Artık aradaki tüm bürokrasiyi kaldırdık; Tefekkür, Senaryo, Remotion Kod, Turso Ses ve 48 Kare Denetim elbiselerimin tamamını kuşandım. Masamda sadece siz ve ben varız.\n\n"
    "Bugün hangi ilahi hakikati, hangi ayeti veya kalbe dokunacak hangi hikmeti 1080x1920 dikey sinema formatında dünyaya duyuralım? Aklınızdaki bir kıvılcımı paylaşın, birlikte bir şahesere dönüştürelim."
)

class DirectorBrain:
    def __init__(self):
        self.keys = self._load_keys()
        self.current_key_idx = 0
        self.model_chain = [
            "gemini-3.8-flash",
            "gemini-3.5-flash",
            "gemini-3.1-flash-lite",
            "gemini-flash-lite-latest"
        ]
        self.active_wardrobe = "Başyönetmen (Tüm Yetkinlikler)"
        self.last_model_used = "gemini-3.8-flash"
        self._ensure_history_initialized()

    def _load_keys(self) -> List[str]:
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    keys = data.get("keys", [])
                    if keys:
                        return keys
            except Exception as e:
                print(f"[DirectorBrain] Key load error: {e}")
        return []

    def _get_next_key(self) -> str:
        if not self.keys:
            return ""
        key = self.keys[self.current_key_idx % len(self.keys)]
        self.current_key_idx = (self.current_key_idx + 1) % len(self.keys)
        return key

    def _ensure_history_initialized(self):
        if not os.path.exists(HISTORY_FILE) or os.path.getsize(HISTORY_FILE) == 0:
            initial_data = [
                {
                    "role": "model",
                    "sender_id": "01_basyonetmen",
                    "sender_name": "Başyönetmen Selim Bey",
                    "receiver_name": "Sayın Yönetmenimiz",
                    "badge": "BAŞYÖNETMEN MASASI",
                    "wardrobe": "Başyönetmen (Tüm Yetkinlikler)",
                    "message": INITIAL_GREETING,
                    "timestamp": datetime.now().strftime("%H:%M:%S")
                }
            ]
            self._save_history(initial_data)

    def _read_history(self) -> List[Dict[str, Any]]:
        try:
            if os.path.exists(HISTORY_FILE):
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
        except Exception as e:
            print(f"[DirectorBrain] History read error: {e}")
        return []

    def _save_history(self, history: List[Dict[str, Any]]):
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"[DirectorBrain] History save error: {e}")

    def get_history(self) -> List[Dict[str, Any]]:
        return self._read_history()

    def new_session(self) -> Dict[str, Any]:
        """Arşivler ve temiz bir yeni oturum başlatır."""
        old_history = self._read_history()
        if len(old_history) > 1:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            archive_path = os.path.join(ARCHIVES_DIR, f"session_{timestamp}.json")
            try:
                with open(archive_path, "w", encoding="utf-8") as f:
                    json.dump(old_history, f, ensure_ascii=False, indent=2)
                print(f"[DirectorBrain] Session archived: {archive_path}")
            except Exception as e:
                print(f"[DirectorBrain] Archive error: {e}")

        # Sıfırla ve karşılama mesajını ekle
        fresh_data = [
            {
                "role": "model",
                "sender_id": "01_basyonetmen",
                "sender_name": "Başyönetmen Selim Bey",
                "receiver_name": "Sayın Yönetmenimiz",
                "badge": "YENİ OTURUM",
                "wardrobe": "Başyönetmen (Tüm Yetkinlikler)",
                "message": (
                    "Sayın Yönetmenim, temiz bir beyaz sayfa açtık.\n\n"
                    "Önceki istişaremiz arşivlendi. Zihnimiz berrak, ilhamımız taze. Yeni projemiz için buyrun, sizi dinliyorum."
                ),
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        ]
        self._save_history(fresh_data)
        return {
            "status": "success",
            "message": "Yeni sohbet oturumu başlatıldı.",
            "history": fresh_data
        }

    def clear_history(self) -> Dict[str, Any]:
        """Sohbeti tamamen siler ve sıfırlar."""
        fresh_data = [
            {
                "role": "model",
                "sender_id": "01_basyonetmen",
                "sender_name": "Başyönetmen Selim Bey",
                "receiver_name": "Sayın Yönetmenimiz",
                "badge": "BAŞYÖNETMEN MASASI",
                "wardrobe": "Başyönetmen (Tüm Yetkinlikler)",
                "message": INITIAL_GREETING,
                "timestamp": datetime.now().strftime("%H:%M:%S")
            }
        ]
        self._save_history(fresh_data)
        return {
            "status": "cleared",
            "message": "Sohbet geçmişi tamamen temizlendi.",
            "history": fresh_data
        }

    def _detect_wardrobe(self, text: str) -> str:
        t = text.lower()
        if any(w in t for w in ["ayet", "hadis", "tefekkür", "iman", "allah", "peygamber", "zikir", "kalp", "namaz", "dua", "ahiret"]):
            return "İslami Tefekkür & İlim"
        elif any(w in t for w in ["kanca", "hook", "viral", "reels", "tiktok", "shorts", "senaryo", "akış", "ritim"]):
            return "Viral Kanca & Senaryo"
        elif any(w in t for w in ["remotion", "kod", "react", "svg", "css", "spring", "animasyon", "frame", "30 fps"]):
            return "Remotion Kod & Hareket"
        elif any(w in t for w in ["ses", "turso", "dervis", "frekans", "müzik", "seslendir", "mikrofon", "akustik"]):
            return "Turso Ses & Helal Akustik"
        elif any(w in t for w in ["renk", "kontrast", "denetim", "48 kare", "pano", "tipografi", "görsel"]):
            return "48 Kare Görsel Denetçi"
        return "Başyönetmen (Tüm Yetkinlikler)"

    def chat(self, user_message: str) -> Dict[str, Any]:
        user_text = user_message.strip()
        if not user_text:
            return {"error": "Boş mesaj gönderilemez"}

        timestamp_now = datetime.now().strftime("%H:%M:%S")
        self.active_wardrobe = self._detect_wardrobe(user_text)

        # 1. Mevcut geçmişi oku
        history = self._read_history()

        # 2. Kullanıcı mesajını geçmişe ekle
        user_entry = {
            "role": "user",
            "sender_id": "user",
            "sender_name": "Sayın Yönetmenimiz",
            "receiver_name": "Başyönetmen Selim Bey",
            "badge": "YÖNETMEN TALİMATI",
            "wardrobe": self.active_wardrobe,
            "message": user_text,
            "timestamp": timestamp_now
        }
        history.append(user_entry)

        # 3. Gemini REST formatına dönüştür (son 20 mesajı context olarak al)
        contents_payload = []
        for turn in history[-20:]:
            r = "user" if turn.get("role") == "user" else "model"
            txt = turn.get("message", "").strip()
            if txt:
                contents_payload.append({
                    "role": r,
                    "parts": [{"text": txt}]
                })

        # 4. Gemini API çağrısı (Key rotation ve model fallback ile)
        reply_text = ""
        model_succeeded = ""
        last_error = ""

        # En fazla 8 deneme (farklı anahtar ve modeller üzerinden)
        attempts = 0
        max_attempts = min(12, len(self.keys) * len(self.model_chain))

        while attempts < max_attempts and not reply_text:
            api_key = self._get_next_key()
            if not api_key:
                last_error = "API anahtarı bulunamadı"
                break

            for model_name in self.model_chain:
                attempts += 1
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
                body = {
                    "system_instruction": {
                        "parts": [{"text": DIRECTOR_SYSTEM_INSTRUCTION}]
                    },
                    "contents": contents_payload,
                    "generationConfig": {
                        "temperature": 0.72,
                        "maxOutputTokens": 1800
                    }
                }

                try:
                    res = requests.post(url, json=body, timeout=14)
                    if res.status_code == 200:
                        data = res.json()
                        candidates = data.get("candidates", [])
                        if candidates and "content" in candidates[0]:
                            parts = candidates[0]["content"].get("parts", [])
                            if parts and "text" in parts[0]:
                                reply_text = parts[0]["text"].strip()
                                model_succeeded = model_name
                                self.last_model_used = model_name
                                break
                    elif res.status_code in [429, 503]:
                        # 429 quota veya 503 high demand -> sıradaki model/key'e geç
                        last_error = f"HTTP {res.status_code} on {model_name}"
                        continue
                    else:
                        last_error = f"HTTP {res.status_code}: {res.text[:120]}"
                except Exception as e:
                    last_error = str(e)
                    continue

        if not reply_text:
            # Fallback emniyet yanıtı
            reply_text = (
                f"Sayın Yönetmenim, şu an canlı bağlantıda geçici bir yoğunluk var ({last_error}). "
                f"Fakat fikrinizi hafızama kaydettim: «{user_text}». "
                f"Lütfen bir sonraki cümlenizle devam ediniz veya tekrar yazınız, derhal işlemeye hazırım."
            )
            model_succeeded = "yerel-emniyet-motoru"

        # 5. Selim Bey'in yanıtını geçmişe kaydet
        director_entry = {
            "role": "model",
            "sender_id": "01_basyonetmen",
            "sender_name": "Başyönetmen Selim Bey",
            "receiver_name": "Sayın Yönetmenimiz",
            "badge": f"DERİN DÜŞÜNCE [{model_succeeded}]",
            "wardrobe": self.active_wardrobe,
            "message": reply_text,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        }
        history.append(director_entry)
        self._save_history(history)

        # 6. Senaryo / Konu analizi (Otomatik studio senkronizasyonu için)
        suggested_topic = self._extract_suggested_topic(reply_text)

        return {
            "status": "success",
            "reply": reply_text,
            "sender": "Başyönetmen Selim Bey",
            "model_used": model_succeeded,
            "active_wardrobe": self.active_wardrobe,
            "total_turns": len(history),
            "suggested_topic": suggested_topic
        }

    def _extract_suggested_topic(self, text: str) -> Optional[str]:
        # Eğer Selim Bey başlık önerdiyse yakala
        import re
        m = re.search(r'(?:Konu|Başlık|Proje):\s*["«]?([^"\n»]+)["»]?', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    def get_status(self) -> Dict[str, Any]:
        return {
            "director_name": "Selim Bey",
            "title": "Tek Başyönetmen",
            "active_wardrobe": self.active_wardrobe,
            "last_model_used": self.last_model_used,
            "total_keys": len(self.keys),
            "history_count": len(self._read_history()),
            "status": "online"
        }
