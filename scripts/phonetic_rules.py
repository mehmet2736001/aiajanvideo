"""
scripts/phonetic_rules.py

Uzman Türkçe Fonetik ve Fıkhi Terminoloji Düzeltme Modülü.
Whisper AI ve ASR modellerinin hızlı Türkçe konuşma, İslami ilimler/fıkıh terimleri,
Arapça/Osmanlıca kökenli kelimeler ve halk ağzı kaynaşmalarında yaptığı akustik/fonetik
hataları TDK imla kılavuzuna ve fıkhi terminolojiye göre restore eder.
"""

import re
from typing import Dict, List, Tuple

# Doğrudan kelime/öbek düzeyinde fonetik dönüşüm kuralları
# (Whisper Hatalı Akustik Döküm -> Doğru İmla & Terminoloji)
PHONETIC_REPLACEMENTS: Dict[str, str] = {
    # 1. Kullanıcının bildirdiği kritik hatalar & Kaynaşmış Soru / Edat Kalıpları
    "mühe defa": "mı hedefe",
    "mü hedefe": "mı hedefe",
    "mu hedefe": "mı hedefe",
    "dinisenden": "dini senden",
    "müörenceğiz": "mı öğreneceğiz",
    "müöreneceğiz": "mı öğreneceğiz",
    "mürenceğiz": "mı öğreneceğiz",
    "okudesen": "oku desen",
    "getirdesen": "getir desen",
    "güzeli mislamı": "güzelim İslam'ı",
    "mislamı": "İslam'ı",
    "demez miydim": "demez miydi",
    "koca sının": "kocasının",
    "alibunları": "Ali bunları",
    
    # 2. İslami ve Fıkhi Terminoloji Hataları
    "fıkında": "fıkhında",
    "fıkıta": "fıkıhta",
    "fıkı": "fıkıh",
    "fuki": "fıkhî",
    "fethvalar": "fetvalar",
    "fethva": "fetva",
    "fethvalar mesine": "fetva vermesine",
    "sahik": "sahih",
    "sai": "sahih",
    "mağruf": "maruf",
    "kavvam": "kavvam",
    "saali hak": "saliha",
    "saali hak adınların": "saliha kadınların",
    "kazayı hütümleriyle": "kazaî hükümleriyle",
    "kazayı": "kazaî",
    "hütümleriyle": "hükümleriyle",
    "hütümleri": "hükümleri",
    "kulum diyenin": "kulun diyaneten",
    "diyeni": "diyanî",
    "diyeneten": "diyaneten",
    "vajı buldu": "vacip olduğu",
    "vajı": "vacip",
    "el mepsut": "el-Mebsût",
    "el-mepsut": "el-Mebsût",
    "reddür muhtar": "Reddü'l-Muhtâr",
    "reddül muhtar": "Reddü'l-Muhtâr",
    "reddü'l muhtar": "Reddü'l-Muhtâr",
    "serasinin": "Serahsî'nin",
    "imne abidinin": "İbn Âbidîn'in",
    "ibni abidin": "İbn Âbidîn",
    "resolu'la hak gerek": "Resûlullah'a gelerek",
    "resolu'la": "Resûlullah",
    "resulullah": "Resûlullah",
    "hazıreti fatima": "Hazreti Fâtıma",
    "hazıreti": "Hazreti",
    "bu hariyi ve müslüm": "Buhârî ve Müslim",
    "bu hariyi": "Buhârî",
    "müslüm": "Müslim",
    "savrı ve tesbi hatı": "sabrı ve tesbihatı",
    "savrı": "sabrı",
    "tesbi hatı": "tesbihatı",
    "taksiybetmiştir": "taksim etmiştir",
    "nefaka": "nafaka",
    "mehire": "mehre",
    
    # 3. Genel Fonetik & Morfolojik Whisper Bozulmaları
    "ısırlık": "asırlık",
    "ziyneyet": "zihniyet",
    "yutuyumlüğüne": "yükümlülüğüne",
    "yutuyumluk": "yükümlülük",
    "çiftestlandardır": "çifte standarttır",
    "çiftestandart": "çifte standart",
    "çiftestandardır": "çifte standarttır",
    "bağri zöğüneydir": "bariz örneğidir",
    "bağri": "bariz",
    "zöğüneydir": "örneğidir",
    "zöğneğidir": "örneğidir",
    "benzetice": "benzetecek",
    "ödiceği": "ödeyeceği",
    "oku kunu": "hukukunu",
    "yapmaksorunda": "yapmak zorunda",
    "sıvın maktadır": "sığınmaktadır",
    "sıvınmak": "sığınmak",
    "arkadaşlı sisteminde": "arkadaşlığı sisteminde",
    "yüklidi": "yüklediği",
    "maddiğim ülkellefiyetleri": "maddi mükellefiyetleri",
    "ülkellefiyetleri": "mükellefiyetleri",
    "mükellefiyeti": "mükellefiyeti",
    "eviçi": "ev içi",
    "sorumluluğduklarını": "sorumluluklarını",
    "sorumluğu": "sorumluluğu",
    "konflunu": "konforuna",
    "kuranı ki": "Kaldı ki",
    "suurası": "Suresi",
    "sekizince": "sekizinci",
    "aileği için": "aile içi",
    "islam'a elimlerinin": "İslam âlimlerinin",
    "elimlerinin": "âlimlerinin",
    "yüzlere": "üzere",
    "yüzere": "üzere",
    "aileinin": "ailesinin",
    "herkeklerin": "erkeklerin",
    "beğen edilmiştir": "beyan edilmiştir",
    "kuranı kurduğu": "Kur'an'ın kurduğu",
    "yoksa yip": "yok sayıp",
    "indir yemek": "indirgemek",
    "iddia'ya": "iddiayı",
    "delilirse": "delil ise",
    "elde-iirmeni": "el değirmeni",
    "onu ütmekten": "un öğütmekten",
    "nasıır": "nasır",
    "kıyafetlerinın": "kıyafetlerinin",
    "sürpürme": "süpürme",
    "sürpürmekten": "süpürmekten",
    "sürpürmem": "süpürmem",
    "zorunduğunu": "zorunluluğu",
    "zorunduğun": "zorunluluğun",
    "zorunduluğum": "zorunluluğum",
    "yapma sakinaha": "yapmazsa günaha",
    "söyleme": "söylemi",
    "cimbızlayarak": "cımbızlayarak",
    "diğini tahri fethmenin": "dini tahrif etmenin",
    "tahri fethmenin": "tahrif etmenin",
    "diğini": "dini",
    "kendin nefislerine": "kendi nefislerine",
    "iyi bükmesini": "eğip bükmesine",
    "zere": "zerre",
    "yer parisine": "ciğerparesine",
    "hamuru yorma": "hamur yoğurma",
    "pişirmeye": "pişirme",
    "içişlerini": "iç işlerini",
    "bilmek tedir": "bilmektedir",
    "çobanadır": "çobanıdır",
    "altındakilardan": "altındakilerden",
    "içi daaretsinin": "iç idaresini",
    "boyuna": "boynuna",
    "kıymıştır": "koymuştur",
    "fakırtaki": "fıkıhtaki",
    "polis soru ile": "polis zoru ile",
    "haltan": "halktan",
    "mutfa": "mutfağa",
    "mesemin": "mezhebinin",
    "etme sağlında": "etmesi halinde",
    "günahker olacak": "günahkâr olacağı",
    "günahker": "günahkâr",
    "açıkca yazıldır": "açıkça yazılıdır",
    "yaptırla bilen": "yaptırılabilen",
    "indirgilecek şufu ki gerçiyide": "indirgeyeceksek şu fıkhî gerçeği de",
    "erkiğin": "erkeğin",
    "olduğunla fakah": "olduğu nafaka",
    "fakah": "fakat",
    "kuray": "kuru",
    "kuray ekmek": "kuru ekmek",
    "hervise": "elbise",
    "ibaretdir": "ibarettir",
    "metinderne": "metinlerine",
    "kırısının": "karısının",
    "ilerç": "ilaç",
    "yapmasın günaha girmem dese": "yapmazsam günaha girmem dese",
    "sınırılı bahaneye gerek": "sınırını bahane ederek",
    "mahkiü metmesin": "mahkûm etmesi",
    "kadınında": "kadının da",
    "çarpı tarak": "çarpıtarak",
    "gömleyini": "gömleğini",
    "sünnetini ihanettir": "sünnetine ihanettir",
    "melfat şebekez": "menfaat şebekesi"
}

# Regex tabanlı çoklu kalıp temizleyiciler
REGEX_PHONETIC_PATTERNS: List[Tuple[re.Pattern, str]] = [
    # Yuvasını mı hedefe
    (re.compile(r"\byuvasını\s+mühe\s+defa\b", re.IGNORECASE), "yuvasını mı hedefe"),
    (re.compile(r"\bmühe\s+defa\b", re.IGNORECASE), "mı hedefe"),
    # Dini senden mi öğreneceğiz
    (re.compile(r"\bdinisenden\s+müörenceğiz\b", re.IGNORECASE), "dini senden mi öğreneceğiz"),
    (re.compile(r"\binsanlardan\s+müörenceğiz\b", re.IGNORECASE), "insanlardan mı öğreneceğiz"),
    # Kur'an-ı Kerim ve ayet terimleri
    (re.compile(r"\bKuranı\s+ki\b", re.IGNORECASE), "Kaldı ki"),
    (re.compile(r"\bKuranı\s+kurduğu\b", re.IGNORECASE), "Kur'an'ın kurduğu"),
    (re.compile(r"\bKur'anı\b", re.IGNORECASE), "Kur'an'ı"),
    (re.compile(r"\bBakara\s+suurası\b", re.IGNORECASE), "Bakara Suresi"),
    (re.compile(r"\bNisa\s+suurası\b", re.IGNORECASE), "Nisa Suresi"),
    # İmam Serahsî ve İbn Âbidîn
    (re.compile(r"\bserasinin\s+el\s+mepsut\b", re.IGNORECASE), "Serahsî'nin el-Mebsût"),
    (re.compile(r"\bimne\s+abidinin\s+reddür\s+muhtar\b", re.IGNORECASE), "İbn Âbidîn'in Reddü'l-Muhtâr"),
    # Fıkhi ve İslami kavramlar
    (re.compile(r"\bfıkında\s+fethvalar\b", re.IGNORECASE), "fıkhında fetvalar"),
    (re.compile(r"\bİslam\s+adına\s+fethvalar\s+mesine\b", re.IGNORECASE), "İslam adına fetva vermesine"),
    (re.compile(r"\bdiğini\s+kendin\s+nefislerine\b", re.IGNORECASE), "dini kendi nefislerine"),
    (re.compile(r"\biyi\s+bükmesini\b", re.IGNORECASE), "eğip bükmesine"),
    (re.compile(r"\bartık\s+zere\s+kadar\b", re.IGNORECASE), "artık zerre kadar"),
    (re.compile(r"\bbağri\s+zöğüneydir\b", re.IGNORECASE), "bariz örneğidir"),
    (re.compile(r"\bmelfat\s+şebekez\b", re.IGNORECASE), "menfaat şebekesi"),
    (re.compile(r"\bçiftestlandardır\b", re.IGNORECASE), "çifte standarttır"),
]


def clean_phonetic_errors(text: str) -> str:
    """Metindeki tüm bilinen Whisper fonetik ve fıkhi döküm hatalarını düzeltir."""
    if not text:
        return ""

    result = text

    # Önce regex kalıplarını uygula
    for pattern, repl in REGEX_PHONETIC_PATTERNS:
        result = pattern.sub(repl, result)

    # Birebir sözlük eşleşmelerini uygula (uzun ifadelerden kısaya doğru)
    sorted_keys = sorted(PHONETIC_REPLACEMENTS.keys(), key=len, reverse=True)
    for wrong in sorted_keys:
        correct = PHONETIC_REPLACEMENTS[wrong]
        pattern = re.compile(rf"\b{re.escape(wrong)}\b", re.IGNORECASE)
        result = pattern.sub(correct, result)

    # Çift boşlukları ve imla temizliğini normalize et
    result = re.sub(r"\s+", " ", result).strip()
    return result


apply_phonetic_corrections = clean_phonetic_errors


if __name__ == "__main__":
    test_str = "Yuvasını mühe defa koymaya başladınız. Bu dinisenden müörenceğiz. İslam fıkında fethvalar vermek. İmam serasinin el mepsut ve imne abidinin reddür muhtar adlı eseri."
    cleaned = clean_phonetic_errors(test_str)
    print("Orijinal:", test_str)
    print("Düzeltilmiş:", cleaned)
