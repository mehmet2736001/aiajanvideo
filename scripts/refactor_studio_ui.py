import os
import re

INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "index.html"))

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Replace Section 2 (the 11 agents grid) with the Single Master Director Banner
section2_pattern = re.compile(
    r'<!-- 2\. İSTİŞARE HEYETİ & ÖĞRETMENLER KURULU.*?id="agentsGrid".*?</section>',
    re.DOTALL
)

section2_replacement = """<!-- 2. TEK BAŞYÖNETMEN MASASI & POLİMORFİK GARDIROP -->
    <section class="glass-panel rounded-2xl p-4 border border-gold-500/30 bg-gradient-to-r from-obsidian-950 via-obsidian-900 to-obsidian-950 shadow-xl">
      <div class="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        
        <!-- Sol: Başyönetmen Portre & Canlı Durum -->
        <div class="flex items-center gap-3.5">
          <div class="relative">
            <div class="w-14 h-14 rounded-2xl bg-gradient-to-tr from-gold-600 via-gold-400 to-amber-300 p-0.5 shadow-lg shadow-gold-500/20">
              <div class="w-full h-full bg-obsidian-950 rounded-[14px] flex items-center justify-center text-2xl">
                🎬
              </div>
            </div>
            <span class="absolute -bottom-1 -right-1 w-4 h-4 rounded-full bg-emerald-500 border-2 border-obsidian-950 flex items-center justify-center">
              <span class="w-1.5 h-1.5 rounded-full bg-white animate-ping"></span>
            </span>
          </div>

          <div>
            <div class="flex items-center gap-2 flex-wrap">
              <h2 class="font-display font-bold text-base md:text-lg text-white">Başyönetmen Selim Bey</h2>
              <span class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-gold-500/20 text-gold-300 border border-gold-500/40">Tek Yetkili Başyönetmen</span>
              <span id="directorApiBadge" class="text-[10px] font-mono px-2 py-0.5 rounded-full bg-emerald-500/15 text-emerald-400 border border-emerald-500/30 flex items-center gap-1">
                <span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Canlı Gemini 3.8 / 3.5 Flash
              </span>
            </div>
            <p class="text-xs text-slate-400 mt-0.5">
              Tüm bürokrasi kaldırıldı. İslami tefekkür, senaryo, Remotion kod, Turso ses ve 48 kare denetim elbiselerinin tamamını tek zihinde kuşanır.
            </p>
          </div>
        </div>

        <!-- Orta / Sağ: 5 Temel Elbise ve Sohbet Kontrolleri -->
        <div class="flex items-center gap-2 flex-wrap">
          <div class="flex items-center gap-1.5 bg-obsidian-950/80 p-1.5 rounded-xl border border-slate-800 text-[11px]">
            <span class="text-slate-500 text-[10px] px-1 font-semibold">Elbiseler:</span>
            <button onclick="wearWardrobePrompt('İslami Tefekkür & İlim')" class="wardrobe-pill px-2.5 py-1 rounded-lg bg-emerald-500/15 hover:bg-emerald-500/25 text-emerald-300 border border-emerald-500/30 transition flex items-center gap-1">
              <span>🕌</span> <span>Tefekkür</span>
            </button>
            <button onclick="wearWardrobePrompt('Viral Kanca & Senaryo')" class="wardrobe-pill px-2.5 py-1 rounded-lg bg-sky-500/15 hover:bg-sky-500/25 text-sky-300 border border-sky-500/30 transition flex items-center gap-1">
              <span>⚡</span> <span>Senaryo</span>
            </button>
            <button onclick="wearWardrobePrompt('Remotion Kod & Hareket')" class="wardrobe-pill px-2.5 py-1 rounded-lg bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 transition flex items-center gap-1">
              <span>🎬</span> <span>Remotion</span>
            </button>
            <button onclick="wearWardrobePrompt('Turso Ses & Helal Akustik')" class="wardrobe-pill px-2.5 py-1 rounded-lg bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 transition flex items-center gap-1">
              <span>🎙️</span> <span>Turso Ses</span>
            </button>
            <button onclick="wearWardrobePrompt('48 Kare Görsel Denetçi')" class="wardrobe-pill px-2.5 py-1 rounded-lg bg-rose-500/15 hover:bg-rose-500/25 text-rose-300 border border-rose-500/30 transition flex items-center gap-1">
              <span>👁️</span> <span>Denetim</span>
            </button>
          </div>

          <div class="flex items-center gap-2">
            <button onclick="startNewChatSession()" 
                    class="px-3.5 py-2 rounded-xl bg-gold-500/20 hover:bg-gold-500/30 text-gold-300 border border-gold-500/40 text-xs font-bold transition flex items-center gap-1.5 shadow"
                    title="Önceki sohbeti arşive kaldırıp temiz sayfa açar">
              <i data-lucide="plus-circle" class="w-3.5 h-3.5"></i>
              <span>Yeni Sohbet</span>
            </button>
            <button onclick="clearChatHistoryConfirm()" 
                    class="p-2 rounded-xl bg-obsidian-900 hover:bg-red-500/20 text-slate-400 hover:text-red-400 border border-slate-800 transition"
                    title="Sohbet geçmişini tamamen sil">
              <i data-lucide="trash-2" class="w-4 h-4"></i>
            </button>
          </div>
        </div>

      </div>
    </section>"""

content, count1 = section2_pattern.subn(section2_replacement, content)
print(f"Section 2 replaced: {count1} times")

# 2. Replace the sub-sidebar (11 teacher channels) with the Wardrobe & Status sidebar
sidebar_pattern = re.compile(
    r'<!-- KANALLAR KENAR ÇUBUĞU \(SUB-SIDEBAR\) -->.*?id="teacherChannelsList".*?</div>\s*</div>',
    re.DOTALL
)

sidebar_replacement = """<!-- SOL GARDIROP & STATÜ PANELİ (ELBİSELER & HAFIZA) -->
          <div class="w-48 sm:w-56 flex-shrink-0 flex flex-col gap-2 border-r border-slate-800/80 pr-3 overflow-y-auto">
            
            <!-- Aktif Başyönetmen Kartı -->
            <div class="p-3 rounded-xl border border-gold-500/30 bg-gold-500/10 text-left space-y-2">
              <div class="flex items-center gap-2">
                <span class="text-2xl">🎬</span>
                <div>
                  <strong class="text-xs text-gold-300 block">Selim Bey</strong>
                  <span class="text-[9px] text-slate-400 block font-mono">Tek Başyönetmen</span>
                </div>
              </div>
              <div class="pt-2 border-t border-gold-500/20 space-y-1">
                <div class="text-[9px] text-slate-400">Şu Anki Elbise:</div>
                <div id="sideActiveWardrobe" class="text-[10px] font-bold text-gold-400 bg-obsidian-950/80 px-2 py-1 rounded border border-gold-500/20 truncate">
                  Başyönetmen (Tüm Yetkinlikler)
                </div>
              </div>
            </div>

            <!-- Elbise Değiştir Butonları -->
            <div class="text-[9px] font-extrabold uppercase tracking-wider text-slate-500 px-1 pt-1 flex items-center justify-between">
              <span>Elbise Kuşan</span>
              <span class="text-[8px] text-slate-600">Polimorfik</span>
            </div>

            <div class="space-y-1 text-xs">
              <button onclick="wearWardrobePrompt('İslami Tefekkür & İlim')" class="w-full p-2 rounded-xl border border-slate-800 hover:border-emerald-500/40 bg-obsidian-950 hover:bg-emerald-500/10 text-left flex items-center gap-2 transition group">
                <span class="text-base">🕌</span>
                <div class="truncate">
                  <span class="text-slate-200 block text-xs group-hover:text-emerald-300 font-semibold">İslami Tefekkür</span>
                  <span class="text-[9px] text-slate-500 block truncate">Ayet, Hadis, Hikmet</span>
                </div>
              </button>
              <button onclick="wearWardrobePrompt('Viral Kanca & Senaryo')" class="w-full p-2 rounded-xl border border-slate-800 hover:border-sky-500/40 bg-obsidian-950 hover:bg-sky-500/10 text-left flex items-center gap-2 transition group">
                <span class="text-base">⚡</span>
                <div class="truncate">
                  <span class="text-slate-200 block text-xs group-hover:text-sky-300 font-semibold">Viral Kanca</span>
                  <span class="text-[9px] text-slate-500 block truncate">0-3s Hook & Ritim</span>
                </div>
              </button>
              <button onclick="wearWardrobePrompt('Remotion Kod & Hareket')" class="w-full p-2 rounded-xl border border-slate-800 hover:border-amber-500/40 bg-obsidian-950 hover:bg-amber-500/10 text-left flex items-center gap-2 transition group">
                <span class="text-base">🎬</span>
                <div class="truncate">
                  <span class="text-slate-200 block text-xs group-hover:text-amber-300 font-semibold">Remotion Kod</span>
                  <span class="text-[9px] text-slate-500 block truncate">Saf SVG & Tipografi</span>
                </div>
              </button>
              <button onclick="wearWardrobePrompt('Turso Ses & Helal Akustik')" class="w-full p-2 rounded-xl border border-slate-800 hover:border-purple-500/40 bg-obsidian-950 hover:bg-purple-500/10 text-left flex items-center gap-2 transition group">
                <span class="text-base">🎙️</span>
                <div class="truncate">
                  <span class="text-slate-200 block text-xs group-hover:text-purple-300 font-semibold">Turso Ses</span>
                  <span class="text-[9px] text-slate-500 block truncate">121 Ses Havuzu</span>
                </div>
              </button>
              <button onclick="wearWardrobePrompt('48 Kare Görsel Denetçi')" class="w-full p-2 rounded-xl border border-slate-800 hover:border-rose-500/40 bg-obsidian-950 hover:bg-rose-500/10 text-left flex items-center gap-2 transition group">
                <span class="text-base">👁️</span>
                <div class="truncate">
                  <span class="text-slate-200 block text-xs group-hover:text-rose-300 font-semibold">48 Kare Denetim</span>
                  <span class="text-[9px] text-slate-500 block truncate">Görsel Estetik</span>
                </div>
              </button>
            </div>

            <!-- Hafıza & API Durumu -->
            <div class="mt-auto pt-2 border-t border-slate-800/80 space-y-1.5 text-[10px]">
              <div class="flex items-center justify-between text-slate-400">
                <span>Hafıza:</span>
                <span id="sideHistoryCount" class="font-mono text-gold-400 font-bold">1 Mesaj</span>
              </div>
              <div class="flex items-center justify-between text-slate-400">
                <span>API Havuzu:</span>
                <span class="font-mono text-emerald-400 font-bold">136 Anahtar</span>
              </div>
              <button onclick="startNewChatSession()" class="w-full py-1.5 px-2 rounded-lg bg-gold-500/15 hover:bg-gold-500/25 text-gold-300 border border-gold-500/30 text-[10px] font-bold transition flex items-center justify-center gap-1 shadow-sm">
                <i data-lucide="plus" class="w-3 h-3"></i> Yeni Sohbet Aç
              </button>
            </div>

          </div>"""

content, count2 = sidebar_pattern.subn(sidebar_replacement, content)
print(f"Sidebar replaced: {count2} times")

# 3. Update the chat header title & description
header_title_pattern = re.compile(
    r'<span id="activeChannelTitle"[^>]*>.*?</span>\s*<span id="activeChannelBadge"[^>]*>.*?</span>\s*</div>\s*<p id="activeChannelDesc"[^>]*>.*?</p>',
    re.DOTALL
)
header_title_replacement = """<span id="activeChannelTitle" class="font-bold text-sm text-gold-400">Başyönetmen Selim Bey</span>
                <span id="activeChannelBadge" class="text-[10px] font-mono px-2 py-0.5 rounded bg-gold-500/15 text-gold-300 border border-gold-500/30">Tüm Yetkinlikler Kuşanıldı</span>
              </div>
              <p id="activeChannelDesc" class="text-[10px] text-slate-400 truncate max-w-[340px]">Asla unutulmayan kalıcı hafıza • Canlı Gemini API ile doğal diyalog</p>"""

content, count3 = header_title_pattern.subn(header_title_replacement, content)
print(f"Header title replaced: {count3} times")

# 4. Update the quick chips
chips_pattern = re.compile(
    r'<div id="quickChipsBar".*?</div>\s*<!-- Sohbet Mesajları',
    re.DOTALL
)
chips_replacement = """<div id="quickChipsBar" class="flex items-center gap-1.5 pb-2 overflow-x-auto no-scrollbar border-b border-slate-800/60 text-[11px]">
              <span class="text-slate-500 text-[10px] whitespace-nowrap">Hızlı Fikirler:</span>
              <button onclick="sendQuickPrompt('Bana çarpıcı bir İslami tefekkür konusu öner.')" class="px-2 py-0.5 rounded-full bg-gold-500/10 hover:bg-gold-500/20 text-gold-300 border border-gold-500/20 whitespace-nowrap transition">💡 Konu Öner</button>
              <button onclick="sendQuickPrompt('Nemrut ve Firavun\\'un kibrinin yıkılışı üzerine 50 saniyelik bir video kurgulayalım.')" class="px-2 py-0.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 whitespace-nowrap transition">🏛️ Nemrut & Firavun</button>
              <button onclick="sendQuickPrompt('Kün Fe Yekûn: Kâinattaki İlahi Kudret ve Mâtürîdî İtikadı üzerine kurgulayalım.')" class="px-2 py-0.5 rounded-full bg-slate-800 hover:bg-slate-700 text-slate-300 border border-slate-700 whitespace-nowrap transition">🌌 Kün Fe Yekûn</button>
              <button onclick="sendQuickPrompt('Bu senaryoya Turso havuzumuzdan hangi derviş veya hatip sesi en uygun?')" class="px-2 py-0.5 rounded-full bg-purple-500/15 hover:bg-purple-500/25 text-purple-300 border border-purple-500/30 whitespace-nowrap transition">🎙️ Turso Sesi Seç</button>
              <button onclick="sendQuickPrompt('Remotion tipografi ve sahne geçiş kodlarını planlayalım.')" class="px-2 py-0.5 rounded-full bg-amber-500/15 hover:bg-amber-500/25 text-amber-300 border border-amber-500/30 whitespace-nowrap transition">🎬 Remotion Kurgu</button>
            </div>

            <!-- Sohbet Mesajları"""

content, count4 = chips_pattern.subn(chips_replacement, content)
print(f"Quick chips replaced: {count4} times")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("HTML DOM updates written successfully!")
