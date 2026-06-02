/**
 * AI Chat System - Enhanced UX Edition
 * @version 4.0.0
 *
 * Features:
 * 1. Visual Quick Reply Cards
 * 2. Smart context-aware loading messages
 * 3. Typewriter / chunk streaming effect
 * 4. Live Content Item Panel with animated updates
 * 5. Markdown rendering
 * 6. Post-generation action buttons
 */

// ─── Lightweight Markdown Parser ────────────────────────────────────────────
const MD = {
    parse(text) {
        if (!text) return '';
        let html = text
            // escape HTML entities first
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;');

        // headings
        html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
        html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');
        html = html.replace(/^# (.+)$/gm, '<h1>$1</h1>');

        // bold & italic
        html = html.replace(/\*\*\*(.+?)\*\*\*/g, '<strong><em>$1</em></strong>');
        html = html.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/\*(.+?)\*/g, '<em>$1</em>');

        // inline code
        html = html.replace(/`([^`]+)`/g, '<code>$1</code>');

        // blockquote
        html = html.replace(/^&gt; (.+)$/gm, '<blockquote>$1</blockquote>');

        // unordered lists
        html = html.replace(/^[-•] (.+)$/gm, '<li>$1</li>');
        html = html.replace(/(<li>.*<\/li>)/gs, '<ul>$1</ul>');

        // ordered lists
        html = html.replace(/^\d+\. (.+)$/gm, '<li>$1</li>');

        // horizontal rule
        html = html.replace(/^---+$/gm, '<hr>');

        // line breaks → paragraphs
        html = html
            .split(/\n{2,}/)
            .map(block => {
                if (/^<(h[1-3]|ul|ol|li|blockquote|hr)/.test(block.trim())) return block;
                return `<p>${block.replace(/\n/g, '<br>')}</p>`;
            })
            .join('\n');

        // clean up empty <p> and nested list issues
        html = html.replace(/<p>\s*<\/p>/g, '');
        html = html.replace(/<ul>(<li>[\s\S]*?<\/li>)<\/ul>\s*<ul>/g, '<ul>$1');

        return html;
    }
};

// ─── Stage-aware loading messages ───────────────────────────────────────────
const LOADING_MESSAGES = {
    greeting:           ['در حال آماده‌سازی...', 'دستیار در حال تفکر است...'],
    platform_selection: ['در حال تحلیل پلتفرم...', 'بررسی بهترین رویکرد...'],
    goal_selection:     ['در حال بررسی اهداف...', 'تحلیل استراتژی محتوا...'],
    content_details:    ['در حال پردازش اطلاعات...', 'استخراج جزئیات محتوا...'],
    research:           ['در حال جستجو در منابع...', 'تحلیل داده‌های مرتبط...', 'یافتن بهترین منابع...'],
    final_confirmation: ['بررسی اطلاعات نهایی...', 'آماده‌سازی برای تولید...'],
    content_generation: ['در حال نوشتن محتوا...', 'خلاقیت در جریان است...', 'تولید محتوای حرفه‌ای...', 'بهینه‌سازی متن...'],
    completed:          ['در حال بارگذاری...'],
    default:            ['در حال پردازش...', 'لطفاً منتظر بمانید...'],
};

// ─── Platform metadata ───────────────────────────────────────────────────────
const PLATFORM_META = {
    instagram: { icon: '📸', label: 'اینستاگرام', color: '#E1306C' },
    linkedin:  { icon: '💼', label: 'لینکدین',    color: '#0077B5' },
    telegram:  { icon: '✈️', label: 'تلگرام',     color: '#0088CC' },
    twitter:   { icon: '🐦', label: 'توییتر',     color: '#1DA1F2' },
    facebook:  { icon: '👥', label: 'فیسبوک',     color: '#1877F2' },
    website:   { icon: '🌐', label: 'وب‌سایت',    color: '#10B981' },
    youtube:   { icon: '▶️', label: 'یوتیوب',     color: '#FF0000' },
    blog:      { icon: '📝', label: 'وبلاگ',      color: '#F59E0B' },
};

// ─── Post-generation variant actions ────────────────────────────────────────
const CONTENT_VARIANTS = [
    { label: '😊 دوستانه‌تر',     value: 'محتوا را دوستانه‌تر و صمیمی‌تر بنویس' },
    { label: '👔 رسمی‌تر',        value: 'محتوا را رسمی‌تر و حرفه‌ای‌تر بنویس' },
    { label: '✂️ کوتاه‌تر',       value: 'محتوا را خلاصه‌تر و کوتاه‌تر بنویس' },
    { label: '📱 نسخه اینستاگرام', value: 'یک نسخه مناسب اینستاگرام با هشتگ بنویس' },
    { label: '✈️ نسخه تلگرام',    value: 'یک نسخه مناسب کانال تلگرام بنویس' },
    { label: '💼 نسخه لینکدین',   value: 'یک نسخه حرفه‌ای برای لینکدین بنویس' },
    { label: '🔥 جذاب‌تر',        value: 'محتوا را با Hook قوی‌تر و جذاب‌تر بنویس' },
    { label: '📋 کپی متن',        value: null, action: 'copy' },
];

// ─── Main AIChat Class ───────────────────────────────────────────────────────
class AIChat {

    constructor() {
        this.state = {
            sessionId: null,
            contentItemId: null,
            campaignId: null,
            isProcessing: false,
            retryCount: 0,
            currentStage: 'greeting',
            contentData: {},
        };

        this.config = {
            maxRetries: 3,
            retryDelay: 2000,
            maxMessageLength: 2000,
            autoSaveInterval: 30000,
            storageKey: 'ai_chat_state_v4',
            typewriterSpeed: 8,   // ms per character
            typewriterChunk: 4,   // characters per tick
        };

        this.endpoints = {
            sendMessage:    '/content/api/v1/ai/chat/send/',
            generateImage:  '/content/api/v1/ai/generate-image/',
            sessionHistory: (id) => `/content/api/v1/ai/session/${id}/history/`,
            newConversation:'/content/api/v1/ai/chat/new/',
            campaigns:      '/campaign/api/v1/campaign_list',
            contentDetail:  (id) => `/content/api/v1/content/${id}/`,
        };

        this.elements = {};
        this.loadingInterval = null;
        this.tempImageData = null;

        this._bindElements();

        if (!this._validateElements()) {
            console.error('❌ Required DOM elements not found');
            return;
        }

        this.init();
    }

    _bindElements() {
        const ids = [
            'chatWindow','chatMessages','chatInput','sendBtn',
            'generateImageBtn','typingIndicator','welcomeMessage',
            'contentDetails','historyList','sessionStatus','newChatBtn',
            'campaignSelect','platformSelect','charCount','refreshHistoryBtn',
            'exportChatBtn','confirmModal','confirmNewChat','cancelNewChat',
            'toast','toastMessage','imageGeneratorModal','imagePrompt',
            'imageSize','promptCharCount','generateImageSubmit',
            'cancelImageGeneration','closeImageModal','imagePreview',
            'generatedImage','downloadImage','insertImageToChat',
        ];
        ids.forEach(id => { this.elements[id] = document.getElementById(id); });
    }

    _validateElements() {
        return ['chatMessages','chatInput','sendBtn','chatWindow']
            .every(k => !!this.elements[k]);
    }

    // =========================================================
    // INIT
    // =========================================================

    async init() {
        try {
            console.log('🚀 AI Chat v4.0 initializing...');
            this._loadState();
            this._bindEvents();
            await this._loadCampaigns();

            if (this.state.sessionId) {
                await this._loadSessionHistory();
                this._updateStatus('بازیابی شده');
            } else {
                this._showWelcome();
                this._updateStatus('آماده دریافت پیام');
            }

            if (this.state.contentItemId) {
                await this._refreshContentPanel();
            }

            this.elements.chatInput?.focus();
            this._startAutoSave();
            console.log('✅ Initialized');
        } catch (err) {
            console.error('❌ Init error:', err);
            this._toast('خطا در بارگذاری سیستم', 'error');
        }
    }

    // =========================================================
    // EVENTS
    // =========================================================

    _bindEvents() {
        const el = this.elements;

        el.sendBtn?.addEventListener('click', () => this.sendMessage());

        el.chatInput?.addEventListener('keydown', e => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        el.chatInput?.addEventListener('input', () => {
            this._updateCharCounter();
            this._autoResizeTextarea();
        });

        el.generateImageBtn?.addEventListener('click', () => this._openImageModal());

        document.querySelectorAll('.example-btn').forEach(btn => {
            btn.addEventListener('click', e => {
                const msg = e.currentTarget.dataset.message;
                if (msg && el.chatInput) {
                    el.chatInput.value = msg;
                    this._updateCharCounter();
                    this.sendMessage();
                }
            });
        });

        el.newChatBtn?.addEventListener('click', () => this._showNewChatModal());
        el.confirmNewChat?.addEventListener('click', () => this._startNewConversation());
        el.cancelNewChat?.addEventListener('click', () => this._hideModal());
        el.confirmModal?.addEventListener('click', e => {
            if (e.target === el.confirmModal) this._hideModal();
        });

        el.refreshHistoryBtn?.addEventListener('click', () => {
            if (this.state.sessionId) this._loadSessionHistory();
        });

        el.exportChatBtn?.addEventListener('click', () => this._exportChat());

        // Image modal
        el.imagePrompt?.addEventListener('input', () => {
            if (el.promptCharCount) el.promptCharCount.textContent = el.imagePrompt.value.length;
        });
        el.generateImageSubmit?.addEventListener('click', () => this._generateImage());
        el.cancelImageGeneration?.addEventListener('click', () => this._closeImageModal());
        el.closeImageModal?.addEventListener('click', () => this._closeImageModal());
        el.imageGeneratorModal?.addEventListener('click', e => {
            if (e.target === el.imageGeneratorModal) this._closeImageModal();
        });
        el.downloadImage?.addEventListener('click', () => this._downloadImage());
        el.insertImageToChat?.addEventListener('click', () => this._insertImageToChat());

        el.campaignSelect?.addEventListener('change', e => {
            this.state.campaignId = parseInt(e.target.value) || null;
            this._saveState();
            this._toast('کمپین انتخاب شد', 'success');
        });

        window.addEventListener('beforeunload', e => {
            if (this.state.isProcessing) {
                e.preventDefault();
                e.returnValue = '';
            }
        });
    }

    // =========================================================
    // SEND MESSAGE  ← core flow
    // =========================================================

    async sendMessage() {
        const message = this.elements.chatInput?.value.trim();
        if (!message) return;
        if (this.state.isProcessing) { this._toast('لطفاً منتظر پاسخ قبلی بمانید', 'warning'); return; }
        if (message.length > this.config.maxMessageLength) { this._toast('پیام خیلی طولانی است', 'error'); return; }

        if (!this.state.sessionId && !this.state.campaignId) {
            this._toast('لطفاً ابتدا یک کمپین انتخاب کنید', 'warning');
            this.elements.campaignSelect?.focus();
            return;
        }

        const platform = this.elements.platformSelect?.value;
        if (!platform) {
            this._toast('لطفاً پلتفرم را انتخاب کنید', 'warning');
            this.elements.platformSelect?.focus();
            return;
        }

        this._hideWelcome();
        this._addUserMessage(message);

        if (this.elements.chatInput) this.elements.chatInput.value = '';
        this._updateCharCounter();
        this._autoResizeTextarea();

        this._setProcessing(true);

        try {
            const response = await this._callAPI(message, platform);

            if (!response?.message) throw new Error('پاسخ نامعتبر از سرور');

            this._updateStateFromResponse(response);

            // Decide rendering mode
            const isLongContent = response.message.length > 300;
            const isGenerated   = response.stage === 'completed' || isLongContent;

            if (isGenerated) {
                await this._addAIMessageTypewriter(response.message, response);
                this._renderPostGenerationActions(response.message);
            } else {
                this._addAIMessage(response.message, response);
            }

            // quick replies as cards
            if (response.quick_replies?.length) {
                this._renderQuickReplyCards(response.quick_replies);
            }

            this._saveState();
            this._updateStatus('آماده دریافت پیام');

            // refresh content panel
            if (this.state.contentItemId) {
                await this._refreshContentPanel();
            }

        } catch (err) {
            console.error('❌ sendMessage error:', err);
            this._addErrorMessage();
        } finally {
            this._setProcessing(false);
            this.elements.chatInput?.focus();
        }
    }

    async _callAPI(message, platform) {
        const payload = {
            message,
            session_id:      this.state.sessionId,
            content_item_id: this.state.contentItemId,
            campaign_id:     this.state.campaignId,
            platform,
        };
        const res = await fetch(this.endpoints.sendMessage, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this._csrf(),
            },
            body: JSON.stringify(payload),
        });
        if (!res.ok) {
            const err = await res.json().catch(() => ({}));
            throw new Error(err.error || `HTTP ${res.status}`);
        }
        return res.json();
    }

    _updateStateFromResponse(response) {
        if (response.session_id)      this.state.sessionId      = response.session_id;
        if (response.content_item_id) this.state.contentItemId  = response.content_item_id;
        if (response.stage)           this.state.currentStage   = response.stage;
        if (response.content_item)    this.state.contentData    = response.content_item;
    }

    // =========================================================
    // MESSAGE RENDERING
    // =========================================================

    _addUserMessage(text) {
        const el = this._createMessageShell('user');
        const content = el.querySelector('.message-content');
        content.textContent = text;
        this.elements.chatMessages.appendChild(el);
        requestAnimationFrame(() => el.classList.add('message-show'));
        this._scrollBottom();
        return el;
    }

    _addAIMessage(text, response = {}) {
        const el = this._createMessageShell('assistant');
        const content = el.querySelector('.message-content');
        content.innerHTML = MD.parse(text);
        this.elements.chatMessages.appendChild(el);
        requestAnimationFrame(() => el.classList.add('message-show'));
        this._scrollBottom();
        return el;
    }

    async _addAIMessageTypewriter(text, response = {}) {
        const el = this._createMessageShell('assistant');
        el.classList.add('message-generating');
        const content = el.querySelector('.message-content');
        content.innerHTML = '';

        // cursor element
        const cursor = document.createElement('span');
        cursor.className = 'typewriter-cursor';
        cursor.textContent = '▋';
        content.appendChild(cursor);

        this.elements.chatMessages.appendChild(el);
        requestAnimationFrame(() => el.classList.add('message-show'));

        // Build final HTML, but type raw text then render at end
        const chars = text.split('');
        let displayed = '';
        const speed = this.config.typewriterSpeed;
        const chunk = this.config.typewriterChunk;

        await new Promise(resolve => {
            let i = 0;
            const tick = () => {
                if (i >= chars.length) {
                    // final render with full markdown
                    content.innerHTML = MD.parse(text);
                    el.classList.remove('message-generating');
                    resolve();
                    return;
                }
                for (let c = 0; c < chunk && i < chars.length; c++, i++) {
                    displayed += chars[i];
                }
                // lightweight partial render: just plain text with cursor
                content.textContent = displayed;
                const cur = document.createElement('span');
                cur.className = 'typewriter-cursor';
                cur.textContent = '▋';
                content.appendChild(cur);
                this._scrollBottom();
                setTimeout(tick, speed);
            };
            tick();
        });

        this._scrollBottom();
        return el;
    }

    _addErrorMessage() {
        const el = this._createMessageShell('assistant');
        el.classList.add('message-error');
        const content = el.querySelector('.message-content');
        content.innerHTML = '⚠️ متأسفانه خطایی رخ داد. لطفاً دوباره تلاش کنید.';
        this.elements.chatMessages.appendChild(el);
        requestAnimationFrame(() => el.classList.add('message-show'));
        this._scrollBottom();
    }

    _createMessageShell(role) {
        const wrap = document.createElement('div');
        wrap.className = `message message-${role}`;

        const avatar = document.createElement('div');
        avatar.className = 'message-avatar';
        avatar.textContent = role === 'user' ? '👤' : '🤖';

        const inner = document.createElement('div');
        inner.className = 'message-wrapper';

        const content = document.createElement('div');
        content.className = 'message-content';
        inner.appendChild(content);

        const time = document.createElement('div');
        time.className = 'message-time';
        time.textContent = this._formatTime(new Date());
        inner.appendChild(time);

        wrap.appendChild(avatar);
        wrap.appendChild(inner);
        return wrap;
    }

    // =========================================================
    // QUICK REPLY CARDS  (Feature 1)
    // =========================================================

    _renderQuickReplyCards(quickReplies) {
        const existing = this.elements.chatMessages.querySelector('.quick-replies-container:last-child');
        if (existing) existing.remove();

        const container = document.createElement('div');
        container.className = 'quick-replies-container';

        quickReplies.forEach(reply => {
            const card = document.createElement('button');
            card.className = 'quick-reply-card';
            card.dataset.value = reply.value;

            // detect if it's a platform card
            const platform = Object.entries(PLATFORM_META).find(([k]) =>
                reply.value?.toLowerCase().includes(k) || reply.label?.includes(PLATFORM_META[k]?.label)
            );

            if (platform) {
                const [key, meta] = platform;
                card.style.setProperty('--card-accent', meta.color);
                card.innerHTML = `<span class="qr-icon">${meta.icon}</span><span class="qr-label">${reply.label}</span>`;
            } else {
                card.innerHTML = `<span class="qr-label">${reply.label}</span>`;
            }

            card.addEventListener('click', () => {
                // remove all quick reply containers
                this.elements.chatMessages.querySelectorAll('.quick-replies-container').forEach(el => el.remove());
                // send as message
                if (this.elements.chatInput) {
                    this.elements.chatInput.value = reply.value;
                    this._updateCharCounter();
                    this.sendMessage();
                }
            });

            container.appendChild(card);
        });

        this.elements.chatMessages.appendChild(container);
        this._scrollBottom();
    }

    // =========================================================
    // POST-GENERATION ACTIONS  (Feature 6)
    // =========================================================

    _renderPostGenerationActions(originalText) {
        const container = document.createElement('div');
        container.className = 'post-gen-actions';

        const label = document.createElement('p');
        label.className = 'post-gen-label';
        label.textContent = '✨ ویرایش سریع:';
        container.appendChild(label);

        const btnRow = document.createElement('div');
        btnRow.className = 'post-gen-buttons';

        CONTENT_VARIANTS.forEach(variant => {
            const btn = document.createElement('button');
            btn.className = 'post-gen-btn';
            btn.textContent = variant.label;

            if (variant.action === 'copy') {
                btn.addEventListener('click', () => {
                    navigator.clipboard.writeText(originalText).then(() => {
                        btn.textContent = '✅ کپی شد!';
                        setTimeout(() => { btn.textContent = variant.label; }, 2000);
                    });
                });
            } else {
                btn.addEventListener('click', () => {
                    container.remove();
                    if (this.elements.chatInput) {
                        this.elements.chatInput.value = variant.value;
                        this._updateCharCounter();
                        this.sendMessage();
                    }
                });
            }

            btnRow.appendChild(btn);
        });

        container.appendChild(btnRow);
        this.elements.chatMessages.appendChild(container);
        this._scrollBottom();
    }

    // =========================================================
    // TYPING INDICATOR  (Feature 2 — smart loading messages)
    // =========================================================

    _setProcessing(flag) {
        this.state.isProcessing = flag;
        if (flag) {
            this._startSmartLoading();
        } else {
            this._stopLoading();
        }
    }

    _startSmartLoading() {
        const indicator = this.elements.typingIndicator;
        if (!indicator) return;

        const stage = this.state.currentStage || 'default';
        const messages = LOADING_MESSAGES[stage] || LOADING_MESSAGES.default;

        let idx = 0;
        const textEl = indicator.querySelector('.typing-text');

        const update = () => {
            if (textEl) textEl.textContent = messages[idx % messages.length];
            idx++;
        };

        update();
        indicator.style.display = 'flex';
        this.loadingInterval = setInterval(update, 1800);
    }

    _stopLoading() {
        const indicator = this.elements.typingIndicator;
        if (indicator) indicator.style.display = 'none';
        if (this.loadingInterval) {
            clearInterval(this.loadingInterval);
            this.loadingInterval = null;
        }
    }

    // =========================================================
    // CONTENT PANEL  (Feature 4 — live updating)
    // =========================================================

    async _refreshContentPanel() {
        if (!this.state.contentItemId) {
            this._renderContentPanel(null);
            return;
        }
        try {
            const res = await fetch(this.endpoints.contentDetail(this.state.contentItemId));
            if (!res.ok) throw new Error('fetch failed');
            const data = await res.json();
            this.state.contentData = data;
            this._renderContentPanel(data);
        } catch (err) {
            // use cached state data if available
            if (Object.keys(this.state.contentData).length) {
                this._renderContentPanel(this.state.contentData);
            }
        }
    }

    _renderContentPanel(data) {
        const panel = this.elements.contentDetails;
        if (!panel) return;

        if (!data) {
            panel.innerHTML = `
                <p class="empty-state">
                    <span class="empty-icon">💬</span>
                    هنوز محتوایی ایجاد نشده
                </p>`;
            return;
        }

        const platform = data.platform || '';
        const meta = PLATFORM_META[platform] || { icon: '📄', label: platform, color: '#6366F1' };
        const metadata = data.metadata || {};

        const fields = [
            { key: 'platform',        icon: meta.icon,  label: 'پلتفرم',       value: meta.label || platform },
            { key: 'goal',            icon: '🎯',        label: 'هدف',          value: data.goal },
            { key: 'title',           icon: '📌',        label: 'عنوان',        value: data.title !== 'محتوای جدید' ? data.title : null },
            { key: 'target_audience', icon: '👥',        label: 'مخاطب',        value: metadata.target_audience },
            { key: 'tone',            icon: '🎭',        label: 'لحن',          value: metadata.tone },
            { key: 'main_keyword',    icon: '🔑',        label: 'کلمه کلیدی',   value: data.main_keyword },
            { key: 'status',          icon: '📊',        label: 'وضعیت',        value: this._statusLabel(data.status) },
        ].filter(f => f.value && f.value.trim && f.value.trim() !== '');

        const completedCount = fields.filter(f => f.value).length;
        const totalRequired = 5;
        const pct = Math.min(100, Math.round((completedCount / totalRequired) * 100));

        panel.innerHTML = `
            <div class="content-panel-inner">
                <div class="cp-progress-row">
                    <span class="cp-progress-label">تکمیل اطلاعات</span>
                    <span class="cp-progress-pct">${pct}٪</span>
                </div>
                <div class="cp-progress-bar">
                    <div class="cp-progress-fill" style="width:${pct}%"></div>
                </div>

                <ul class="cp-fields">
                    ${fields.map(f => `
                        <li class="cp-field cp-field-enter">
                            <span class="cp-field-icon">${f.icon}</span>
                            <div class="cp-field-info">
                                <span class="cp-field-label">${f.label}</span>
                                <span class="cp-field-value">${f.value}</span>
                            </div>
                        </li>
                    `).join('')}
                </ul>
            </div>`;

        // stagger animation
        panel.querySelectorAll('.cp-field-enter').forEach((el, i) => {
            el.style.animationDelay = `${i * 60}ms`;
        });
    }

    _statusLabel(status) {
        const map = {
            draft:            'پیش‌نویس',
            research_done:    'تحقیق انجام شد',
            research_skipped: 'بدون تحقیق',
            generating:       'در حال تولید...',
            completed:        '✅ تکمیل شده',
            error:            '❌ خطا',
        };
        return map[status] || status;
    }

    // =========================================================
    // IMAGE GENERATION
    // =========================================================

    _openImageModal() {
        if (!this.state.sessionId && !this.state.campaignId) {
            this._toast('لطفاً ابتدا یک کمپین انتخاب کنید', 'warning');
            return;
        }
        const el = this.elements;
        if (el.imagePrompt) el.imagePrompt.value = '';
        if (el.imageSize) el.imageSize.value = '1024x1024';
        if (el.promptCharCount) el.promptCharCount.textContent = '0';
        el.imagePreview?.classList.add('hidden');
        if (el.imageGeneratorModal) el.imageGeneratorModal.style.display = 'flex';
        setTimeout(() => el.imagePrompt?.focus(), 100);
    }

    _closeImageModal() {
        if (this.elements.imageGeneratorModal)
            this.elements.imageGeneratorModal.style.display = 'none';
        this.tempImageData = null;
    }

    async _generateImage() {
        const prompt = this.elements.imagePrompt?.value.trim();
        const size   = this.elements.imageSize?.value || '1024x1024';
        if (!prompt || prompt.length < 10) {
            this._toast('توضیحات کافی وارد کنید', 'warning');
            return;
        }
        const btn = this.elements.generateImageSubmit;
        if (btn) { btn.disabled = true; btn.innerHTML = '<span>⏳</span><span>در حال تولید...</span>'; }

        try {
            const res = await fetch(this.endpoints.generateImage, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this._csrf() },
                body: JSON.stringify({ prompt, session_id: this.state.sessionId, size }),
            });
            if (!res.ok) throw new Error(`HTTP ${res.status}`);
            const data = await res.json();
            this.tempImageData = { url: data.image_url, prompt: data.prompt, size: data.size };
            if (this.elements.generatedImage) this.elements.generatedImage.src = data.image_url;
            this.elements.imagePreview?.classList.remove('hidden');
            this._toast('✅ تصویر تولید شد', 'success');
            if (data.session_id) { this.state.sessionId = data.session_id; this._saveState(); }
        } catch (err) {
            this._toast('خطا در تولید تصویر: ' + err.message, 'error');
        } finally {
            if (btn) { btn.disabled = false; btn.innerHTML = '<span>🎨</span><span>تولید تصویر</span>'; }
        }
    }

    _downloadImage() {
        if (!this.tempImageData?.url) return;
        const a = document.createElement('a');
        a.href = this.tempImageData.url;
        a.download = `ai-image-${Date.now()}.png`;
        a.target = '_blank';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
    }

    _insertImageToChat() {
        if (!this.tempImageData) return;
        const el = this._createMessageShell('assistant');
        const content = el.querySelector('.message-content');
        content.innerHTML = `
            <div class="image-message">
                <img src="${this.tempImageData.url}" alt="${this.tempImageData.prompt}" class="chat-image">
                <p class="image-caption">${this.tempImageData.prompt}</p>
                <span class="image-size-badge">📐 ${this.tempImageData.size}</span>
            </div>`;
        this.elements.chatMessages.appendChild(el);
        requestAnimationFrame(() => el.classList.add('message-show'));
        this._closeImageModal();
        this._scrollBottom();
        this._toast('✅ تصویر به چت اضافه شد', 'success');
    }

    // =========================================================
    // HISTORY & SESSION
    // =========================================================

    async _loadSessionHistory() {
        try {
            const res = await fetch(this.endpoints.sessionHistory(this.state.sessionId));
            if (!res.ok) return;
            const data = await res.json();

            // Render messages
            if (data.messages?.length) {
                this._hideWelcome();
                data.messages.forEach(msg => {
                    if (msg.message_type === 'image') {
                        const el = this._createMessageShell(msg.role);
                        const content = el.querySelector('.message-content');
                        content.innerHTML = `<div class="image-message"><img src="${msg.content}" class="chat-image"></div>`;
                        this.elements.chatMessages.appendChild(el);
                        requestAnimationFrame(() => el.classList.add('message-show'));
                    } else {
                        if (msg.role === 'user') {
                            this._addUserMessage(msg.content);
                        } else {
                            this._addAIMessage(msg.content);
                        }
                    }
                });
                this._scrollBottom();
            }

            if (data.content_item) {
                this._renderContentPanel(data.content_item);
            }
        } catch (err) {
            console.error('History load error:', err);
        }
    }

    async _loadCampaigns() {
        try {
            const res = await fetch(this.endpoints.campaigns);
            if (!res.ok) throw new Error();
            const response = await res.json();
            const campaigns = response.data || [];
            const sel = this.elements.campaignSelect;
            if (!sel) return;
            sel.innerHTML = '<option value="">انتخاب کمپین...</option>';
            campaigns.forEach(c => {
                const opt = document.createElement('option');
                opt.value = c.id;
                opt.textContent = c.title;
                sel.appendChild(opt);
            });
            if (this.state.campaignId) sel.value = this.state.campaignId;
        } catch (err) {
            console.error('Campaigns load error:', err);
        }
    }

    // =========================================================
    // NEW CONVERSATION
    // =========================================================

    _showNewChatModal() {
        if (this.elements.confirmModal) this.elements.confirmModal.style.display = 'block';
    }

    _hideModal() {
        if (this.elements.confirmModal) this.elements.confirmModal.style.display = 'none';
    }

    async _startNewConversation() {
        this._hideModal();
        this._clearState();
        try {
            const res = await fetch(this.endpoints.newConversation, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'X-CSRFToken': this._csrf() },
                body: JSON.stringify({ campaign_id: this.state.campaignId }),
            });
            if (!res.ok) throw new Error();
            const data = await res.json();
            this.state.sessionId = data.session_id;
            if (this.elements.chatMessages) this.elements.chatMessages.innerHTML = '';
            this._renderContentPanel(null);
            this._showWelcome();
            this._saveState();
            this._toast('✅ مکالمه جدید آغاز شد', 'success');
        } catch (err) {
            this._toast('خطا در ایجاد مکالمه جدید', 'error');
        }
    }

    // =========================================================
    // UTILITIES
    // =========================================================

    _showWelcome()  { this.elements.welcomeMessage?.classList.remove('hidden'); }
    _hideWelcome()  { this.elements.welcomeMessage?.classList.add('hidden'); }
    _updateStatus(t){ if (this.elements.sessionStatus) this.elements.sessionStatus.textContent = t; }
    _scrollBottom() { this.elements.chatMessages?.scrollTo({ top: this.elements.chatMessages.scrollHeight, behavior: 'smooth' }); }
    _csrf()         { const c = document.cookie.split(';').find(x => x.trim().startsWith('csrftoken=')); return c ? c.split('=')[1] : ''; }
    _formatTime(d)  { return new Date(d).toLocaleTimeString('fa-IR', { hour: '2-digit', minute: '2-digit' }); }

    _updateCharCounter() {
        const len = this.elements.chatInput?.value.length || 0;
        if (this.elements.charCount) this.elements.charCount.textContent = len;
    }

    _autoResizeTextarea() {
        const ta = this.elements.chatInput;
        if (!ta) return;
        ta.style.height = 'auto';
        ta.style.height = Math.min(ta.scrollHeight, 150) + 'px';
    }

    _toast(message, type = 'info') {
        const t = this.elements.toast;
        const m = this.elements.toastMessage;
        if (!t || !m) return;
        m.textContent = message;
        t.className = `toast toast-${type} toast-show`;
        clearTimeout(this._toastTimer);
        this._toastTimer = setTimeout(() => t.classList.remove('toast-show'), 3200);
    }

    _exportChat() {
        const messages = [...this.elements.chatMessages.querySelectorAll('.message')].map(el => ({
            role: el.classList.contains('message-user') ? 'user' : 'assistant',
            content: el.querySelector('.message-content')?.textContent?.trim(),
        }));
        const blob = new Blob([JSON.stringify(messages, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url; a.download = `chat-${Date.now()}.json`; a.click();
        URL.revokeObjectURL(url);
        this._toast('📁 گفتگو ذخیره شد', 'success');
    }

    // =========================================================
    // STATE PERSISTENCE
    // =========================================================

    _saveState() {
        localStorage.setItem(this.config.storageKey, JSON.stringify({
            sessionId:      this.state.sessionId,
            contentItemId:  this.state.contentItemId,
            campaignId:     this.state.campaignId,
            currentStage:   this.state.currentStage,
            contentData:    this.state.contentData,
        }));
    }

    _loadState() {
        try {
            const saved = localStorage.getItem(this.config.storageKey);
            if (saved) Object.assign(this.state, JSON.parse(saved));
        } catch (e) {
            localStorage.removeItem(this.config.storageKey);
        }
    }

    _clearState() {
        localStorage.removeItem(this.config.storageKey);
        this.state.sessionId      = null;
        this.state.contentItemId  = null;
        this.state.currentStage   = 'greeting';
        this.state.contentData    = {};
        this.state.isProcessing   = false;
    }

    _startAutoSave() {
        setInterval(() => this._saveState(), this.config.autoSaveInterval);
    }
}

// ─── Boot ────────────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => new AIChat());