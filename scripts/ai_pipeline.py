import os
import sys
import json
import argparse
from gtts import gTTS

# Set UTF-8 encoding for Windows terminal
sys.stdout.reconfigure(encoding='utf-8')

TEMPLATES = {
    "ibnisina": {
        "headerSubtitle": "İlim peşinde bir dâhi",
        "headerMain": "BİR KİTABI NEDEN 40 KEZ OKUDU?",
        "circledWord": "40 KEZ",
        "highlightedText": "YİNE ANLAMADI?",
        "cards": [
            {
                "id": "1",
                "label": "hafızlık",
                "value": "10 yaş",
                "icon": "book",
                "color": "#15803d"
            },
            {
                "id": "2",
                "label": "hekimlik",
                "value": "16 yaş",
                "icon": "embryo",
                "color": "#1e3a8a"
            },
            {
                "id": "3",
                "label": "bütün ilimler",
                "value": "18 yaş",
                "icon": "lightbulb",
                "color": "#854d0e"
            }
        ],
        "timeline": {
            "startYear": "980",
            "endYear": "1037",
            "durationLabel": "57 yıl",
            "title": "İbn-i Sina'nın İlim Mirası",
            "ayahArabic": "العِلْمُ نُورٌ",
            "ayahTranslation": "Kısa ama geniş bir ömür.",
            "ayahRef": "Avicenna"
        },
        "socialHandle": "@birkissa",
        "narration": "Bir kitabı tam kırk kez okudu ve yine de anlamadı. Oysa on yaşında hafız, on altısında hekim, on sekizinde bütün ilimlere hâkimdi. Aristo'nun Metafizik kitabını Farabi'nin üç dirhemlik şerhiyle çözdü. Dostlarına dedi ki: Uzun ama dar bir ömür yerine, kısa ama geniş bir ömrü tercih ederim."
    },
    "kainat": {
        "headerSubtitle": "Allah kâinatı",
        "headerMain": "NEDEN BİRDEN DEĞİL DE ALTI GÜNDE?",
        "circledWord": "BİRDEN",
        "highlightedText": "ALTI GÜNDE?",
        "cards": [
            {
                "id": "1",
                "label": "kâinat",
                "value": "6 gün",
                "icon": "galaxy",
                "color": "#1e3a8a"
            },
            {
                "id": "2",
                "label": "anne karnında",
                "value": "9 ay",
                "icon": "embryo",
                "color": "#15803d"
            },
            {
                "id": "3",
                "label": "Kur'an",
                "value": "23 yıl",
                "icon": "book",
                "color": "#854d0e"
            }
        ],
        "timeline": {
            "startYear": "610",
            "endYear": "632",
            "durationLabel": "23 yıl",
            "title": "Vahiy de böyle geldi",
            "ayahArabic": "لِنُثَبِّتَ بِهِ فُؤَادَكَ",
            "ayahTranslation": "Kalbine iyice yerleşsin diye.",
            "ayahRef": "Furkân 32"
        },
        "socialHandle": "@kanitlarla_islam",
        "narration": "Allah, kâinatı neden birden değil de altı günde yarattı? Oysa ol dese bir anda oluverirdi. Seni de anne karnında dokuz ayda yarattı. Kur'an'ı yirmi üç yılda indirdi. Kudreti sınırsız olan Allah bile acele etmiyorsa, adım adım gelen bu ölçü bir ilmin imzasıdır."
    }
}

def generate_subtitles(text: str, total_duration: float):
    words = text.split()
    if not words:
        return []
    time_per_word = total_duration / len(words)
    subtitles = []
    
    # Group in chunks of 3-4 words for short aesthetic subtitle boxes
    chunk_size = 4
    for i in range(0, len(words), chunk_size):
        chunk = words[i:i + chunk_size]
        start = round(i * time_per_word, 2)
        end = round(min(total_duration, (i + len(chunk)) * time_per_word), 2)
        subtitles.append({
            "text": " ".join(chunk),
            "start": start,
            "end": end
        })
    return subtitles

def main():
    parser = argparse.ArgumentParser(description="Notebook Explainer Video AI Pipeline")
    parser.add_argument("--topic", type=str, default="kainat", help="Topic key (kainat, ibnisina) or custom prompt")
    parser.add_argument("--voice", type=str, default="tr", help="Language code")
    args = parser.parse_args()

    topic_key = args.topic.lower()
    if topic_key in TEMPLATES:
        video_data = TEMPLATES[topic_key]
    else:
        # Default fallback to kainat template with custom header
        video_data = TEMPLATES["kainat"].copy()
        video_data["headerSubtitle"] = "Merak Edilen Soru"
        video_data["headerMain"] = args.topic.upper()

    print(f"\n[1/4] Senaryo ve Şema Hazırlandı: '{video_data['headerMain']}'")

    # Generate Audio via gTTS
    public_dir = os.path.join(os.path.dirname(__file__), "..", "public")
    os.makedirs(public_dir, exist_ok=True)
    audio_path = os.path.join(public_dir, "audio.mp3")

    print("[2/4] Seslendirme üretiliyor (TTS)...")
    tts = gTTS(text=video_data["narration"], lang=args.voice)
    tts.save(audio_path)
    print(f"      Ses kaydedildi: {audio_path}")

    # Estimate audio duration or use mutagen/ffmpeg
    # Rough estimate: ~140 words per minute -> 2.3 words/sec
    word_count = len(video_data["narration"].split())
    estimated_duration = max(8.0, word_count / 2.2)

    # Subtitles
    print("[3/4] Senkronize altyazılar hesaplanıyor...")
    video_data["subtitles"] = generate_subtitles(video_data["narration"], estimated_duration)
    video_data["audioUrl"] = "audio.mp3"

    # Save to generatedData.json in src/
    out_json = os.path.join(os.path.dirname(__file__), "..", "src", "generatedData.json")
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(video_data, f, ensure_ascii=False, indent=2)
    print(f"[4/4] Video verisi kaydedildi: {out_json}")
    print("\n Başarılı! 'npm run build' veya 'npm run start' komutuyla videoyu izleyebilir veya render alabilirsiniz.")

if __name__ == "__main__":
    main()
