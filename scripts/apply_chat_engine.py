import os
import re

INDEX_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "web", "index.html"))

with open(INDEX_PATH, "r", encoding="utf-8") as f:
    content = f.read()

# Pattern matching from // Uygulama Başlatma down to function clearCurrentChannelUI() { ... }
pattern = re.compile(
    r'// Uygulama Başlatma\s*document\.addEventListener\(\'DOMContentLoaded\'.*?function clearCurrentChannelUI\(\)\s*\{[^}]*\}',
    re.DOTALL
)

replacement = """// Uygulama Başlatma
    document.addEventListener('DOMContentLoaded', () => {
      lucide.createIcons();
      initWaveSurfer();
      initErrorStore();
      loadKeyPoolStatus();
      loadState();
      loadAudioLibrary();
      loadDirectorStatus();
      loadChatHistory();
    });

    // ===============================================================
    // BAŞYÖNETMEN SELİM BEY - CANLI GEMİNİ MOTORU & KALICI HAFIZA
    // ===============================================================

    let currentActiveWardrobe = "Başyönetmen (Tüm Yetkinlikler)";

    async function loadDirectorStatus() {
      try {
        const res = await fetch('/api/director/status');
        if (!res.ok) return;
        const data = await res.json();
        currentActiveWardrobe = data.active_wardrobe || currentActiveWardrobe;
        
        const sideWardrobe = document.getElementById('sideActiveWardrobe');
        if (sideWardrobe) sideWardrobe.innerText = currentActiveWardrobe;

        const apiBadge = document.getElementById('directorApiBadge');
        if (apiBadge && data.last_model_used) {
          apiBadge.innerHTML = `<span class="w-1.5 h-1.5 rounded-full bg-emerald-400"></span> Canlı ${data.last_model_used}`;
        }
      } catch (e) {
        console.warn('Director status yüklenemedi:', e);
      }
    }

    async function loadChatHistory() {
      const feed = document.getElementById('logFeed');
      if (!feed) return;

      try {
        const res = await fetch('/api/chat/history');
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        const history = data.history || [];

        feed.innerHTML = '';
        history.forEach(m => {
          appendMessageBubbleToFeed(m, false);
        });

        const badge = document.getElementById('logCountBadge');
        if (badge) badge.innerText = `${history.length} Mesaj`;

        const sideCount = document.getElementById('sideHistoryCount');
        if (sideCount) sideCount.innerText = `${history.length} Mesaj`;

        if (data.director_status) {
          currentActiveWardrobe = data.director_status.active_wardrobe || currentActiveWardrobe;
          const sideWardrobe = document.getElementById('sideActiveWardrobe');
          if (sideWardrobe) sideWardrobe.innerText = currentActiveWardrobe;
        }

        feed.scrollTop = feed.scrollHeight;
        lucide.createIcons();
      } catch (e) {
        console.error('Sohbet geçmişi yüklenemedi:', e);
      }
    }

    function formatMarkdown(text) {
      if (!text) return '';
      let html = text
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;');

      // Code blocks ```code```
      html = html.replace(/```([a-zA-Z]*)\\n([\\s\\S]*?)```/g, (match, lang, code) => {
        return `<pre class="my-2 p-2.5 rounded-lg bg-obsidian-950 border border-slate-700 text-gold-300 font-mono text-[11px] overflow-x-auto whitespace-pre"><code>${code}</code></pre>`;
      });

      // Inline code `code`
      html = html.replace(/`([^`]+)`/g, '<code class="px-1.5 py-0.5 rounded bg-obsidian-900 text-gold-300 font-mono text-[11px] border border-slate-700">$1</code>');

      // Bold **text**
      html = html.replace(/\\*\\*([^*]+)\\*\\*/g, '<strong class="text-gold-300 font-semibold">$1</strong>');

      // Italic *text*
      html = html.replace(/\\*([^*]+)\\*/g, '<em class="text-slate-300 italic">$1</em>');

      // Line breaks
      html = html.replace(/\\n/g, '<br/>');

      return html;
    }

    function appendMessageBubbleToFeed(m, shouldScroll = true) {
      const feed = document.getElementById('logFeed');
      if (!feed) return;

      const isUser = m.role === 'user' || m.sender_id === 'user';
      const item = document.createElement('div');

      if (isUser) {
        item.className = 'p-3 rounded-xl bg-obsidian-900/90 border border-slate-700 ml-6 text-xs space-y-1 shadow-sm';
        item.innerHTML = `
          <div class="flex items-center justify-between text-[10px] text-slate-400 mb-0.5">
            <span class="text-sky-400 font-bold flex items-center gap-1"><span>👤</span> ${m.sender_name || 'Sayın Yönetmenimiz'}</span>
            <span class="font-mono text-slate-500">${m.timestamp || ''}</span>
          </div>
          <div class="text-slate-100 leading-relaxed">${formatMarkdown(m.message)}</div>
        `;
      } else {
        const wardrobe = m.wardrobe || currentActiveWardrobe || 'Başyönetmen (Tüm Yetkinlikler)';
        const modelBadge = m.badge || 'BAŞYÖNETMEN';

        const hasScriptLines = /\\d+\\.\\s+[^\\n]+/.test(m.message);

        let scriptActionHtml = '';
        if (hasScriptLines) {
          scriptActionHtml = `
            <div class="pt-2 border-t border-gold-500/20 flex justify-end">
              <button onclick="loadMessageScriptToStudio(this)" 
                      class="px-2.5 py-1.5 rounded-lg bg-gold-500/20 hover:bg-gold-500/30 text-gold-300 border border-gold-500/40 text-[11px] font-bold flex items-center gap-1.5 transition shadow">
                <span>📋</span> <span>Bu Senaryoyu Pre-Render'a Aktar</span>
              </button>
            </div>
          `;
        }

        item.className = 'p-3.5 rounded-xl bg-obsidian-950/95 border-l-4 border-l-gold-500 border-y border-r border-slate-800 text-xs space-y-2 shadow-lg animate-fade-in transition-all';
        item.dataset.rawMessage = m.message;
        item.innerHTML = `
          <div class="flex items-center justify-between text-[11px] text-slate-400 pb-1 border-b border-slate-800/60">
            <span class="font-bold flex items-center gap-1.5 text-slate-200">
              <span class="text-base">🎬</span>
              <span class="text-gold-400 font-display">Başyönetmen Selim Bey</span>
              <span class="text-[10px] font-mono px-1.5 py-0.2 rounded bg-gold-500/10 text-gold-400 border border-gold-500/20">${wardrobe}</span>
            </span>
            <span class="font-mono text-slate-500 text-[10px]">${m.timestamp || ''}</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="inline-block text-[10px] font-mono px-2 py-0.5 rounded bg-slate-800 text-gold-300 border border-slate-700/80 shadow-sm">${modelBadge}</span>
          </div>
          <div class="text-slate-200 leading-relaxed text-xs font-normal selection:bg-gold-500/30 break-words message-content">
            ${formatMarkdown(m.message)}
          </div>
          ${scriptActionHtml}
        `;
      }

      feed.appendChild(item);
      if (shouldScroll) {
        feed.scrollTop = feed.scrollHeight;
      }

      const badge = document.getElementById('logCountBadge');
      if (badge) badge.innerText = `${feed.children.length} Mesaj`;
      const sideCount = document.getElementById('sideHistoryCount');
      if (sideCount) sideCount.innerText = `${feed.children.length} Mesaj`;
    }

    async function sendChatMessage() {
      const input = document.getElementById('chatInput');
      const text = input.value.trim();
      if (!text) return;

      input.value = '';
      const nowStr = new Date().toLocaleTimeString();

      const userEntry = {
        role: 'user',
        timestamp: nowStr,
        sender_id: 'user',
        sender_name: 'Sayın Yönetmenimiz',
        receiver_name: 'Başyönetmen Selim Bey',
        badge: 'YÖNETMEN TALİMATI',
        wardrobe: currentActiveWardrobe,
        message: text
      };

      appendMessageBubbleToFeed(userEntry, true);

      const workingBar = document.getElementById('agentWorkingBar');
      const workingText = document.getElementById('agentWorkingText');
      const activeModelTag = document.getElementById('activeModelTag');

      if (workingText) workingText.innerText = 'Başyönetmen Selim Bey canlı Gemini API üzerinden derinlemesine düşünüyor...';
      if (activeModelTag) activeModelTag.innerText = currentActiveModel;
      if (workingBar) workingBar.classList.remove('hidden');

      const sendBtn = document.getElementById('btnSendChat');
      if (sendBtn) sendBtn.disabled = true;

      try {
        const res = await fetch('/api/chat/message', {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify({
            message: text,
            model: currentActiveModel
          })
        });

        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: Sunucu yanıt vermedi`);
        }

        const data = await res.json();
        if (workingBar) workingBar.classList.add('hidden');

        if (data.active_wardrobe) {
          currentActiveWardrobe = data.active_wardrobe;
          const sideWardrobe = document.getElementById('sideActiveWardrobe');
          if (sideWardrobe) sideWardrobe.innerText = currentActiveWardrobe;
        }

        const replyEntry = {
          role: 'model',
          timestamp: new Date().toLocaleTimeString(),
          sender_id: '01_basyonetmen',
          sender_name: 'Başyönetmen Selim Bey',
          receiver_name: 'Sayın Yönetmenimiz',
          badge: `DERİN DÜŞÜNCE [${data.model_used || currentActiveModel}]`,
          wardrobe: data.active_wardrobe || currentActiveWardrobe,
          message: data.reply
        };

        appendMessageBubbleToFeed(replyEntry, true);

        if (data.suggested_topic) {
          const topicInput = document.getElementById('topicInput');
          if (topicInput) topicInput.value = data.suggested_topic;
        }

      } catch (e) {
        if (workingBar) workingBar.classList.add('hidden');
        logSystemError({
          error_type: 'CHAT_REQUEST_ERROR',
          step: 'Başyönetmen İstişaresi',
          model: currentActiveModel,
          agent_id: '01_basyonetmen',
          message: `Mesaj iletilemedi: ${e.message || e}`,
          traceback: String(e.stack || e)
        });
        alert('Canlı istişare bağlantısında bir sorun oluştu: ' + e);
      } finally {
        if (sendBtn) sendBtn.disabled = false;
        lucide.createIcons();
      }
    }

    async function startNewChatSession() {
      if (!confirm('Mevcut sohbet oturumu arşive kaldırılacak ve temiz yeni bir istişare oturumu başlatılacak. Onaylıyor musunuz?')) {
        return;
      }
      try {
        const res = await fetch('/api/chat/new', { method: 'POST' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        await loadChatHistory();
        await loadDirectorStatus();
      } catch (e) {
        alert('Yeni sohbet başlatılamadı: ' + e);
      }
    }

    async function clearChatHistoryConfirm() {
      if (!confirm('Sohbet geçmişi ve tüm konuşmalar tamamen silinecek. Emin misiniz?')) {
        return;
      }
      try {
        const res = await fetch('/api/chat/clear', { method: 'POST' });
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        await loadChatHistory();
        await loadDirectorStatus();
      } catch (e) {
        alert('Sohbet silinemedi: ' + e);
      }
    }

    function wearWardrobePrompt(wardrobeName) {
      currentActiveWardrobe = wardrobeName;
      const sideWardrobe = document.getElementById('sideActiveWardrobe');
      if (sideWardrobe) sideWardrobe.innerText = wardrobeName;

      const input = document.getElementById('chatInput');
      if (input) {
        input.value = `Selim Bey, "${wardrobeName}" elbiseni kuşanarak şu konuyu ele alalım: `;
        input.focus();
      }
    }

    function loadMessageScriptToStudio(btn) {
      const parent = btn.closest('[data-raw-message]');
      if (!parent) return;
      const rawText = parent.dataset.rawMessage;

      const lines = [];
      const rawLines = rawText.split('\\n');
      for (const line of rawLines) {
        const trimmed = line.trim();
        const match = trimmed.match(/^\\d+[\\.\\)]\\s*(?:\\*\\*)?(.*?)(?:\\*\\*)?$/);
        if (match && match[1].length > 5) {
          lines.push(match[1].trim());
        }
      }

      const scriptEditor = document.getElementById('scriptEditor');
      if (scriptEditor) {
        if (lines.length > 0) {
          scriptEditor.value = lines.join('\\n');
        } else {
          scriptEditor.value = rawText;
        }
        updateScenesCount();
        alert('Senaryo başarıyla Pre-Render Masası metin editörüne yüklendi!');
        switchPreRenderTab('script');
      }
    }"""

content, count = pattern.subn(lambda m: replacement, content)
print(f"Chat JS replaced: {count} times")

with open(INDEX_PATH, "w", encoding="utf-8") as f:
    f.write(content)

print("index.html JS updated successfully!")
