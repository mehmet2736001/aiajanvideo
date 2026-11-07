# Nexus AI Video Studio

Türkçe, dikey (1080×1920, 30 FPS) tefekkür/kısa video üretim hattı.
Görüntü **tamamen kodla** (Remotion + SVG) çizilir; yapay zeka yalnızca metin sohbetinde (Gemini) ve seslendirmede (edge-tts) kullanılır.

## Nasıl çalışır?

```
Senaryo satırları ─► edge-tts seslendirme ─► faster-whisper kelime zamanları
                  ─► FFmpeg mastering (EQ + compand + -16 LUFS) ─► ses.mp3 + kelimeler.json
                  ─► Remotion render ─► 48 karelik pano + kalite denetimi ─► out/<slug>/<slug>.mp4
```

* **Yeni bir slug** için video, veri güdümlü genel şablonla (`TefekkurVideo`, `src/templates/`) otomatik üretilir.
* `src/<slug>/index.ts` varsa (`hud-112`, `olum-son-mu` gibi elle tasarlanmış videolar) o kompozisyon render edilir.
* Başka bir projenin videosuna asla sessizce geri dönülmez; bulunamazsa hata verilir.

## Gereksinimler

| Araç | Not |
|---|---|
| Python 3.10+ | `pip install -r requirements.txt` |
| Node.js 18+ | `npm install` |
| FFmpeg + ffprobe | PATH'te olmalı |
| Gemini API anahtarı | Başyönetmen sohbeti için; `api_keys.json` veya `GEMINI_API_KEYS` |

İlk `faster-whisper` çalıştırmasında "base" modeli indirilir (internet gerekir).

## Kurulum ve çalıştırma

```bash
pip install -r requirements.txt
npm install
cp api_keys.example.json api_keys.json   # anahtarlarınızı yazın (git'e girmez)

python -m web.server                      # http://127.0.0.1:8000
npm start                                 # Remotion önizleme: http://localhost:3000
```

Windows'ta `BASLAT.bat` aynı işlemler için menü sunar.

Sağlık kontrolü: `GET /api/health` (ffmpeg, node, node_modules, anahtar sayısı).

## Yapılandırma

* `api_keys.json`: `{"keys": [...], "models": [...]}`; ya da `GEMINI_API_KEYS` / `GEMINI_MODELS` ortam değişkenleri (bkz. `.env.example`).
* Model zinciri soldan sağa denenir. 429'da sıradaki anahtara, 404'te sıradaki modele geçilir.
* Turso ses kütüphanesi `core/turso_client.py` içinde ayarlanır (`turso_credentials.json` ile geçersiz kılınabilir).

## API özeti

| Uç nokta | Açıklama |
|---|---|
| `POST /api/produce` | `{project_slug, title, lines[]}` — üretimi çalıştırır, bitince sonucu döner (aynı anda tek üretim, aksi halde 409) |
| `GET /api/production/status` | Canlı ilerleme (adım, yüzde, kalan süre, log) |
| `POST /api/chat/message` | Başyönetmen ile sohbet |
| `GET /api/audio_library` | Turso ses listesi |
| `GET/POST /api/errors…` | Sunucu hata günlüğü |

`project_slug` yalnızca `[a-z0-9_-]` (en çok 64 karakter) olabilir.

## Bilinen sınırlar

* edge-tts'te Türkçe için yalnızca iki ses vardır (Ahmet / Emel). Turso kaydı yalnızca cinsiyet seçimini etkiler.
* Kalite denetimi, panodaki karelerin boşluk/kontrast/hareket sinyallerini ölçen bir sezgiseldir; görsel estetiği yargılamaz.
* Gemini model adları `api_keys.json` içinden ayarlanır; geçersiz (404) modeller oturum boyunca atlanır.
* Arayüz (`web/index.html`) Tailwind CDN'i ve unpkg üzerinden betik yükler; internet gerekir.

## Geliştirme

```bash
pip install -r requirements-dev.txt
python -m pytest -q        # Python testleri
npm run typecheck          # TypeScript tip denetimi
```

CI (`.github/workflows/ci.yml`) bu iki denetimi her push'ta çalıştırır.

## Klasörler

```
core/        üretim hattı (orchestrator, ses, denetim, Gemini sohbeti, Turso)
web/         FastAPI sunucusu + arayüz
src/         Remotion kompozisyonları (templates/, hud-112/, olum-son-mu/, components/)
brain/       ajan tanımları (agents/), hafıza ve üretim geçmişi
public/      ses, kelime zamanları, SFX, görseller (Remotion staticFile)
out/         üretilen videolar (git'e girmez)
tests/       pytest testleri
```

`brain/agents/*` içindeki SKILL/memory dosyaları belge niteliğindedir; kod yalnızca `memory.json` dosyalarını arayüzde listeler.
