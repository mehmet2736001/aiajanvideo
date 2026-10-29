import os
import json
import re
import urllib.request
from typing import Dict, List, Optional

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PUBLIC_DIR = os.path.join(BASE_DIR, "public")
ASSETS_DIR = os.path.join(PUBLIC_DIR, "assets")
ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
WATERMARKS_DIR = os.path.join(ASSETS_DIR, "watermarks")
SFX_DIR = os.path.join(PUBLIC_DIR, "sfx")
MANIFEST_PATH = os.path.join(ASSETS_DIR, "manifest.json")

os.makedirs(ICONS_DIR, exist_ok=True)
os.makedirs(WATERMARKS_DIR, exist_ok=True)
os.makedirs(SFX_DIR, exist_ok=True)

# Curated high-precision vector SVGs for core concepts
CORE_ICONS = {
    "crescent": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 68 15 C 40 22 24 50 34 78 C 42 92 58 98 72 90 C 48 88 38 66 46 44 C 52 28 62 18 68 15 Z" fill="currentColor" fill-opacity="0.2"/>
  <circle cx="72" cy="40" r="5" fill="currentColor"/>
</svg>""",

    "kaaba": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3" stroke-linejoin="round">
  <polygon points="50 18, 86 34, 50 50, 14 34" fill="currentColor" fill-opacity="0.3"/>
  <polygon points="14 34, 50 50, 50 88, 14 72" fill="currentColor" fill-opacity="0.5"/>
  <polygon points="50 50, 86 34, 86 72, 50 88" fill="currentColor" fill-opacity="0.7"/>
  <line x1="14" y1="44" x2="50" y2="60" stroke="#facc15" stroke-width="4"/>
  <line x1="50" y1="60" x2="86" y2="44" stroke="#facc15" stroke-width="4"/>
</svg>""",

    "islamic_star": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5">
  <rect x="25" y="25" width="50" height="50" rx="3" fill="currentColor" fill-opacity="0.15"/>
  <rect x="25" y="25" width="50" height="50" rx="3" transform="rotate(45 50 50)" fill="currentColor" fill-opacity="0.15"/>
  <circle cx="50" cy="50" r="12" fill="currentColor" fill-opacity="0.4"/>
</svg>""",

    "fingerprint": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round">
  <path d="M 50 15 C 32 15 20 30 20 50 C 20 80 32 92 50 95" />
  <path d="M 50 25 C 38 25 30 36 30 50 C 30 74 38 86 50 88" />
  <path d="M 50 35 C 44 35 40 42 40 50 C 40 68 44 76 50 80" />
  <path d="M 50 15 C 68 15 80 30 80 50 C 80 80 68 92 50 95" />
  <path d="M 50 25 C 62 25 70 36 70 50 C 70 74 62 86 50 88" />
  <path d="M 50 35 C 56 35 60 42 60 50 C 60 68 56 76 50 80" />
  <circle cx="50" cy="50" r="3.5" fill="currentColor" />
</svg>""",

    "dna": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round">
  <path d="M 28 15 C 72 38 72 62 28 85" />
  <path d="M 72 15 C 28 38 28 62 72 85" />
  <line x1="38" y1="28" x2="62" y2="28" stroke-width="3" />
  <line x1="46" y1="50" x2="54" y2="50" stroke-width="3" />
  <line x1="38" y1="72" x2="62" y2="72" stroke-width="3" />
  <circle cx="38" cy="28" r="3" fill="currentColor"/>
  <circle cx="62" cy="28" r="3" fill="currentColor"/>
  <circle cx="38" cy="72" r="3" fill="currentColor"/>
  <circle cx="62" cy="72" r="3" fill="currentColor"/>
</svg>""",

    "atom": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5">
  <ellipse cx="50" cy="50" rx="42" ry="16" transform="rotate(30 50 50)" />
  <ellipse cx="50" cy="50" rx="42" ry="16" transform="rotate(-30 50 50)" />
  <circle cx="50" cy="50" r="9" fill="currentColor" />
  <circle cx="20" cy="35" r="3.5" fill="currentColor" />
  <circle cx="80" cy="65" r="3.5" fill="currentColor" />
</svg>""",

    "brain": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 48 20 C 40 20 30 26 30 36 C 24 38 20 46 22 54 C 20 62 25 72 34 76 C 36 82 42 86 48 86" />
  <path d="M 52 20 C 60 20 70 26 70 36 C 76 38 80 46 78 54 C 80 62 75 72 66 76 C 64 82 58 86 52 86" />
  <line x1="50" y1="20" x2="50" y2="86" stroke-width="2.5" stroke-dasharray="4 3"/>
  <path d="M 34 44 C 40 46 44 40 48 42" />
  <path d="M 66 44 C 60 46 56 40 52 42" />
  <path d="M 32 62 C 40 60 42 68 48 66" />
  <path d="M 68 62 C 60 60 58 68 52 66" />
</svg>""",

    "heart": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="currentColor">
  <path d="M 50 86 L 44 80 C 22 60 12 48 12 34 C 12 22 22 14 34 14 C 41 14 47 17 50 22 C 53 17 59 14 66 14 C 78 14 88 22 88 34 C 88 48 78 60 56 80 Z" />
</svg>""",

    "eye": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round">
  <path d="M 12 50 Q 50 16 88 50 Q 50 84 12 50 Z" />
  <circle cx="50" cy="50" r="16" fill="currentColor" fill-opacity="0.2" stroke-width="3" />
  <circle cx="50" cy="50" r="8" fill="currentColor" />
  <circle cx="46" cy="46" r="3" fill="#ffffff" />
</svg>""",

    "scale": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round">
  <line x1="50" y1="16" x2="50" y2="86" stroke-width="4"/>
  <line x1="30" y1="86" x2="70" y2="86" stroke-width="5"/>
  <line x1="18" y1="28" x2="82" y2="28" stroke-width="4"/>
  <circle cx="50" cy="20" r="4" fill="currentColor"/>
  <!-- Left Pan -->
  <line x1="20" y1="28" x2="12" y2="52"/>
  <line x1="20" y1="28" x2="28" y2="52"/>
  <path d="M 10 52 Q 20 62 30 52 Z" fill="currentColor" fill-opacity="0.3"/>
  <!-- Right Pan -->
  <line x1="80" y1="28" x2="72" y2="52"/>
  <line x1="80" y1="28" x2="88" y2="52"/>
  <path d="M 70 52 Q 80 62 90 52 Z" fill="currentColor" fill-opacity="0.3"/>
</svg>""",

    "hourglass": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round">
  <line x1="24" y1="18" x2="76" y2="18" stroke-width="5"/>
  <line x1="24" y1="82" x2="76" y2="82" stroke-width="5"/>
  <path d="M 30 18 L 70 18 L 54 48 C 52 50 52 50 54 52 L 70 82 L 30 82 L 46 52 C 48 50 48 50 46 48 Z" fill="currentColor" fill-opacity="0.15"/>
  <polygon points="40 76, 60 76, 50 64" fill="currentColor"/>
  <circle cx="50" cy="54" r="2" fill="currentColor"/>
</svg>""",

    "book": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">
  <path d="M 50 26 C 38 18 20 18 14 22 L 14 78 C 20 74 38 74 50 82 C 62 74 80 74 86 78 L 86 22 C 80 18 62 18 50 26 Z" fill="currentColor" fill-opacity="0.2"/>
  <line x1="50" y1="26" x2="50" y2="82" stroke-width="4"/>
  <line x1="24" y1="38" x2="42" y2="38" stroke-width="2.5"/>
  <line x1="24" y1="50" x2="42" y2="50" stroke-width="2.5"/>
  <line x1="58" y1="38" x2="76" y2="38" stroke-width="2.5"/>
  <line x1="58" y1="50" x2="76" y2="50" stroke-width="2.5"/>
</svg>""",

    "lightbulb": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round">
  <path d="M 34 38 C 34 24 66 24 66 38 C 66 48 58 54 58 64 L 42 64 C 42 54 34 48 34 38 Z" fill="currentColor" fill-opacity="0.2"/>
  <line x1="42" y1="70" x2="58" y2="70" stroke-width="4"/>
  <line x1="45" y1="76" x2="55" y2="76" stroke-width="4"/>
  <path d="M 50 14 L 50 8" stroke-width="3"/>
  <path d="M 22 24 L 17 19" stroke-width="3"/>
  <path d="M 78 24 L 83 19" stroke-width="3"/>
  <path d="M 16 44 L 10 44" stroke-width="3"/>
  <path d="M 84 44 L 90 44" stroke-width="3"/>
</svg>""",

    "compass": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5">
  <circle cx="50" cy="50" r="38" stroke-width="4"/>
  <polygon points="50 20, 58 46, 50 50, 42 46" fill="#ef4444" stroke="#ef4444"/>
  <polygon points="50 80, 58 54, 50 50, 42 54" fill="currentColor" fill-opacity="0.4"/>
  <circle cx="50" cy="50" r="4" fill="#ffffff" stroke="currentColor" stroke-width="2"/>
  <text x="50" y="15" text-anchor="middle" font-size="10" font-weight="bold" fill="currentColor">K</text>
</svg>""",

    "shield": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round">
  <path d="M 50 16 L 82 26 C 82 58 68 78 50 88 C 32 78 18 58 18 26 Z" fill="currentColor" fill-opacity="0.2"/>
  <path d="M 50 32 L 68 38 C 68 56 60 70 50 76 C 40 70 32 56 32 38 Z" fill="currentColor" fill-opacity="0.3"/>
</svg>""",

    "infinity": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round">
  <path d="M 32 36 C 18 36 14 50 14 50 C 14 50 18 64 32 64 C 46 64 54 50 54 50 C 54 50 62 36 76 36 C 90 36 94 50 94 50 C 94 50 90 64 76 64 C 62 64 54 50 54 50 C 54 50 46 36 32 36 Z" />
</svg>"""
}

# Curated watermark SVG patterns
CORE_WATERMARKS = {
    "islamic_geometric": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" fill="none" stroke="currentColor" stroke-width="2.5" opacity="0.12">
  <g transform="translate(200, 200)">
    <circle cx="0" cy="0" r="160" />
    <circle cx="0" cy="0" r="110" />
    <circle cx="0" cy="0" r="60" />
    <rect x="-80" y="-80" width="160" height="160" />
    <rect x="-80" y="-80" width="160" height="160" transform="rotate(45)" />
    <rect x="-80" y="-80" width="160" height="160" transform="rotate(22.5)" />
    <rect x="-80" y="-80" width="160" height="160" transform="rotate(67.5)" />
  </g>
</svg>""",

    "fingerprint": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 300 400" fill="none" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.08">
  <path d="M 150 40 C 90 40 50 90 50 170 C 50 280 90 340 150 360" />
  <path d="M 150 70 C 110 70 80 110 80 170 C 80 250 110 320 150 330" />
  <path d="M 150 100 C 130 100 110 130 110 170 C 110 230 130 270 150 290" />
  <path d="M 150 40 C 210 40 250 90 250 170 C 250 280 210 340 150 360" />
  <path d="M 150 70 C 190 70 220 110 220 170 C 220 250 190 320 150 330" />
  <path d="M 150 100 C 170 100 190 130 190 170 C 190 230 170 270 150 290" />
  <circle cx="150" cy="170" r="10" fill="currentColor"/>
</svg>""",

    "dna": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 400" fill="none" stroke="currentColor" stroke-width="5" stroke-linecap="round" opacity="0.10">
  <path d="M 50 30 C 150 100 150 170 50 240 C -50 310 -50 380 50 450" />
  <path d="M 150 30 C 50 100 50 170 150 240 C 250 310 250 380 150 450" />
</svg>""",

    "cosmic": """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 400" fill="none" stroke="currentColor" stroke-width="2" opacity="0.10">
  <circle cx="200" cy="200" r="180" stroke-dasharray="8 6"/>
  <circle cx="200" cy="200" r="130"/>
  <circle cx="200" cy="200" r="70" stroke-dasharray="4 4"/>
  <line x1="20" y1="200" x2="380" y2="200"/>
  <line x1="200" y1="20" x2="200" y2="380"/>
</svg>"""
}

def load_manifest() -> dict:
    if os.path.exists(MANIFEST_PATH):
        try:
            with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"icons": {}, "watermarks": {}, "sfx": {}, "last_updated": ""}

def save_manifest(manifest: dict):
    with open(MANIFEST_PATH, "w", encoding="utf-8") as f:
        json.dump(manifest, f, ensure_ascii=False, indent=2)

def initialize_core_assets():
    """Populates local disk with core vectors and creates manifest if not present"""
    manifest = load_manifest()
    
    # Save Core Icons
    for name, svg_content in CORE_ICONS.items():
        file_path = os.path.join(ICONS_DIR, f"{name}.svg")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(svg_content.strip())
        manifest["icons"][name] = {
            "path": f"assets/icons/{name}.svg",
            "type": "vector_svg",
            "source": "curated_core"
        }

    # Save Core Watermarks
    for name, svg_content in CORE_WATERMARKS.items():
        file_path = os.path.join(WATERMARKS_DIR, f"{name}.svg")
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(svg_content.strip())
        manifest["watermarks"][name] = {
            "path": f"assets/watermarks/{name}.svg",
            "type": "vector_svg",
            "source": "curated_core"
        }

    save_manifest(manifest)
    print(f"Core assets initialized: {len(CORE_ICONS)} icons, {len(CORE_WATERMARKS)} watermarks ready on disk.")

def generate_missing_svg(asset_name: str, pool=None) -> Optional[str]:
    """Uses LLM from key pool to generate a clean, responsive SVG vector icon"""
    if not pool:
        return None

    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', asset_name.lower().replace(' ', '_'))
    prompt = f"""Sen uzman bir minimalist SVG vektör ikon tasarımcısısın.
İstenen İkon Konsepti: '{clean_name}' (Türkçe/İngilizce kavram)
Gereksinimler:
1. SADECE saf ve geçerli SVG kodu döndür: <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round">...</svg>
2. Responsive olsun, 100x100 viewBox içinde ortalanmış olsun.
3. Minimalist, modern, profesyonel çizgilere sahip olsun.
4. Başka hiçbir açıklama, markdown veya metin yazma, sadece <svg>...</svg> döndür.
"""
    try:
        res, key_name = pool.query_with_rotation(prompt, "Output ONLY valid raw SVG xml. No markdown.")
        if res:
            match = re.search(r'(<svg[\s\S]*?<\/svg>)', res, re.IGNORECASE)
            if match:
                svg_code = match.group(1).strip()
                target_path = os.path.join(ICONS_DIR, f"{clean_name}.svg")
                with open(target_path, "w", encoding="utf-8") as f:
                    f.write(svg_code)
                
                manifest = load_manifest()
                manifest["icons"][clean_name] = {
                    "path": f"assets/icons/{clean_name}.svg",
                    "type": "vector_svg",
                    "source": "ai_generated",
                    "generated_by": key_name
                }
                save_manifest(manifest)
                print(f"✨ AI Vector Asset Generated & Saved: assets/icons/{clean_name}.svg")
                return f"assets/icons/{clean_name}.svg"
    except Exception as e:
        print(f"Asset generation error for {asset_name}: {e}")
    return None

def ensure_asset(asset_name: str, asset_type: str = "icon", pool=None) -> str:
    """Checks if asset exists on local disk, generates or retrieves if missing"""
    clean_name = re.sub(r'[^a-zA-Z0-9_]', '', asset_name.lower().replace(' ', '_').replace('-', '_'))
    
    if asset_type == "icon":
        file_path = os.path.join(ICONS_DIR, f"{clean_name}.svg")
        if os.path.exists(file_path):
            return f"assets/icons/{clean_name}.svg"
        
        # Check core icons map
        if clean_name in CORE_ICONS:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(CORE_ICONS[clean_name].strip())
            return f"assets/icons/{clean_name}.svg"
        
        # If missing, generate via AI
        generated = generate_missing_svg(clean_name, pool=pool)
        if generated:
            return generated
        
        return "assets/icons/fingerprint.svg"

    elif asset_type == "watermark":
        file_path = os.path.join(WATERMARKS_DIR, f"{clean_name}.svg")
        if os.path.exists(file_path):
            return f"assets/watermarks/{clean_name}.svg"
        if clean_name in CORE_WATERMARKS:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(CORE_WATERMARKS[clean_name].strip())
            return f"assets/watermarks/{clean_name}.svg"
        return "assets/watermarks/fingerprint.svg"

    return ""

def process_video_assets(video_data: dict, pool=None) -> dict:
    """Adım 2: Scans video_data for all required visual assets, ensures they exist on disk,
    downloads or generates missing ones, and returns updated video_data with asset paths."""
    acquired_assets = []

    # 1. Background Watermark
    watermark_req = video_data.get("ambientPattern", "none")
    if watermark_req and watermark_req != "none":
        w_path = ensure_asset(watermark_req, asset_type="watermark", pool=pool)
        acquired_assets.append({"name": watermark_req, "type": "watermark", "path": w_path})

    # 2. Layout Specific Icons
    # Grid Explosion
    if video_data.get("gridExplosion"):
        g_icon = video_data["gridExplosion"].get("iconType", "fingerprint")
        i_path = ensure_asset(g_icon, asset_type="icon", pool=pool)
        video_data["gridExplosion"]["iconAssetPath"] = i_path
        acquired_assets.append({"name": g_icon, "type": "grid_icon", "path": i_path})

    # Tri Concept
    if video_data.get("triConcept"):
        tc = video_data["triConcept"]
        for key in ["concept1", "concept2", "concept3"]:
            if key in tc and isinstance(tc[key], dict) and "icon" in tc[key]:
                c_icon = tc[key]["icon"]
                i_path = ensure_asset(c_icon, asset_type="icon", pool=pool)
                tc[key]["iconAssetPath"] = i_path
                acquired_assets.append({"name": c_icon, "type": "concept_icon", "path": i_path})

    # Cards Grid
    if video_data.get("cards"):
        for card in video_data["cards"]:
            if "icon" in card:
                c_icon = card["icon"]
                i_path = ensure_asset(c_icon, asset_type="icon", pool=pool)
                card["iconAssetPath"] = i_path
                acquired_assets.append({"name": c_icon, "type": "card_icon", "path": i_path})

    video_data["_acquired_assets"] = acquired_assets
    return video_data

if __name__ == "__main__":
    initialize_core_assets()
