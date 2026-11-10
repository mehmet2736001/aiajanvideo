---
name: 3d-karakter-animasyon
description: Beyaz clay (vinyl) çubuk-insan karakterle, 12 sahnelik / 60 sn'lik, sesli ve altyazılı "3D görünümlü" ibretlik animasyon videosu üretir. Blender, yapay zekâ video modeli veya internet gerektirmez; sadece Python (numpy, OpenCV, PIL, scipy) ve ffmpeg kullanır. Yeni senaryo, yeni sahne veya sahne düzeltme istendiğinde kullan.
---

# 3D Karakter Animasyon (Python + OpenCV + ffmpeg)

Bu beceri, "Güneş Doğmadığında" videosunun nasıl yapıldığını adım adım anlatır. Aynı yöntemle başka senaryolar (farklı ibretlik hikâyeler, ayet/hadis temalı kısa filmler, bilgi videoları) üretilebilir.

> **Önemli dürüstlük notu:** Çıktı gerçek 3D render değil. Karakter, normal haritası taklit eden gölgelendirme ile "clay / vinyl 3D" gibi görünen 2D çizimdir. Veo/Kling/Runway gibi bir video modeli yerine, ortamda hiçbir şey indirmeden çalışır. Kullanıcıya bunu baştan söyle.

---

## 0. Klasör yapısı

```
animasyon skills/
└── 3d-karakter-animasyon/
    ├── SKILL.md                  ← bu dosya
    ├── kod/
    │   ├── engine.py             ← karakter, ışık, yüz, IK, kamera, altyazı, post-process
    │   ├── scenes.py             ← 12 sahne + senaryo altyazıları (SCENES, CAPS)
    │   ├── audio.py              ← ses sentezi (numpy) → out/audio.wav
    │   ├── render.py             ← sahne başına mp4 render
    │   └── test.py               ← seçilen karelerden kontak sheet (PNG)
    └── demo/
        ├── demo_gunes_dogmadiginda.mp4   ← bitmiş örnek video (60 sn)
        └── karakter_referans.jpg         ← karakter referans görseli
```

Yeni bir şablon eklenecekse **yeni bir klasör** aç (ör. `animasyon skills/ayet-videosu/`); mevcut klasörlere dokunma. Her yeni şablonla birlikte `demo/` içine örnek bir mp4 koy.

---

## 1. Ortam gerçekleri (ilk önce kontrol et)

- Blender yok, internet/pip kapalı olabilir. Kontrol: `which ffmpeg; python3 -c "import cv2, numpy, PIL, scipy"`.
- Türkçe TTS (espeak vb.) yok → **dış ses üretilemez**, metinler altyazı olarak basılır. Kullanıcıya dış sesi kendisinin ekleyeceğini söyle.
- CPU az (2 çekirdek) → sahneleri 2 süreçte paralel render et.
- Font: `/usr/share/fonts/opentype/inter/Inter-Bold.otf` ve `Inter-SemiBold.otf` (Türkçe ş, ğ, İ, ı destekler). DejaVu yedek.
- Hız: sahneye göre kare başı ~0.1–1.0 sn. 1800 kare (60 sn @30fps) iki süreçle birkaç dakika sürer.
- Geçici dosyaları scratchpad dizininde tut; çıktıları kullanıcıya `SendUserFile` ile gönder.

---

## 2. Genel akış (adım adım)

1. **Senaryoyu sahnelere böl.** Her sahne için: görsel plan, dış ses metni (altyazı olur), ses/atmosfer notu. Standart: 12 sahne × 5 sn = 60 sn.
2. **Karakteri kur** (`engine.py`): referans görsele benzeyen beyaz clay karakter. Bkz. bölüm 3.
3. **Test et:** önce tek karakteri farklı pozlarda çiz (ayakta, diz çökmüş, secde, yüz ifadeleri). Gözle kontrol et.
4. **Sahneleri yaz** (`scenes.py`): her sahne `sceneN(t)` fonksiyonu, `t` saniye (0–5), uint8 RGB (720×1280×3) döndürür. Bkz. bölüm 5.
5. **Kontak sheet ile kontrol et:** `python3 test.py 1,2 0.5,2.0,4.8 sheet.png` (sahne listesi, zaman listesi, çıktı). Kareleri `Read` ile aç, düzelt. **Tam render'dan önce mutlaka birkaç kare bak.**
6. **Sesi üret** (`audio.py`) → `out/audio.wav` (60 sn, stereo, 44.1 kHz).
7. **Sahneleri render et** (`render.py`): her sahne ayrı mp4. İki süreç paralel:
   ```bash
   python3 render.py 1 3 5 7 9 11 &
   python3 render.py 2 4 6 8 10 12 &
   ```
8. **Birleştir:** concat demuxer + `-c copy`, sonra ses ekle `-c:v copy`:
   ```bash
   cd out
   for i in 01 02 03 04 05 06 07 08 09 10 11 12; do echo "file 's$i.mp4'"; done > list.txt
   ffmpeg -y -f concat -safe 0 -i list.txt -c copy video_only.tmp.mp4
   ffmpeg -y -i video_only.tmp.mp4 -i audio.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest final.tmp.mp4
   mv final.tmp.mp4 video.mp4
   ```
9. **Doğrula:** `ffprobe` ile süre (60.0 sn), çözünürlük, codec; 5–6 kareyi `ffmpeg -ss` ile çıkarıp bak.
10. **Teslim et:** mp4'ü gönder, kullanıcıya kısa özet + dürüst notlar (3D değil, dış ses yok, ses sentez).

Kurallar (video-making becerisinden): sahne başına tek kodlanmış dosya, hepsi aynı boyut/fps/encoder; geçici ad `.tmp.mp4`, ffmpeg 0 dönünce `rename`; piksel boru hattı `rawvideo` ile ffmpeg'e pipe; `libx264 -crf 18 -preset veryfast -pix_fmt yuv420p`; 30 fps.

---

## 3. Karakter motoru (`engine.py`)

### 3.1 Görünüm (referans görsele göre)
Beyaz, mat clay; büyük yuvarlak kafa (yarıçap 60 birim), iri parlak siyah gözler (içinde küçük beyaz yansıma), göz çevresinde ince gri halka, ince gri kaşlar, burun/kulak/saç yok, açık ağız içi soluk pembe, ince uzuvlar, eldiven gibi eller (bir başparmak çıkıntısı).

### 3.2 Gölgelendirme (3D hissinin sırrı)
- **Kafa:** analitik küre. Her piksel için normal `(x, y, sqrt(1-r²))`.
- **Gövde/uzuvlar:** maske çizilir (kapsül = kalın çizgi + uçlarda daire) → Gauss bulanıklaştırma ile "yükseklik haritası" → Sobel ile gradyan → normal `(-gx*c, -gy*c, 1)`, `c = 3.2*sigma`. Aynı aydınlatma fonksiyonu (`lit`) uygulanır.
- **Aydınlatma sözlüğü** `mk_lt(amb, key, dir, rim, rimdir)`: ortam rengi, ana ışık rengi/yönü, kenar (rim) ışığı rengi/yönü. Renk = `BASE * (amb + key*lambert) + rim`.
- Yüz çizgileri (kaş, halka) sahne parlaklığına göre koyulaştırılır ki karanlıkta kaş cildin üstünde "parlamasın".
- **Dersler:** karanlık sahnelerde `amb` ve `key` rengini mavi/kırmızıya fazla kaydırma (karakter mavi/turuncu boyanmış gibi olur). Ortamı nötre yakın tut, renk vurgusunu `rim` ile ver.

### 3.3 Poz sistemi
Poz bir sözlük (`DEF` varsayılanları). Anahtarlar:

| anahtar | anlam |
|---|---|
| `x, y, s` | pelvis konumu (piksel), ölçek |
| `dy` | zemin üstü pelvis yüksekliği (birim). Ayakta 158, diz çökmüş 36, secde 93. `y = G - dy*s` |
| `mir` | 1 = sağa bakar, -1 = sola bakar (tüm açılar ve yüz aynalanır) |
| `ta` | gövde eğimi (derece, dikey 0; yatarken -90) |
| `ha` | kafa eğimi (gövdeye göre) |
| `fr` | sadece yüzü döndürür (kafa konumunu değiştirmeden; yatarken/secdede yüzü kameraya çevirmek için) |
| `la1 la2 ra1 ra2` | sol/sağ bacak: üst/alt kemik açıları (aşağıdan başlayarak, derece) |
| `al1 al2 ar1 ar2` | sol/sağ kol açıları (180 = yukarı) |
| `fd` | ayak yönü (+1 ön, -1 arka, 0 karşıdan) |
| `yaw` | kafa dönüşü (profil için 1) |
| `open` | göz açıklığı (0 = kapalı, >1 = fal taşı gibi) |
| `brow` | kaş (−1 kızgın … +1 endişeli) |
| `m` | ağız gülümseme (−1 üzgün … +1 gülen) |
| `mo` | ağız açıklığı (0–1) |
| `lx, ly` | gözbebeği bakış yönü |
| `fy` | yüz öğelerini dikey kaydır (−0.2 = yukarı bakıyor) |
| `tear` | gözyaşı ilerlemesi 0–1 |
| `hs` | kafa ölçeği |
| `af` | 1 = kolları kafanın önünde çiz (eller ağza/gözlere giderken) |

Zaman çizelgesi: `anim(t, spec, base)` / `pz(t, spec, G=..., **base)`; `spec = {anahtar: [(zaman, değer), ...]}`. Her parça `smoothstep` ile yumuşar; ilk anahtardan önce/son anahtardan sonra sabit kalır. Parça sayısı az, okunaklı kal.

### 3.4 IK (kolu hedefe uzat)
`reach(p, 'L'|'R', hedef_xy, bend)` kolun açılarını ayarlar (`engine.ik`).
- Dirsek **aşağıda** olsun istiyorsan: hedef sağdaysa `bend=+1`, soldaysa `bend=-1`.
- Elin kafa/yüz hizasında dikey uzanması: sol kol `-1`, sağ kol `+1` (dirsek dışa).
- Hedef kol uzunluğundan uzaksa otomatik kısaltılır.
- IK, poz (özellikle `x, y, ta, s`) belirlendikten **sonra** çağrılmalı.

### 3.5 Kamera, altyazı, post
- `camera(canvas, z, cx, cy, shake, t)`: yakınlaştırma + kaydırma; **kenar yansıması (BORDER_REFLECT) hatasını önlemek için merkez otomatik sınırlandırılır.** Yüksek tuval (örn. 1280×1100) ile "yukarı tilt" yapılır (`cy` zamanla azalır).
- `caption(frame, metin, alpha)`: alt ortada yarı saydam yuvarlatılmış kutu, otomatik satır kaydırma, Inter SemiBold 33 px.
- `post(frame, vig, grain, fade)`: vinyet + hafif film grain + fade (son sahnede siyaha).
- `text(frame, s, xy, size, color)`: PIL ile metin (saat rakamları, etiketler).

---

## 4. Ses tasarımı (`audio.py`)

Hepsi numpy ile sentezlenir, sonunda hafif yankı (4 gecikme) ve normalizasyon (-1.4 dB civarı) yapılır. Bileşenler:

| sahne | ses |
|---|---|
| tümü (0–49.5 sn) | alçak drone (55 + 82.4 + 110 Hz), zamanla güçlenir |
| S1 | 3 alarm bip'i (880 Hz), kalp atışı (66 bpm, iki vuruşlu), yutkunma (bant geçiren gürültü) |
| S2 | perde hışırtısı (1.2–5 kHz gürültü), düşük rüzgâr (lowpass gürültü) |
| S3 | kalabalık uğultusu (300–1400 Hz modüleli gürültü), ayak sesleri |
| S4 | hızlı kalp (112 bpm), nefes (500–3000 Hz) |
| S5 | siren (850/1200 Hz kare geçişli), panik uğultusu, elektronik cızırtı |
| S6 | ney benzeri ton (392 Hz + vibrato + nefes gürültüsü), boğuk atmosfer |
| S7 | 30. saniyede sub-bass düşüşü, rüzgâr yükselişi, pad |
| S8–S10 | gerilim yayları (Dm tonu), keman benzeri pad, tepe noktası, 49.6–50.0 arası **ani sessizlik** |
| S11 | ani nefes, kalp, 34 kuş cıvıltısı (3–4.8 kHz chirp), C majör aydınlık pad |
| S12 | hicaz hissi veren yavaş ney cümlesi, son 1.2 sn fade-out |

Ayrıca: metinde "ezan tınısı" istenirse gerçek ezan yerine **yalnızca melodik ney tınısı** kullanıldı (kutsal metin/ezan sentezlenmedi). Gerçek ses/müzik isteniyorsa kullanıcı CapCut/DaVinci'de değiştirir.

---

## 5. Sahne tarifleri (`scenes.py`)

Genel desen:
1. Arka planı **bir kez** üret ve `cached(key, fn)` ile sakla; her karede `.copy()` kullan.
2. Dinamik parlamalar için `glow(img, cx, cy, r, renk, k)` (toplamalı ışık).
3. Karakterleri `draw_char(img, p, lt, ground=G, shadow=...)` ile çiz (arkadan öne doğru **G değerine göre sırala**).
4. Sahne sonunda `camera(...)` ile kamera hareketi (yakınlaşma/kaydırma/titreme).

| # | sahne | teknik özet |
|---|---|---|
| 1 | Yatakta uyanış 08:15 | karanlık oda, yatak/komodin/pencere arka planı; karakter `ta=-90` yatar → 1.5–2.4 sn'de oturur; battaniye karakterin **üstüne** çizilir; saat kırmızı glow + `text('08:15')`; başlık ilk 3 sn |
| 2 | Perde | karakter yakın plan (`s=1.9`); sağ kol IK ile perde kenarına uzanır; perde iki panel (sol/sağ) kayarak şehir silüetini (`city_view`) açar |
| 3 | Sokak | `street_bg()` (lambalar, binalar, sis); 12 karakterlik kalabalık, hepsi `fy=-0.2, ly=-1` ile göğe bakar; ana karakter yürüyerek girer (`walk_legs`); yavaş dolly (`z` 1.0→1.14) |
| 4 | Telefon 12:30 | `s=2.4` dev karakter; iki el IK ile telefona; titreme için sinüs jitter; mavi ekran ışığı (`dir` aşağıdan); 3. sn'de bakış yukarı |
| 5 | Panik | 8 karakter koşar (`walk_legs` yüksek genlik), bazıları kırmızı ekranlı telefon tutar; kırmızı/mavi siren glow'u sinüsle dönüşümlü; el kamerası (`shake=7`) |
| 6 | Göz yakın plan | tek dev kafa (`R=640`, önbelleğe alınır); sağ göz merkezde; gözbebeği içinde "anılar" (seccade, 05:12 saat, YARIN takvimi) sağdan sola geçer; 4.0–4.5 sn arasında göz kırpma |
| 7 | Batıdan ışık | 1280×1100 tuval; ufuk glow'u + güneş diski yükselir; bulut dokusu (`cloud_tex`, büyük oktavlar 60/120/240) glow çevresinde açılır; silüet karakter (`show_face=False`, güçlü rim); "◀ BATI" / "DOĞU ▶" etiketleri; kamera yukarı tilt |
| 8 | Dehşet | kırmızı gökyüzü, 5 büyük karakter, alçak açı hissi; eller IK ile ağza (`af=1`; sol kol `bend=+1`, sağ `-1`); titreme ve kırmızı nabız |
| 9 | Diz çökme | 8 karakter profil (`mir=-1`), kademeli (`kneel_spec(ts)`): ayakta → diz çök → kollar yukarı → gözyaşı; yatay toz çizgileri |
| 10 | Pişmanlık | kara fon, tepe spot ışığı (`_cone`), ana karakter diz çökmüş, eller göğüste (IK), kafa öne eğilir, gözyaşı akar, kor parçacıkları |
| 11 | Uyanış | gündüz odası, güneş huzmesi (`_beam`), beyaz flaş (ilk 0.5 sn), hızlı oturma, hızlı nefes, gözleri ovma (IK + sinüs), kuşlar, toz zerreleri, yavaş gülümseme |
| 12 | Secde | seccade (perspektifli yamuk), karakter profil, ayakta→diz→secde (`dy`: 158→36→93, `ta`: 0→3→105, `fr=-85`), eller IK ile yere; son 0.8 sn karartma |

Pozlar için kritik değerler:
- **Diz çökme (sağa bakan):** `dy=36, la1=ra1=75, la2=ra2=-90, fd=-1`, `y = G - 36*s`.
- **Secde:** `dy=93, ta=105, ha=-5, fr=-85, la1=ra1=7, la2=ra2=-90, fd=-1`; kollar IK ile `(omuz.x ∓ 30*s, G - 8*s)`, `bend=+1`.
- **Yatma:** `ta=-90, fr=85, la1=ra1=88, la2=ra2=90, dy=30` (G=yatak üstü).

---

## 6. Yeni senaryo / yeni şablon eklerken

1. Senaryoyu `CAPS` listesine altyazı olarak yaz (sahne başına en fazla ~2 satır).
2. `scenes.py`'de yeni `sceneN(t)` yaz; mevcut sahnelerden birini kopyalayıp değiştirmek en hızlısı. `SCENES` listesine ekle.
3. Sahne sayısı veya süre değişirse `render.py` ve `audio.py` içindeki 5 sn × 12 varsayımını güncelle.
4. Önce `test.py` ile 3–4 kare bak; sonra tam render.
5. Tek sahne değiştiyse **yalnızca o sahneyi** yeniden render et (`python3 render.py 7`), `concat -c copy` ile tekrar birleştir. Ses değiştiyse `-c:v copy` ile yalnızca sesi yeniden ekle.
6. Yeni şablonu **yeni klasöre** koy, demo mp4 ekle, `animasyon skills` klasörünü zipleyip teslim et.

Başka karakter istenirse: `engine.py` içindeki `BASE` rengi, `HR` (kafa yarıçapı), uzuv uzunlukları (`joints` içinde 95, 80, 68, 62) ve yüz fonksiyonu (`draw_face`) değiştirilir. Sahne kodları aynı kalır.

---

## 7. Bilinen sınırlar ve çözümleri

- **Kenar yansıması (aynalı görüntü):** kamera merkezi tuval dışına taşarsa `BORDER_REFLECT` görüntüyü yansıtır. `camera()` artık merkezi sınırlıyor; yine de yeni sahnede `z` ve `cy` değerlerini kontrol et.
- **Renk doygunluğu:** kırmızı/mavi ışık ortama karışırsa karakter turuncu/mavi olur. Ortamı nötr tut, rengi `rim` ile ver.
- **Saat/yazı bozulması yok:** metin PIL ile basıldığı için "08:15", "12:30" her zaman doğru çıkar (yapay zekâ videolarında bozulan şey).
- **Eller basit:** el = eldiven + başparmak. Parmaklı el gerekirse `draw_char` içindeki `arms()` genişletilir.
- **Kalabalıkta yüz detayı:** 12 karakterden fazlasını tek sahnede çizme; hem yavaşlar hem okunaklılığı bozar.
- **Gerçek 3D değil:** kullanıcı Blender/AI video sonucu isterse, `SKILL.md`'deki sahne açıklamalarını ve ana karakter kilidi promptunu kullanarak o araçlar için ayrıca prompt paketi hazırla.
- **Dış ses:** Türkçe TTS yoksa yapılamaz; altyazı + sentez ses teslim et, kullanıcıya açıkça söyle.
- **Dini hassasiyet:** secde, ezan, tövbe gibi unsurlar saygılı ve sade işlendi (yüz profil/yere dönük, gözler kapalı, ezan sentezlenmedi; sadece yumuşak ney). Değiştirme isteği gelirse sahne 12'nin pozu `scene12` içinde değişir.

---

## 8. Kontrol listesi (teslimden önce)

- [ ] Karakter referansa benziyor mu (büyük kafa, iri siyah göz, ince kaşlar)?
- [ ] Her sahne için en az 2 kare kontak sheet'te kontrol edildi mi?
- [ ] Altyazılar Türkçe karakterlerle doğru mu (ş, ğ, ı, İ)?
- [ ] Toplam süre 60.0 sn, 1280×720, h264 + aac mi?
- [ ] Kenarlarda yansıma/siyah bant yok mu?
- [ ] Ses 49.6–50.0 sn arasında kısa sessizlik bırakıyor mu (S10→S11 geçişi)?
- [ ] Kullanıcıya dürüst notlar verildi mi (3D değil, dış ses yok, ses sentez)?
- [ ] `demo/` içine örnek mp4 konuldu, klasör zipe eklendi mi?
