import sys
import json
import re
sys.stdout.reconfigure(encoding='utf-8')

from key_pool import pool

prompt = """Sen bir YouTube Shorts video tasarımcısısın.
Kullanıcı konusu: 'Karadeliklerin içinde ne var?'
Lütfen aşağıdaki JSON formatında bir şema döndür. Sadece saf JSON döndür, başka hiçbir açıklama yazma:
{
  "headerSubtitle": "Uzayın En Büyük Gizemi",
  "headerMain": "KARADELİĞİN İÇİNE DÜŞERSEK NE OLUR?",
  "circledWord": "DÜŞERSEK",
  "highlightedText": "NE OLUR?",
  "cards": [
    {"id": "1", "label": "çekim gücü", "value": "sonsuz", "icon": "galaxy", "color": "#1e3a8a"},
    {"id": "2", "label": "zaman", "value": "durur", "icon": "clock", "color": "#15803d"},
    {"id": "3", "label": "ışık", "value": "kaçamaz", "icon": "lightbulb", "color": "#854d0e"}
  ],
  "timeline": {
    "startYear": "Olay Ufku",
    "endYear": "Tekillik",
    "durationLabel": "Sonsuzluk",
    "title": "Zamanın Bittiği Nokta",
    "ayahTranslation": "Işığın bile kaçamadığı kozmik tuzak.",
    "ayahRef": "Genel Görelilik"
  },
  "narration": "Bir karadeliğin içine düşersen ne olur? Işık bile onun devasa çekim gücünden kaçamaz. Olay ufkunu geçtiğin an zaman senin için yavaşlar, merkezde ise tamamen durur."
}
"""

res, key_name = pool.query_with_rotation(prompt, "You are a specialized JSON video schema generator. Output ONLY raw JSON.")
print("Key used:", key_name)
if res:
    # clean markdown codeblock ```json ... ```
    cleaned = re.sub(r"```json\s*", "", res)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()
    data = json.loads(cleaned)
    print("Parsed JSON successfully!")
    print(json.dumps(data, ensure_ascii=False, indent=2))
else:
    print("Failed to get response")
