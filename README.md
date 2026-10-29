# Notebook Video AI (Defter Notu Shorts / Reel Video Oluşturucu) 🎬📖

Yapay zekâ destekli, **"Spiral Not Defteri / Explain-Like-I'm-5"** estetiğinde dikey (1080x1920) YouTube Shorts, Instagram Reels ve TikTok videoları üreten tam otomatik video oluşturucu.

---

## 🚀 Özellikler

- 📓 **Otantik Defter Estetiği:** Üstten telli spiral delikler, sol kırmızı kenar çizgisi, kareli defter kağıdı ve hafif kağıt dokusu.
- ✍️ **El Yazısı & Vurgular:** Kalam / Caveat el yazısı fontları, animasyonlu kırmızı daire çizimi, fosforlu sarı kalem (*highlighter*) vurgusu.
- 🗂️ **Kartlar ve Vektör İkonlar:** Yuvarlak hatlı renkli bilgi kutucukları, yay animasyonları (*spring*), elle çizilmiş SVG ikonlar (galaksi, hücre bölünmesi, kitap, ampul, fidan vb.).
- ⏳ **Zaman Çizelgesi & Alıntı Kartı:** Yıllara göre çizilen cetvel aksı, ayet/hadis Arapça kaligrafisi ve yapışkan sarı post-it notu.
- 🎙️ **Ses & Dinamik Altyazı:** Konuşmayla eşzamanlı kelime kelime yanan yuvarlak köşeli altyazı kutusu.
- ⚡ **Yüksek Hızlı Render:** React ve Remotion motoru sayesinde saniyeler içinde 1080x1920 Full HD MP4 çıktısı.

---

## 🛠️ Kurulum ve Kullanım

### 1. Canlı Önizleme (Web Studio)
Videoyu tarayıcında açıp kare kare oynatmak, metinleri canlı değiştirmek için:
```bash
cd C:\Users\xd\.gemini\antigravity\scratch\notebook-video-ai
npm run start
```
Tarayıcında `http://localhost:3000` açılacak ve Remotion Player üzerinden videoyu gerçek zamanlı inceleyebileceksin.

---

### 2. Yapay Zekâ ile Yeni Bir Konu Üretme
Python pipeline scriptini çalıştırarak dilediğin konuda senaryo, seslendirme ve altyazıyı saniyeler içinde oluşturabilirsin:

```bash
# İbn-i Sina Konusu İçin:
python scripts/ai_pipeline.py --topic ibnisina

# Evren Neden 6 Günde Yaratıldı Konusu İçin:
python scripts/ai_pipeline.py --topic kainat
```

Bu komut:
1. Senaryoyu ve sahne şemasını hazırlar.
2. `public/audio.mp3` ses dosyasını üretir.
3. Kelime seviyesinde zaman damgalarını (`subtitles`) hesaplar.
4. `src/generatedData.json` dosyasına kaydeder.

---

### 3. MP4 Olarak Render Alma
```bash
npm run build
```
Oluşan video `out/video.mp4` konumuna kaydedilir.

---

## 📁 Proje Yapısı

```
notebook-video-ai/
├── src/
│   ├── components/
│   │   ├── NotebookBackground.tsx  # Spiral teller ve kareli zemin
│   │   ├── HanddrawnHeader.tsx     # Daire ve fosforlu sarı vurgulu başlık
│   │   ├── CardGrid.tsx            # Yay animasyonlu 3'lü bilgi kartı
│   │   ├── TimelineView.tsx        # Çizgisel zaman tüneli ve alıntı kartı
│   │   ├── SubtitlesBar.tsx        # Sesle senkron kinetik altyazı
│   │   └── Icons.tsx               # Elle çizilmiş minimalist SVG'ler
│   ├── NotebookVideo.tsx           # Ana sahne bileşeni
│   ├── Root.tsx                    # Remotion kompozisyon kökü
│   ├── sampleData.ts               # Örnek veri şablonu
│   └── types.ts                    # TypeScript veri modelleri
├── scripts/
│   └── ai_pipeline.py              # TTS, altyazı ve şema üreten Python motoru
├── public/                         # Üretilen ses ve statik varlıklar
└── out/                            # Render edilen test kareleri ve video.mp4
```
