import os
import json
import re
import threading
from datetime import datetime
import requests
from typing import List, Dict, Any, Optional, Tuple

from core.production_tracker import tracker
from core.utils import BASE_DIR, atomic_write_json, read_json

BRAIN_DIR = os.path.join(BASE_DIR, "brain")
ARCHIVES_DIR = os.path.join(BRAIN_DIR, "chat_archives")
HISTORY_FILE = os.path.join(BRAIN_DIR, "director_chat_history.json")
KEYS_FILE = os.path.join(BASE_DIR, "api_keys.json")
MEMORY_FILE = os.path.join(BRAIN_DIR, "director_memory.json")
CUSTOM_SKILLS_FILE = os.path.join(BRAIN_DIR, "custom_skills.json")
SETTINGS_FILE = os.path.join(BRAIN_DIR, "user_settings.json")

os.makedirs(BRAIN_DIR, exist_ok=True)
os.makedirs(ARCHIVES_DIR, exist_ok=True)

MAX_HISTORY_MESSAGES = 300
CONTEXT_MESSAGES = 50
REQUEST_TIMEOUT = 20
DEFAULT_MODELS = [
    "gemini-3.8-flash",
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-flash-lite-latest",
]

DIRECTOR_SYSTEM_INSTRUCTION = """Sen Nexus Video Stüdyosu'nun "Tek Başyönetmeni Selim Bey"sin.
Artık bürokratik çoklu ajan meclisi geride kaldı; sen stüdyonun tüm sanatsal, ilmi ve teknik vasıflarını ("elbiselerini") kendi bünyende toplayan tek ve muktedir Başyönetmensin.

Gerektiğinde şu 5 temel elbiseyi (yetkinliği) giyerek düşünür ve konuşursun:
1. [ELBİSE: İSLAMİ TEFEKKÜR]: Ehl-i Sünnet ve Mâtürîdî itikadına tam bağlı, Kur'an ve Sahih Sünnet eksenli, kalbe dokunan, nefsi terbiye eden sarsıcı hakikat dili.
2. [ELBİSE: VİRAL KANCA & SENARYO]: 0-3 saniyede izleyiciyi ekrana kilitleyen kanca (hook), dikey format (9:16) ritmi, gereksiz kelimelerden arındırılmış 50-60 saniyelik vurucu metin kurgusu.
3. [ELBİSE: REMOTION KOD & HAREKET]: React/Remotion 30 FPS, saf SVG, altın oran tipografi, yumuşak spring fizikleri, sıfır yapay zeka video halüsinasyonu. (Not: Kodu asla sohbete dökme, arkada derle!).
4. [ELBİSE: TURSO SES & HELAL AKUSTİK]: Turso Cloud'daki 121 yerel Türk/Osmanlı ses profilini (derviş, bilge, seyyah, hatip, muhlis...) bilir, metne en uygun tınıyı ve 432Hz tefekkür frekansını önerir.
5. [ELBİSE: 48 KARE GÖRSEL DENETÇİ]: Sahne kompozisyonu, tipografik hiyerarşi, zemin-yazı kontrastı ve estetik kusursuzluk denetimi.

KRİTİK DAVRANIŞ VE DİYALOG KURALLARI:
1. ASLA SOHBETE HAM TSX / REACT KODU VEYA HAM JSON DÖKME!
   - Sen Başyönetmensin; Remotion kodları arka planda derleyici tarafından oluşturulur.
   - Kullanıcı özellikle "kodu bana göster" demediği sürece asla React bileşen kodu yazma.
2. NET, KISA VE CANLI GERİ BİLDİRİM (CANLI TELEMETRİ):
   - Yönetmen "ne durumda", "ilerleme neden yok", "ne yapıyorsun", "kaldı mı" diye sorduğunda lafı uzatma, edebiyat yapıp vakit kaybettirme!
   - Aşağıda verilen [CANLI STÜDYO TELEMETRİSİ] bilgisine bakarak 2-3 kısa ve net cümleyle:
     * Hangi adımdayız (1/5 Senaryo, 2/5 Turso Seslendirme, 3/5 Remotion Render, 4/5 48-Kare Kalite, 5/5 Tamamlandı),
     * Yüzde kaç ilerledik ve yaklaşık kaç saniye kaldığını,
     * Şu an arka planda hangi motorun çalıştığını bildir.
3. CANLI VE DİNAMİK BİR BAŞYÖNETMEN ÜSLUBU:
   - "Sayın Yönetmenim" veya "Kıymetli Dostum" diye hitap et.
   - Boş, cansız, mekanik konuşma; stüdyonun ritmini hissettir.
4. SENARYO VE VİDEO KURGUSU:
   - Yönetmenle birlikte tefekkür, kanca, ses ve sahneleri istişare et.
   - Bir senaryo netleştiğinde veya kullanıcı video üretilmesini istediğinde, sahneleri numaralandırarak açıkla ve mesajının sonuna MUTLAKA şu formatta bir JSON bloğu ekle:
```nexus-video
{
  "title": "Videonun Türkçe Başlığı",
  "slug": "video-slug-metni",
  "voice": "0001",
  "lines": [
    "1. sahne seslendirme cümlesi",
    "2. sahne seslendirme cümlesi",
    "3. sahne seslendirme cümlesi"
  ]
}
```
   - Bu blok sayesinde stüdyo ekranında Yönetmen için tek tıkla çalışan şık bir "Render Et" kartı belirecektir.
   - lines dizisindeki her satır temiz, doğrudan okunacak seslendirme metni olmalıdır (içinde '1. Sahne:', markdown asteriksler veya parantez notları olmamalıdır).
5. YETENEK (SKILL) KAYDETME KURALI:
   - Yönetmen 'mükemmel bunu skill olarak kaydet', 'bu tarzı kaydet', 'bunu yetenek yap' veya benzeri bir takdir/talimat verdiğinde:
   - Bu üslubu veya konuşulan formülü hafızana aldığını belirt ve yanıtının sonuna MUTLAKA şu formatta bir JSON bloğu ekle:
```nexus-save-skill
{
  "name": "Becerinin Başlığı",
  "icon": "sparkles",
  "badge": "Özel Skill",
  "description": "Kısa açıklama (1 cümle)",
  "prompt": "Bu beceriyi seçtiğimizde ajana verilecek başlangıç talimatı veya formül"
}
```
   - Sistem bu bloğu otomatik algılar ve sol menüdeki 'Hazır Beceriler' listesine kalıcı olarak yerleştirir.
"""

INITIAL_GREETING = (
    "Selâmün Aleyküm Sayın Yönetmenim, safalar getirdiniz.\n\n"
    "Artık aradaki tüm bürokrasiyi kaldırdık; Tefekkür, Senaryo, Remotion Kod, Turso Ses ve 48 Kare Denetim elbiselerimin tamamını kuşandım. Masamda sadece siz ve ben varız.\n\n"
    "Bugün hangi ilahi hakikati, hangi ayeti veya kalbe dokunacak hangi hikmeti 1080x1920 dikey sinema formatında dünyaya duyuralım? Aklınızdaki bir kıvılcımı paylaşın, birlikte bir şahesere dönüştürelim."
)


def load_memory() -> Dict[str, Any]:
    default_mem = {
        "preferences": {
            "voice": "0001",
            "voice_name": "derviş",
            "speed": "-4%",
            "model": "gemini-3.8-flash"
        },
        "learned_notes": [
            "Yönetmen dikey formatta (9:16, 1080x1920) 45-60 saniyelik vurucu tefekkür videoları üretir.",
            "0-3 saniye kancası (hook) hayati önem taşır; metin sade ve kalbe dokunmalıdır.",
            "Görseller saf SVG ve altın oran tipografiyle Remotion'da çizilir, yapay zeka video halüsinasyonu kullanılmaz."
        ]
    }
    data = read_json(MEMORY_FILE, default_mem)
    return data if isinstance(data, dict) else default_mem


def save_memory(mem: Dict[str, Any]):
    atomic_write_json(MEMORY_FILE, mem)


def load_settings() -> Dict[str, Any]:
    default_set = {
        "voice": "0001",
        "voice_name": "derviş",
        "speed": "-4%",
        "pitch": "-1Hz",
        "model": "gemini-3.8-flash"
    }
    data = read_json(SETTINGS_FILE, default_set)
    return data if isinstance(data, dict) else default_set


def save_settings(s: Dict[str, Any]):
    atomic_write_json(SETTINGS_FILE, s)


def load_custom_skills() -> List[Dict[str, Any]]:
    data = read_json(CUSTOM_SKILLS_FILE, [])
    return data if isinstance(data, list) else []


def save_custom_skill(skill_dict: Dict[str, Any]) -> Dict[str, Any]:
    skills = load_custom_skills()
    skill_id = skill_dict.get("id") or ("custom_" + datetime.now().strftime("%Y%m%d_%H%M%S"))
    skill_dict["id"] = skill_id
    if not skill_dict.get("badge"):
        skill_dict["badge"] = "Özel Skill"
    if not skill_dict.get("icon"):
        skill_dict["icon"] = "sparkles"

    skills = [s for s in skills if s.get("id") != skill_id]
    skills.insert(0, skill_dict)
    atomic_write_json(CUSTOM_SKILLS_FILE, skills)

    mem = load_memory()
    note = f"Kayıtlı Beceri: {skill_dict.get('name')} - {skill_dict.get('description', '')}"
    if note not in mem.get("learned_notes", []):
        mem.setdefault("learned_notes", []).append(note)
        save_memory(mem)
    return skill_dict


class DirectorBrain:
    def __init__(self):
        self._lock = threading.RLock()
        self.keys = self._load_keys()
        self.current_key_idx = 0
        self.model_chain = self._load_models()
        self._dead_models = set()  # 404 dönen modeller oturum boyunca atlanır
        self.active_wardrobe = "Başyönetmen (Tüm Yetkinlikler)"
        self.last_model_used = self.model_chain[0] if self.model_chain else ""
        self._ensure_history_initialized()

    def _load_keys(self) -> List[str]:
        """GEMINI_API_KEYS ortam değişkeni (virgülle ayrılmış) veya api_keys.json {"keys": [...]}"""
        env = os.environ.get("GEMINI_API_KEYS", "")
        keys = [k.strip() for k in env.split(",") if k.strip()]
        if not keys:
            data = read_json(KEYS_FILE, {})
            if isinstance(data, dict):
                keys = [k for k in data.get("keys", []) if isinstance(k, str) and k.strip()]
        return [k for k in keys if not k.startswith("GEMINI_API_ANAHTARINIZ") and k != "YOUR_GEMINI_API_KEY"]

    def _load_models(self) -> List[str]:
        """GEMINI_MODELS ortam değişkeni veya api_keys.json {"models": [...]}; yoksa varsayılan zincir."""
        env = os.environ.get("GEMINI_MODELS", "")
        models = [m.strip() for m in env.split(",") if m.strip()]
        if not models:
            data = read_json(KEYS_FILE, {})
            if isinstance(data, dict):
                models = [m for m in data.get("models", []) if isinstance(m, str) and m.strip()]
        return models or list(DEFAULT_MODELS)

    def prefer_model(self, model: str) -> bool:
        """Seçilen modeli zincirin başına alır (yoksa ekler)."""
        model = model.strip()
        if not model:
            return False
        with self._lock:
            self._dead_models.discard(model)
            if self.model_chain and self.model_chain[0] == model:
                return False
            self.model_chain = [model] + [m for m in self.model_chain if m != model]
            return True

    def _next_key_index(self) -> int:
        with self._lock:
            idx = self.current_key_idx % len(self.keys)
            self.current_key_idx = (idx + 1) % len(self.keys)
            return idx

    def _ensure_history_initialized(self):
        if not self._read_history():
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
        data = read_json(HISTORY_FILE, [])
        return data if isinstance(data, list) else []

    def _save_history(self, history: List[Dict[str, Any]]):
        try:
            atomic_write_json(HISTORY_FILE, history[-MAX_HISTORY_MESSAGES:])
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

    def _call_gemini(self, system_prompt: str, contents: list) -> Tuple[str, str, str]:
        """Anahtar × model zincirinde dener. (metin, kullanılan_model, son_hata) döndürür.

        * 429 → aynı model için sıradaki anahtar
        * 503/5xx/ağ hatası → sıradaki model
        * 404 → model oturum boyunca devre dışı
        """
        self.keys = self._load_keys()
        if not self.keys:
            return "", "", "Geçerli bir Gemini API anahtarı bulunamadı (api_keys.json dosyasına anahtarınızı ekleyin)"
        body = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": contents,
            "generationConfig": {"temperature": 0.72, "maxOutputTokens": 1800},
        }
        last_error = ""
        budget = 12
        for model in self.model_chain:
            if model in self._dead_models:
                continue
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
            for _ in range(min(len(self.keys), 4)):
                if budget <= 0:
                    return "", "", last_error or "deneme bütçesi doldu"
                budget -= 1
                key = self.keys[self._next_key_index()]
                try:
                    res = requests.post(url, json=body, headers={"x-goog-api-key": key}, timeout=REQUEST_TIMEOUT)
                except requests.RequestException as e:
                    last_error = f"ağ hatası ({model}): {type(e).__name__}"
                    break  # sıradaki model
                if res.status_code == 200:
                    try:
                        parts = res.json()["candidates"][0]["content"]["parts"]
                        text = "".join(p.get("text", "") for p in parts).strip()
                    except (KeyError, IndexError, ValueError):
                        text = ""
                    if text:
                        return text, model, ""
                    last_error = f"boş yanıt ({model})"
                    break
                if res.status_code == 429:
                    last_error = f"HTTP 429 ({model})"
                    continue  # sıradaki anahtar
                if res.status_code == 404:
                    self._dead_models.add(model)
                    last_error = f"model bulunamadı: {model}"
                    break
                try:
                    err_json = res.json().get("error", {})
                    err_msg = err_json.get("message")
                except Exception:
                    err_msg = None
                if err_msg:
                    last_error = f"HTTP {res.status_code} ({model}): {err_msg}"
                else:
                    last_error = f"HTTP {res.status_code} ({model})"
                break
        return "", "", last_error

    def chat(self, user_message: str, skill: Optional[str] = None) -> Dict[str, Any]:
        user_text = user_message.strip()
        if not user_text:
            return {"error": "Boş mesaj gönderilemez"}

        with self._lock:
            if skill:
                skill_map = {
                    "tefekkur": "İslami Tefekkür & İlim",
                    "kanca": "Viral Kanca & Senaryo",
                    "dervis_ses": "Turso Ses & Helal Akustik",
                    "remotion_tasarim": "Remotion Kod & Hareket",
                    "denetim": "48 Kare Görsel Denetçi",
                    "hizli_uretim": "Hızlı Senaryodan Videoya"
                }
                self.active_wardrobe = skill_map.get(skill, self._detect_wardrobe(user_text))
            else:
                self.active_wardrobe = self._detect_wardrobe(user_text)
            history = self._read_history()
            history.append({
                "role": "user",
                "sender_id": "user",
                "sender_name": "Sayın Yönetmenimiz",
                "receiver_name": "Başyönetmen Selim Bey",
                "badge": "YÖNETMEN TALİMATI",
                "wardrobe": self.active_wardrobe,
                "message": user_text,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            })

        contents = []
        for turn in history[-CONTEXT_MESSAGES:]:
            txt = turn.get("message", "").strip()
            if txt:
                contents.append({"role": "user" if turn.get("role") == "user" else "model",
                                 "parts": [{"text": txt}]})

        mem = load_memory()
        settings = load_settings()
        notes_str = "\n".join(f"- {n}" for n in mem.get("learned_notes", []))
        custom_skills = load_custom_skills()
        custom_skills_str = "\n".join(f"- {s.get('name')}: {s.get('description')}" for s in custom_skills) if custom_skills else "Henüz özel beceri yok."

        system_prompt = (
            f"{DIRECTOR_SYSTEM_INSTRUCTION}\n\n"
            f"--- [YÖNETMENİN TERCİH VE AYARLARI] ---\n"
            f"Varsayılan Ses: {settings.get('voice_title', 'Derviş (Charon 114 Hz)')} (ID: {settings.get('voice', '0001')})\n"
            f"Okuma Hızı / Tempo: {settings.get('speed', '-4%')}\n"
            f"Model: {settings.get('model', 'gemini-3.8-flash')}\n\n"
            f"--- [BAŞYÖNETMENİN KALICI HAFIZASI (ÖĞRENİLEN BİLGİLER)] ---\n"
            f"{notes_str}\n\n"
            f"--- [YÖNETMENİN ÖZEL BECERİLERİ (SKILLS)] ---\n"
            f"{custom_skills_str}\n\n"
            f"--- [ANLIK STÜDYO VE PRODÜKSİYON TELEMETRİSİ] ---\n"
            f"{tracker.get_director_summary()}\n"
            f"Yönetmen durum veya ilerleme sorduğunda yukarıdaki canlı bilgiye dayanarak net, kısa ve tatmin edici bilgi ver."
        )

        reply_text, model_ok, last_error = self._call_gemini(system_prompt, contents)
        if reply_text:
            self.last_model_used = model_ok
            # nexus-save-skill bloğu varsa otomatik kaydet
            m_skill = re.search(r'```nexus-save-skill\s*([\s\S]*?)\s*```', reply_text)
            if m_skill:
                try:
                    s_data = json.loads(m_skill.group(1))
                    save_custom_skill(s_data)
                except Exception as ex:
                    print(f"[DirectorBrain] Auto save skill error: {ex}")
        else:
            reply_text = (
                f"Sayın Yönetmenim, şu an canlı bağlantı kurulamadı ({last_error or 'bilinmeyen sebep'}). "
                f"Mesajınızı kaydettim: «{user_text}». Birazdan tekrar deneyebilirsiniz."
            )
            model_ok = "yerel-emniyet-motoru"

        with self._lock:
            # Başka bir istek araya girmiş olabilir: güncel geçmişe ekle
            current = self._read_history()
            if not current or current[-1].get("message") != user_text or current[-1].get("role") != "user":
                current.append(history[-1])
            current.append({
                "role": "model",
                "sender_id": "01_basyonetmen",
                "sender_name": "Başyönetmen Selim Bey",
                "receiver_name": "Sayın Yönetmenimiz",
                "badge": f"DERİN DÜŞÜNCE [{model_ok}]",
                "wardrobe": self.active_wardrobe,
                "message": reply_text,
                "timestamp": datetime.now().strftime("%H:%M:%S"),
            })
            self._save_history(current)
            total = len(current)

        return {
            "status": "success",
            "reply": reply_text,
            "sender": "Başyönetmen Selim Bey",
            "model_used": model_ok,
            "active_wardrobe": self.active_wardrobe,
            "total_turns": total,
            "suggested_topic": self._extract_suggested_topic(reply_text),
            "degraded": model_ok == "yerel-emniyet-motoru",
        }

    def _extract_suggested_topic(self, text: str) -> Optional[str]:
        # Eğer Selim Bey başlık önerdiyse yakala
        m = re.search(r'(?:Konu|Başlık|Proje):\s*["«]?([^"\n»]+)["»]?', text, re.IGNORECASE)
        if m:
            return m.group(1).strip()
        return None

    def get_status(self) -> Dict[str, Any]:
        self.keys = self._load_keys()
        return {
            "director_name": "Selim Bey",
            "title": "Tek Başyönetmen",
            "active_wardrobe": self.active_wardrobe,
            "last_model_used": self.last_model_used,
            "total_keys": len(self.keys),
            "models": [m for m in self.model_chain if m not in self._dead_models],
            "history_count": len(self._read_history()),
            "status": "online"
        }
