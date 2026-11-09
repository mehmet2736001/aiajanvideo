import os
import sys
import json
import base64
import sqlite3
import urllib.request
import urllib.error
from typing import Dict, List, Optional, Tuple, Any

# Windows encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOCAL_DB_PATH = os.path.join(BASE_DIR, "brain", "aisesler.db")
CREDS_FILE = os.path.join(BASE_DIR, "turso_credentials.json")

DEFAULT_CONFIG = {
    "org_slug": "zakirun002",
    "db_name": "aisesler",
    "db_url": "https://aisesler-zakirun002.aws-eu-west-1.turso.io/v2/pipeline",
    "api_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJicFZKZWMtR0VmR25QQ0x4WGlLNERRIiwib3JnX2lkIjoxMDAwMjgyNTIyfQ.Z5NwQkwV64bk_ca4PIMkWNLmR230tDbRvxBDc4w2YoPxPpcOQDzdzgbzWS2pKckHMASDEnbzqmrnFRS_CXw0Dg",
    "jwt_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTM5MDU4OTYsImlkIjoiMDFhMWE4MjEtZWMwMS03N2QzLTkxZGMtOGMwMzRlOWQ1MTM2Iiwia2lkIjoidUd6SUVaT0Y4cnhTWW9aUENJcVFqWkNleExuaFNrTE9PSVVWNXVISkE1VSIsInJpZCI6Ijc3ZjgyZThjLTQ1MGItNGNhMC1hMjM5LTNiNWVkNzdlNDczNCJ9.NQJY50ZoL03UZkPoXG_zKHjCTsXt99-ENrPL6OW6RuW_ZOtLd-f4-EP6aCOcs4_4zPIT3FyJxrCzzCrIo4qxCA"
}


class TursoVoiceClient:
    """
    VoxAtelier v3.0 Uyumlu Ses İstemcisi.
    Öncelikli olarak yerel 'brain/aisesler.db' (SQLite) üzerinden 0 ms gecikmeyle çalışır.
    Yerel veritabanı bulunamazsa Turso Cloud pipeline'ına yedek olarak bağlanır.
    """

    def __init__(self, local_db_path: str = LOCAL_DB_PATH):
        self.local_db_path = local_db_path
        self.load_creds()

    def has_local_db(self) -> bool:
        return os.path.isfile(self.local_db_path)

    def load_creds(self):
        if os.path.exists(CREDS_FILE):
            try:
                with open(CREDS_FILE, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
                    return
            except Exception:
                pass
        self.config = DEFAULT_CONFIG.copy()
        self.save_creds()

    def save_creds(self):
        try:
            with open(CREDS_FILE, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2)
        except Exception:
            pass

    def refresh_jwt_token(self):
        """Turso Platform API üzerinden yeni bir DB JWT token alır."""
        org = self.config.get("org_slug", "zakirun002")
        db = self.config.get("db_name", "aisesler")
        api_token = self.config.get("api_token")
        url = f"https://api.turso.tech/v1/organizations/{org}/databases/{db}/auth/tokens"

        req = urllib.request.Request(
            url,
            headers={"Authorization": f"Bearer {api_token}"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            new_jwt = data.get("jwt")
            if new_jwt:
                self.config["jwt_token"] = new_jwt
                self.save_creds()
                return new_jwt
        return None

    def _query_local(self, sql: str, args: tuple = ()) -> List[dict]:
        """Yerel SQLite veritabanından doğrudan sorgu çalıştırır."""
        conn = sqlite3.connect(self.local_db_path)
        conn.row_factory = sqlite3.Row
        try:
            cursor = conn.cursor()
            cursor.execute(sql, args)
            rows = cursor.fetchall()
            return [dict(r) for r in rows]
        finally:
            conn.close()

    def _execute_local(self, sql: str, args: tuple = ()) -> int:
        """Yerel SQLite veritabanında yazma işlemi yapar."""
        conn = sqlite3.connect(self.local_db_path)
        try:
            cursor = conn.cursor()
            cursor.execute(sql, args)
            conn.commit()
            return cursor.rowcount
        finally:
            conn.close()

    def _query_cloud(self, sql: str, args: list = None) -> list:
        """Turso pipeline endpoint'ine HTTP isteği gönderir."""
        stmt = {"sql": sql}
        if args:
            stmt["args"] = [{"type": "text", "value": str(a)} for a in args]

        payload = {"requests": [{"type": "execute", "stmt": stmt}]}
        body = json.dumps(payload).encode("utf-8")

        for attempt in range(2):
            req = urllib.request.Request(
                self.config["db_url"],
                data=body,
                headers={
                    "Authorization": f"Bearer {self.config.get('jwt_token')}",
                    "Content-Type": "application/json"
                },
                method="POST"
            )
            try:
                with urllib.request.urlopen(req, timeout=10) as resp:
                    res = json.loads(resp.read().decode())
                    results = res.get("results", [])
                    if results and results[0].get("type") == "ok":
                        exec_res = results[0]["response"]["result"]
                        cols = [c["name"] for c in exec_res.get("cols", [])]
                        rows = []
                        for row in exec_res.get("rows", []):
                            row_dict = {}
                            for i, col in enumerate(cols):
                                cell = row[i]
                                row_dict[col] = cell.get("value")
                            rows.append(row_dict)
                        return rows
                    elif results and results[0].get("type") == "error":
                        raise RuntimeError(results[0].get("error", "Turso hatası"))
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt == 0:
                    self.refresh_jwt_token()
                    continue
                raise e
        return []

    def execute(self, sql: str, args: list = None) -> list:
        if self.has_local_db():
            try:
                return self._query_local(sql, tuple(args) if args else ())
            except Exception as e:
                print(f"[TURSO CLIENT] Yerel DB hatası, buluta yönlendiriliyor: {e}")
        return self._query_cloud(sql, args)

    def list_voices(self) -> List[dict]:
        """
        VoxAtelier standartlarında tüm sesleri listeler.
        Sıralama: Kalp puanı (3 kalp en üstte) -> favoriler -> ses_id sıralı.
        """
        sql = """
            SELECT ses_id, id, display_name, turkish_title, yas, cinsiyet, unvan,
                   category, custom_category, api_voice_name, gender, pitch_hz, pitch_ratio,
                   is_favorite, heart_rating, audio_duration, updated_at, timbre, emotion_tone,
                   (audio_base64 IS NOT NULL AND length(audio_base64) > 100) AS has_sample
            FROM voices 
            ORDER BY CAST(heart_rating AS INTEGER) DESC, is_favorite DESC, ses_id ASC
        """
        try:
            rows = self.execute(sql)
        except Exception:
            # Sütun uyumluluğu için basit sorgu fallback'i
            sql_fallback = """
                SELECT ses_id, id, display_name, turkish_title, api_voice_name, gender, 
                       category, pitch_hz, pitch_ratio, is_favorite, heart_rating, audio_duration, updated_at
                FROM voices 
                ORDER BY CAST(heart_rating AS INTEGER) DESC, is_favorite DESC, rowid ASC
            """
            rows = self.execute(sql_fallback)

        voices = []
        for r in rows:
            is_fav = bool(r.get("is_favorite") in (1, "1", True))
            dur = None
            try:
                if r.get("audio_duration"):
                    dur = round(float(r["audio_duration"]), 1)
            except Exception:
                pass

            h_rating = 0
            try:
                h_rating = int(r.get("heart_rating") or 0)
            except Exception:
                pass

            voices.append({
                "ses_id": str(r.get("ses_id") or "").zfill(4) if r.get("ses_id") else "",
                "id": r.get("id"),
                "display_name": r.get("display_name"),
                "turkish_title": r.get("turkish_title"),
                "yas": r.get("yas") or "Genç",
                "cinsiyet": r.get("cinsiyet") or ("Kadın" if str(r.get("gender")).lower() == "female" else "Erkek"),
                "unvan": r.get("unvan") or r.get("turkish_title"),
                "category": r.get("custom_category") or r.get("category") or "İslami Yayın & Tefekkür",
                "api_voice_name": r.get("api_voice_name"),
                "pitch_hz": r.get("pitch_hz"),
                "pitch_ratio": r.get("pitch_ratio") or 1.0,
                "is_favorite": is_fav,
                "heart_rating": h_rating,
                "duration_sec": dur,
                "updated_at": r.get("updated_at"),
                "timbre": r.get("timbre"),
                "emotion_tone": r.get("emotion_tone"),
                "has_sample": bool(r.get("has_sample", True)),
            })
        return voices

    def get_voice(self, identifier: str) -> Optional[dict]:
        """
        ses_id ('0001', '0051', '1'), id ('dervis', 'deneme_37'), 
        display_name ('derviş', 'vip_fısıltılı', '10kalp') veya category ile arar.
        """
        if not identifier:
            return None
        clean = str(identifier).strip()
        padded = clean.zfill(4) if clean.isdigit() else clean

        sql = """
            SELECT * FROM voices 
            WHERE ses_id = ? OR id = ? OR display_name = ? OR category = ? OR custom_category = ?
            LIMIT 1
        """
        rows = self.execute(sql, [padded, clean, clean, clean, clean])
        if rows:
            return rows[0]
        # Eğer bulunamazsa gevşek arama
        sql_like = "SELECT * FROM voices WHERE display_name LIKE ? OR turkish_title LIKE ? LIMIT 1"
        rows_like = self.execute(sql_like, [f"%{clean}%", f"%{clean}%"])
        if rows_like:
            return rows_like[0]
        return None

    def toggle_favorite(self, identifier: str) -> bool:
        """Sesin favori durumunu tersine çevirir."""
        voice = self.get_voice(identifier)
        if not voice:
            return False
        current = voice.get("is_favorite")
        new_val = 0 if current in (1, "1", True) else 1
        sql = "UPDATE voices SET is_favorite = ? WHERE id = ?"
        if self.has_local_db():
            self._execute_local(sql, (new_val, voice["id"]))
        try:
            self._query_cloud(sql, [new_val, voice["id"]])
        except Exception:
            pass
        return bool(new_val == 1)

    def get_sample_audio(self, identifier: str) -> Tuple[Optional[bytes], Optional[str]]:
        """Önizleme sesini doğrudan yerel DB'den veya buluttan çözüp bytes döndürür."""
        voice = self.get_voice(identifier)
        if not voice or not voice.get("audio_base64"):
            return None, None

        b64_str = voice["audio_base64"]
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]

        raw_bytes = base64.b64decode(b64_str)
        mime = voice.get("audio_mime_type") or "audio/wav"
        return raw_bytes, mime


if __name__ == "__main__":
    client = TursoVoiceClient()
    print(f"Yerel Veritabanı Aktif mi?: {client.has_local_db()}")
    voices = client.list_voices()
    print(f"Toplam Ses: {len(voices)}")
    v001 = client.get_voice("0001")
    if v001:
        print(f"0001 Sesi: {v001.get('display_name')} ({v001.get('api_voice_name')}) - {v001.get('pitch_hz')} Hz")
    v_fisilti = client.get_voice("vip_fısıltılı")
    if v_fisilti:
        print(f"vip_fısıltılı Sesi: #{v_fisilti.get('ses_id')} - {v_fisilti.get('turkish_title')}")
