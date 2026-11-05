import os
import sys
import json
import base64
import urllib.request
import urllib.error

# Windows encoding safety
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CREDS_FILE = os.path.join(BASE_DIR, "turso_credentials.json")

# Default credentials extracted from environment / config
DEFAULT_CONFIG = {
    "org_slug": "zakirun002",
    "db_name": "aisesler",
    "db_url": "https://aisesler-zakirun002.aws-eu-west-1.turso.io/v2/pipeline",
    "api_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJicFZKZWMtR0VmR25QQ0x4WGlLNERRIiwib3JnX2lkIjoxMDAwMjgyNTIyfQ.Z5NwQkwV64bk_ca4PIMkWNLmR230tDbRvxBDc4w2YoPxPpcOQDzdzgbzWS2pKckHMASDEnbzqmrnFRS_CXw0Dg",
    "jwt_token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTM5MDU4OTYsImlkIjoiMDFhMWE4MjEtZWMwMS03N2QzLTkxZGMtOGMwMzRlOWQ1MTM2Iiwia2lkIjoidUd6SUVaT0Y4cnhTWW9aUENJcVFqWkNleExuaFNrTE9PSVVWNXVISkE1VSIsInJpZCI6Ijc3ZjgyZThjLTQ1MGItNGNhMC1hMjM5LTNiNWVkNzdlNDczNCJ9.NQJY50ZoL03UZkPoXG_zKHjCTsXt99-ENrPL6OW6RuW_ZOtLd-f4-EP6aCOcs4_4zPIT3FyJxrCzzCrIo4qxCA"
}

class TursoVoiceClient:
    """
    Canlı Turso Cloud (aisesler-zakirun002) veritabanı istemcisi.
    Sesleri listeler, favori durumunu günceller ve örnek sesleri çeker.
    """

    def __init__(self):
        self.load_creds()

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

    def execute(self, sql: str, args: list = None) -> list:
        """Turso pipeline endpoint'ine tek bir SQL ifadesi gönderir."""
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
                    # Token yenile ve tekrar dene
                    self.refresh_jwt_token()
                    continue
                raise e
        return []

    def list_voices(self) -> list:
        """
        Turso Cloud'dan tüm ses profillerini çeker.
        Favoriler en başta, sonra en son güncellenenler.
        """
        sql = """
            SELECT id, display_name, turkish_title, api_voice_name, gender, 
                   category, pitch_hz, is_favorite, audio_duration, updated_at, timbre, emotion_tone
            FROM voices 
            ORDER BY is_favorite DESC, rowid DESC
        """
        rows = self.execute(sql)
        voices = []
        for r in rows:
            is_fav = bool(r.get("is_favorite") in (1, "1", True))
            dur = None
            try:
                if r.get("audio_duration"):
                    dur = round(float(r["audio_duration"]), 1)
            except Exception:
                pass

            voices.append({
                "id": r.get("id"),
                "display_name": r.get("display_name"),
                "turkish_title": r.get("turkish_title"),
                "api_voice_name": r.get("api_voice_name"),
                "gender": r.get("gender"),
                "category": r.get("category"),
                "pitch_hz": r.get("pitch_hz"),
                "is_favorite": is_fav,
                "duration_sec": dur,
                "updated_at": r.get("updated_at"),
                "timbre": r.get("timbre"),
                "emotion_tone": r.get("emotion_tone")
            })
        return voices

    def get_voice(self, voice_id: str) -> dict:
        """Belirli bir sesin tüm detaylarını çeker."""
        sql = "SELECT * FROM voices WHERE id = ? OR display_name = ? LIMIT 1"
        rows = self.execute(sql, [voice_id, voice_id])
        if not rows:
            return None
        return rows[0]

    def toggle_favorite(self, voice_id: str) -> bool:
        """Sesin favori durumunu tersine çevirir (1 -> 0 veya 0 -> 1) ve Turso'ya kaydeder."""
        sql_check = "SELECT is_favorite FROM voices WHERE id = ? LIMIT 1"
        rows = self.execute(sql_check, [voice_id])
        if not rows:
            return False

        current = rows[0].get("is_favorite")
        new_val = 0 if current in (1, "1", True) else 1

        sql_update = "UPDATE voices SET is_favorite = ? WHERE id = ?"
        self.execute(sql_update, [new_val, voice_id])
        return bool(new_val == 1)

    def get_sample_audio(self, voice_id: str):
        """Önizleme sesini base64'ten çözüp bytes olarak döndürür."""
        sql = "SELECT audio_base64, audio_mime_type FROM voices WHERE id = ? LIMIT 1"
        rows = self.execute(sql, [voice_id])
        if not rows or not rows[0].get("audio_base64"):
            return None, None

        b64_str = rows[0]["audio_base64"]
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]

        raw_bytes = base64.b64decode(b64_str)
        mime = rows[0].get("audio_mime_type") or "audio/wav"
        return raw_bytes, mime

if __name__ == "__main__":
    client = TursoVoiceClient()
    v_list = client.list_voices()
    print(f"Turso Canlı Ses Sayısı: {len(v_list)}")
    print(f"Favoriler: {[v['id'] for v in v_list if v['is_favorite']]}")
