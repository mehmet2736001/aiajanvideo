# 🏛️ Nexus AI Video Studio — 16 Ajanlı Otonom Video Hükümeti 🎬

> **Sıfır Yapay Zeka Görsel Halüsinasyonu · %100 Kod Tabanlı Remotion (React + SVG) · 30 FPS Full HD (1080x1920) Dikey Video Motoru**  
> Kendini denetleyen, tarafsız eleştiren, arayüzünü sadeleştiren ve her videoda öğrenen dünyanın ilk 16 ajanlı video stüdyosu.

---

## 🌟 Çekirdek Felsefe

* **Görüntü Tamamen Kod:** Midjourney, Kling veya durağan slayt gösterileri yok. Bütün karakterler, membranlar, ışıklar ve geçişler matematiksel SVG ve Bezier fizik eğrileriyle kodlanır.
* **Yapay Zeka Yalnızca Seste:** Edge-TTS (`tr-TR-AhmetNeural`) + Stüdyo Mastering + `faster-whisper` milisaniyelik kelime senkronu (`kelimeler.json`).
* **Kinetik Tipografi:** Konuşulan her kelime anında altın sarısıyla parıldar, satır zıplamaz.
* **Bağımsız Çift Denetim:** 48 karelik pano (`pano.jpg`) hem Başdenetçi Hasan hem de veto yetkisine sahip Müfettiş Nuri tarafından incelenir.

---

## 🏛️ 16 Ajanlı Hükümet Kadrosu (4x4 Matris)

### I. Strateji ve Hikmet Katmanı
1. **`01_basyonetmen` – Selim Bey:** Orkestra Şefi ve Ajan Hükümeti Başkanı.
2. **`03_islami_kurgu` – Müderris Âkif:** Kur'an, Sünnet ve Hanefi Fıkhı edep sınırları denetçisi.
3. **`04_metin_tefekkur` – Senarist Yahya:** 70-100 kelimelik, acele etmeyen kancalı konuşma metni yazarı.
4. **`15_viral_strateji` – Stratejist Kaya:** İlk 3 saniye kancasını ve izleyici tutundurma (retention) eğrilerini denetleyen algoritma uzmanı.

### II. Görsel ve Ses Üretim Katmanı
5. **`05_sahne_storyboard` – Yönetmen Zeynep:** Saniye saniye SVG nesne ve kamera süzülüş planı.
6. **`06_materyal_toplama` – Arşivci Tarık:** Hat levhaları, 24K altın ve obsidyen renk kodları arşivi.
7. **`07_gorsel_motion_uretim` – Stüdyo Şefi Emre:** Parametrik SVG Rig kütüphanesi yöneticisi.
8. **`08_ses_frekans` – Ses Mühendisi Bora:** Stüdyo EQ, compand, loudnorm (-16 LUFS) ve kelime zamanlaması.
9. **`09_video_edit_render` – Kurgu Ustası Kerem:** 30 FPS Full HD (1080x1920) Remotion render motoru şefi.

### III. Bağımsız Denetim ve Yargı Katmanı
10. **`10_islami_video_analiz` – Başdenetçi Hasan:** 48 karelik panoyu (`pano.jpg`) kare kare denetleyen Vision uzmanı.
11. **`13_tarafsiz_denetci` – Müfettiş Nuri:** Şeytanın Avukatı; grup içi körlüğü engelleyen, zayıf işleri veto etme yetkisine sahip bağımsız hakem.
12. **`12_kapak_ve_yayin_seo` – Editör Bilal:** Kapak görseli (Thumbnail), viral başlık ve YouTube SEO uzmanı.
13. **`02_yonetmen` – Sinan Bey:** Üretim ajanlarının ara teslimat koordinatörü.

### IV. Evrim, Sadelik ve Sistem Sağlığı Katmanı
14. **`11_yetenek_gelistirme` – Muallim Farabi:** Analiz raporlarını okuyup `SKILL.md` ve hafıza dosyalarını güncelleyen meta-öğrenme şefi.
15. **`14_zen_arayuz` – Mimar Sinan:** Arayüzü tek tıkla çalışacak Apple/Dieter Rams sadeliğinde tutan UI/UX mimarı.
16. **`16_sistem_temizlik` – Mühendis Demir:** Render sonrası ara wav ve temp dosyalarını süpüren, render hızını koruyan sistem mühendisi.

---

## 🚀 Nasıl Çalıştırılır?

### 1. Tek Tıkla Konsol Menüsü
Klasördeki **`BASLAT.bat`** dosyasına çift tıkla:
* `[1]` Web Stüdyo Panelini Başlat (`http://localhost:8000`)
* `[2]` Remotion Canlı Önizleme Player'ı Başlat (`http://localhost:3000`)
* `[3]` Hızlı Otonom Video Üret (Terminalden 16 ajanla)
* `[4]` Sistem Sağlık Denetimi ve Çöp Temizliği (Mühendis Demir)

### 2. Doğrudan Web Arayüzü
```bash
python -m web_ui.server
```
Tarayıcında `http://localhost:8000` adresini aç.

### 3. Doğrudan Otonom Terminal Motoru
```bash
python engine/orchestrator.py
```

---

## 📁 Proje Klasör Mimarisi

```
e:\aivideoyap/
├── 🏛️ agents/               # 16 Ajanın SKILL.md ve memory.json dosyaları
├── 🧠 brain/                # Merkezi hafıza (experience_memory.json & video_history.json)
├── ⚙️ engine/               # Python seslendirme, render, denetim ve temizlik motoru
├── 🌐 web_ui/               # Tailwind + FastAPI modern stüdyo kontrol paneli
├── 📦 production_output/    # Üretilen her videonun klasörü (video.mp4 + pano.jpg)
├── 🎬 src/                  # Remotion TypeScript & SVG bileşenleri
├── 📁 public/               # Fontlar, seslendirmeler ve kelimeler.json
└── 🚀 BASLAT.bat            # Tek tıkla kontrol merkezi
```
