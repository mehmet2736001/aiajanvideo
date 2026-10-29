# 🎬 Zaman Tüneli Geliştirme Planı (Timeline Engine 2.0)
## Video, Medya & Ses Bölme, Kırpma, Silme ve Profesyonel Kurgu Mimarisi

CapCut, VN Editor ve Adobe Premiere Pro gibi modern video düzenleme yazılımlarının zaman tüneli mantığını uygulamamıza entegre ederek **Video**, **Medya (B-Roll / Görsel)** ve **Ses (Konuşma + Müzik + SFX)** katmanlarını bağımsız olarak **bölünebilir (split)**, **silinebilir (delete)**, **kırpılabilir (trim)** ve **manyetik kaydırılabilir (ripple)** hale getirme planıdır.

---

### 📌 Faz 1: Çoklu Ses Klipleri (Multi-Clip Audio) & Sesi Bölme/Silme Motoru
- FFmpeg tabanlı ses bölme (`split_audio_clip`): İğnenin bulunduğu veya tıklanan saniyeden bağımsız iki ses klibi oluşturma.
- Ses klibi silme (Delete audio clip) ve aradaki boşluğu kapatma (Ripple).
- Ses klibi kırpma tutamaçları (Audio Trim Handles).
- Bağımsız ses seviyesi (%0 - %150) ve Mute butonu.

### 📌 Faz 2: Jilet Aracı (Razor Tool 'C') & Video Klipleri Bölme/Silme
- Jilet / Makas Modu (`C` tuşu): Klip üzerinde tıklanan saniyeden anında kesme.
- İğneden Bölme (`S` veya `Ctrl+B`).
- Klip Silme & Boşluksuz Kapatma (`Delete` / `Backspace` - Ripple Delete).
- Sahne Çoğaltma (`Ctrl+D`).

### 📌 Faz 3: Medya & B-Roll Katmanı (Overlay / PiP Video Track)
- Video katmanının altında bağımsız 2. bir medya izi (`track-broll`).
- `public/broll/*.mp4` video döngüleri ve görsellerin zaman tüneline blok olarak eklenmesi, uzatılması, bölünmesi ve silinmesi.

### 📌 Faz 4: Profesyonel Araç Çubuğu, Kısayol Tuşları & Geri Al (Undo/Redo)
- Araç çubuğu: `[V Seç]` `[C Jilet]` `[S Böl]` `[Del Sil]` `[Ctrl+Z Geri Al]`.
- Klavye kısayolları: `Space` (oynat/durdur), `C` (jilet), `V` (seçim), `Delete` (silme), `Ctrl+Z` (geri al), `Ctrl+Y` (ileri al).
