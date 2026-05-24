// static/assets/scripts/messaging-auto-reply.js

class AutoReplyManager {
    constructor() {
        this.accounts = [];
        this.rules = [];
        this.currentEditingRuleId = null;
        this.csrfToken = this.getCSRFToken();

        this.init();
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    async init() {
        try {
            await this.loadAccounts();
            await this.loadRules();
            await this.loadStats();
            this.setupEventListeners();
            this.hideLoading();
        } catch (error) {
            console.error('خطا در بارگذاری اولیه:', error);
            this.showNotification('خطا در بارگذاری اطلاعات', 'error');
            this.hideLoading();
        }
    }

    setupEventListeners() {
        // دکمه‌های افزودن قانون
        document.getElementById('add-rule-btn')?.addEventListener('click', () => this.openAddModal());
        document.getElementById('empty-add-btn')?.addEventListener('click', () => this.openAddModal());

        // فرم قانون
        document.getElementById('rule-form')?.addEventListener('submit', (e) => this.handleRuleSubmit(e));

        // فرم حذف
        document.getElementById('delete-form')?.addEventListener('submit', (e) => this.handleDeleteSubmit(e));

        // تغییر نوع قانون
        document.querySelectorAll('input[name="rule_type"]').forEach(radio => {
            radio.addEventListener('change', (e) => this.handleRuleTypeChange(e.target.value));
        });

        // تنظیمات پیشرفته
        document.getElementById('advanced-toggle')?.addEventListener('click', () => {
            const content = document.getElementById('advanced-content');
            const icon = document.querySelector('#advanced-toggle i');

            if (content.style.display === 'none') {
                content.style.display = 'block';
                icon.classList.replace('fa-chevron-down', 'fa-chevron-up');
            } else {
                content.style.display = 'none';
                icon.classList.replace('fa-chevron-up', 'fa-chevron-down');
            }
        });

        // فیلترها
        document.getElementById('search-input')?.addEventListener('input', (e) => this.applyFilters());
        document.getElementById('account-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('status-filter')?.addEventListener('change', () => this.applyFilters());
        document.getElementById('type-filter')?.addEventListener('change', () => this.applyFilters());

        // بستن مودال‌ها
        document.querySelectorAll('.close-modal, .cancel-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const modalId = e.target.closest('button').dataset.modal;
                if (modalId) this.closeModal(modalId);
            });
        });

        // کلیک خارج از مودال
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) {
                    this.closeModal(modal.id);
                }
            });
        });

        // دکمه تست
        document.getElementById('run-test-btn')?.addEventListener('click', () => this.runTest());
    }

    handleRuleTypeChange(type) {
        // مخفی کردن همه فیلدهای شرطی
        document.getElementById('keywords-group').style.display = 'none';
        document.getElementById('pattern-group').style.display = 'none';
        document.getElementById('ai-prompt-group').style.display = 'none';
        document.getElementById('context-group').style.display = 'none';
        document.getElementById('response-group').style.display = 'none';

        // نمایش فیلدهای مربوطه
        if (type === 'keyword') {
            document.getElementById('keywords-group').style.display = 'block';
            document.getElementById('response-group').style.display = 'block';

            // required کردن
            document.getElementById('rule-keywords').required = true;
            document.getElementById('rule-pattern').required = false;
            document.getElementById('ai-prompt').required = false;
            document.getElementById('rule-response').required = true;

        } else if (type === 'pattern') {
            document.getElementById('pattern-group').style.display = 'block';
            document.getElementById('response-group').style.display = 'block';

            document.getElementById('rule-keywords').required = false;
            document.getElementById('rule-pattern').required = true;
            document.getElementById('ai-prompt').required = false;
            document.getElementById('rule-response').required = true;

        } else if (type === 'ai') {
            document.getElementById('ai-prompt-group').style.display = 'block';
            document.getElementById('context-group').style.display = 'block';

            document.getElementById('rule-keywords').required = false;
            document.getElementById('rule-pattern').required = false;
            document.getElementById('ai-prompt').required = true;
            document.getElementById('rule-response').required = false;
        }
    }

    async loadAccounts() {
        try {
            const response = await fetch('/messaging/accounts/', {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('خطا در دریافت اکانت‌ها');

            this.accounts = await response.json();
            this.renderAccountOptions();
        } catch (error) {
            console.error('خطا در بارگذاری اکانت‌ها:', error);
            throw error;
        }
    }

    renderAccountOptions() {
        const selects = [
            document.getElementById('rule-account'),
            document.getElementById('account-filter')
        ];

        selects.forEach(select => {
            if (!select) return;

            // حفظ option اول (برای فیلتر)
            const firstOption = select.querySelector('option:first-child');
            select.innerHTML = '';
            if (firstOption && select.id === 'account-filter') {
                select.appendChild(firstOption);
            }

            this.accounts.forEach(account => {
                const option = document.createElement('option');
                option.value = account.id;
                option.textContent = `${account.name} (${this.getPlatformLabel(account.platform)})`;
                select.appendChild(option);
            });
        });
    }

    async loadRules() {
        try {
            const response = await fetch('/messaging/auto-reply/', {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('خطا در دریافت قوانین');

            this.rules = await response.json();
            this.renderRules();
        } catch (error) {
            console.error('خطا در بارگذاری قوانین:', error);
            throw error;
        }
    }

    async loadStats() {
        try {
            const response = await fetch('/messaging/auto-reply/stats/', {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('خطا در دریافت آمار');

            const stats = await response.json();

            document.getElementById('total-rules').textContent = stats.total_rules || 0;
            document.getElementById('active-rules').textContent = stats.active_rules || 0;
            document.getElementById('total-replies').textContent = stats.total_replies || 0;
            document.getElementById('success-rate').textContent = `${stats.success_rate || 0}%`;
        } catch (error) {
            console.error('خطا در بارگذاری آمار:', error);
        }
    }

    renderRules() {
        const grid = document.getElementById('rules-grid');
        const emptyState = document.getElementById('empty-state');

        if (!this.rules || this.rules.length === 0) {
            grid.innerHTML = '';
            emptyState.style.display = 'flex';
            return;
        }

        emptyState.style.display = 'none';
        grid.innerHTML = '';

        this.rules.forEach(rule => {
            const card = this.createRuleCard(rule);
            grid.appendChild(card);
        });
    }

    createRuleCard(rule) {
        const card = document.createElement('div');
        card.className = 'rule-card';
        card.dataset.ruleId = rule.id;

        const account = this.accounts.find(a => a.id === rule.account);
        const accountName = account ? account.name : 'نامشخص';
        const platform = account ? this.getPlatformLabel(account.platform) : '';

        const statusClass = rule.status === 'running' ? 'running' : 'stopped';
        const statusText = rule.status === 'running' ? 'در حال اجرا' : 'متوقف';
        const statusIcon = rule.status === 'running' ? 'fa-play-circle' : 'fa-stop-circle';

        const activeClass = rule.is_active ? 'active' : 'inactive';
        const activeText = rule.is_active ? 'فعال' : 'غیرفعال';

        card.innerHTML = `
            <div class="rule-card-header">
                <div class="rule-info">
                    <h3 class="rule-name">${this.escapeHtml(rule.name)}</h3>
                    <div class="rule-meta">
                        <span class="rule-account">
                            <i class="fas fa-user-circle"></i>
                            ${this.escapeHtml(accountName)} ${platform ? `(${platform})` : ''}
                        </span>
                        <span class="rule-type-badge ${rule.rule_type}">
                            ${this.getRuleTypeLabel(rule.rule_type)}
                        </span>
                    </div>
                </div>
                <div class="rule-status">
                    <span class="status-badge ${statusClass}">
                        <i class="fas ${statusIcon}"></i>
                        ${statusText}
                    </span>
                    <span class="status-badge ${activeClass}">
                        ${activeText}
                    </span>
                </div>
            </div>

            <div class="rule-card-body">
                ${this.getRuleDetails(rule)}

                <div class="rule-stats">
                    <div class="stat-item">
                        <i class="fas fa-comments"></i>
                        <span>${rule.conversation_count || 0} مکالمه</span>
                    </div>
                    <div class="stat-item">
                        <i class="fas fa-sort-amount-up"></i>
                        <span>اولویت: ${rule.priority}</span>
                    </div>
                </div>
            </div>

            <div class="rule-card-footer">
                <button class="btn-icon btn-toggle" data-id="${rule.id}" title="${rule.status === 'running' ? 'توقف' : 'شروع'}">
                    <i class="fas ${rule.status === 'running' ? 'fa-stop' : 'fa-play'}"></i>
                </button>
                <button class="btn-icon btn-test" data-id="${rule.id}" title="تست">
                    <i class="fas fa-vial"></i>
                </button>
                <button class="btn-icon btn-conversations" data-id="${rule.id}" title="مکالمات">
                    <i class="fas fa-comments"></i>
                </button>
                <button class="btn-icon btn-edit" data-id="${rule.id}" title="ویرایش">
                    <i class="fas fa-edit"></i>
                </button>
                <button class="btn-icon btn-delete" data-id="${rule.id}" title="حذف">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
        `;

        // Event listeners
        card.querySelector('.btn-toggle').addEventListener('click', () => this.toggleRule(rule.id));
        card.querySelector('.btn-test').addEventListener('click', () => this.openTestModal(rule));
        card.querySelector('.btn-conversations').addEventListener('click', () => this.openConversationsModal(rule));
        card.querySelector('.btn-edit').addEventListener('click', () => this.openEditModal(rule));
        card.querySelector('.btn-delete').addEventListener('click', () => this.openDeleteModal(rule));

        return card;
    }

    getRuleDetails(rule) {
        if (rule.rule_type === 'keyword') {
            const keywords = Array.isArray(rule.trigger_keywords)
                ? rule.trigger_keywords.join(', ')
                : rule.trigger_keywords || '';
            return `
                <div class="rule-detail">
                    <strong>کلیدواژه‌ها:</strong>
                    <span>${this.escapeHtml(keywords)}</span>
                </div>
                <div class="rule-detail">
                    <strong>پاسخ:</strong>
                    <span class="text-truncate">${this.escapeHtml(rule.response_text || '')}</span>
                </div>
            `;
        } else if (rule.rule_type === 'pattern') {
            return `
                <div class="rule-detail">
                    <strong>الگو:</strong>
                    <code>${this.escapeHtml(rule.trigger_pattern || '')}</code>
                </div>
                <div class="rule-detail">
                    <strong>پاسخ:</strong>
                    <span class="text-truncate">${this.escapeHtml(rule.response_text || '')}</span>
                </div>
            `;
        } else if (rule.rule_type === 'ai') {
            return `
                <div class="rule-detail">
                    <strong>دستورالعمل AI:</strong>
                    <span class="text-truncate">${this.escapeHtml(rule.ai_prompt || '')}</span>
                </div>
                ${rule.context_info ? `
                <div class="rule-detail">
                    <strong>زمینه:</strong>
                    <span class="text-truncate">${this.escapeHtml(rule.context_info)}</span>
                </div>
                ` : ''}
            `;
        }
        return '';
    }

    getRuleTypeLabel(type) {
        const labels = {
            'keyword': 'کلیدواژه',
            'pattern': 'الگو',
            'ai': 'هوش مصنوعی'
        };
        return labels[type] || type;
    }

    getPlatformLabel(platform) {
        const labels = {
            'whatsapp': 'واتساپ',
            'telegram': 'تلگرام',
            'instagram': 'اینستاگرام'
        };
        return labels[platform] || platform;
    }

    openAddModal() {
        this.currentEditingRuleId = null;
        document.getElementById('modal-title').textContent = 'افزودن قانون جدید';
        document.getElementById('rule-form').reset();
        document.getElementById('rule-id').value = '';

        // تنظیم پیش‌فرض
        document.querySelector('input[name="rule_type"][value="keyword"]').checked = true;
        this.handleRuleTypeChange('keyword');

        // بستن تنظیمات پیشرفته
        document.getElementById('advanced-content').style.display = 'none';
        document.querySelector('#advanced-toggle i').classList.replace('fa-chevron-up', 'fa-chevron-down');

        this.openModal('rule-modal');
    }

    openEditModal(rule) {
        this.currentEditingRuleId = rule.id;
        document.getElementById('modal-title').textContent = 'ویرایش قانون';
        document.getElementById('rule-id').value = rule.id;

        // پر کردن فرم
        document.getElementById('rule-name').value = rule.name || '';
        document.getElementById('rule-account').value = rule.account || '';
        document.getElementById('rule-priority').value = rule.priority || 1;
        document.getElementById('rule-active').checked = rule.is_active;

        // نوع قانون
        const ruleTypeRadio = document.querySelector(`input[name="rule_type"][value="${rule.rule_type}"]`);
        if (ruleTypeRadio) {
            ruleTypeRadio.checked = true;
            this.handleRuleTypeChange(rule.rule_type);
        }

        // فیلدهای شرطی
        if (rule.rule_type === 'keyword') {
            const keywords = Array.isArray(rule.trigger_keywords)
                ? rule.trigger_keywords.join(', ')
                : rule.trigger_keywords || '';
            document.getElementById('rule-keywords').value = keywords;
            document.getElementById('rule-response').value = rule.response_text || '';

        } else if (rule.rule_type === 'pattern') {
            document.getElementById('rule-pattern').value = rule.trigger_pattern || '';
            document.getElementById('rule-response').value = rule.response_text || '';

        } else if (rule.rule_type === 'ai') {
            document.getElementById('ai-prompt').value = rule.ai_prompt || '';
            document.getElementById('context-info').value = rule.context_info || '';
        }

        // تنظیمات پیشرفته
        document.getElementById('start-time').value = rule.start_time || '';
        document.getElementById('end-time').value = rule.end_time || '';
        document.getElementById('max-replies').value = rule.max_replies_per_contact || '';
        document.getElementById('cooldown').value = rule.cooldown_minutes || 0;

        this.openModal('rule-modal');
    }

    openDeleteModal(rule) {
        document.getElementById('delete-rule-id').value = rule.id;
        document.getElementById('delete-rule-name').textContent = rule.name;
        this.openModal('delete-modal');
    }

    openTestModal(rule) {
        document.getElementById('test-rule-id').value = rule.id;
        document.getElementById('test-rule-name').textContent = rule.name;
        document.getElementById('test-message').value = '';
        document.getElementById('test-result').style.display = 'none';
        this.openModal('test-modal');
    }

    async openConversationsModal(rule) {
        document.getElementById('conv-rule-id').value = rule.id;
        document.getElementById('conv-rule-name').textContent = rule.name;

        this.openModal('conversations-modal');

        // بارگذاری مکالمات
        await this.loadConversations(rule.id);
    }

    async loadConversations(ruleId) {
        const list = document.getElementById('conversations-list');
        const empty = document.getElementById('empty-conversations');
        const loading = document.getElementById('loading-conversations');

        list.style.display = 'none';
        empty.style.display = 'none';
        loading.style.display = 'flex';

        try {
            const response = await fetch(`/messaging/auto-reply/${ruleId}/conversations/`, {
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) throw new Error('خطا در دریافت مکالمات');

            const conversations = await response.json();
            loading.style.display = 'none';

            if (conversations.length === 0) {
                empty.style.display = 'flex';
                return;
            }

            list.innerHTML = '';
            list.style.display = 'block';

            conversations.forEach(conv => {
                const item = document.createElement('div');
                item.className = `conversation-item ${conv.direction}`;

                const date = new Date(conv.created_at).toLocaleString('fa-IR');

                item.innerHTML = `
                    <div class="conv-header">
                        <span class="conv-contact">${this.escapeHtml(conv.contact_identifier)}</span>
                        <span class="conv-date">${date}</span>
                    </div>
                    <div class="conv-message">${this.escapeHtml(conv.message_text)}</div>
                    <div class="conv-direction">
                        <i class="fas fa-${conv.direction === 'incoming' ? 'arrow-down' : 'arrow-up'}"></i>
                        ${conv.direction === 'incoming' ? 'دریافتی' : 'ارسالی'}
                    </div>
                `;

                list.appendChild(item);
            });

        } catch (error) {
            console.error('خطا در بارگذاری مکالمات:', error);
            loading.style.display = 'none';
            empty.style.display = 'flex';
            this.showNotification('خطا در بارگذاری مکالمات', 'error');
        }
    }

    async handleRuleSubmit(e) {
        e.preventDefault();

        const submitBtn = document.getElementById('submit-btn');
        const originalText = submitBtn.innerHTML;
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>در حال ذخیره...</span>';

        try {
            const formData = this.collectFormData();
            const ruleId = document.getElementById('rule-id').value;

            let url = '/messaging/auto-reply/';
            let method = 'POST';

            if (ruleId) {
                url = `/messaging/auto-reply/${ruleId}/`;
                method = 'PUT';
            }

            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify(formData)
            });

            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'خطا در ذخیره قانون');
            }

            await this.loadRules();
            await this.loadStats();
            this.closeModal('rule-modal');
            this.showNotification(ruleId ? 'قانون با موفقیت ویرایش شد' : 'قانون با موفقیت ایجاد شد', 'success');

        } catch (error) {
            console.error('خطا در ذخیره قانون:', error);
            this.showNotification(error.message || 'خطا در ذخیره قانون', 'error');
        } finally {
            submitBtn.disabled = false;
            submitBtn.innerHTML = originalText;
        }
    }

    collectFormData() {
        const ruleType = document.querySelector('input[name="rule_type"]:checked').value;

        const data = {
            name: document.getElementById('rule-name').value.trim(),
            account: parseInt(document.getElementById('rule-account').value),
            rule_type: ruleType,
            priority: parseInt(document.getElementById('rule-priority').value) || 1,
            is_active: document.getElementById('rule-active').checked,
            start_time: document.getElementById('start-time').value || null,
            end_time: document.getElementById('end-time').value || null,
            max_replies_per_contact: parseInt(document.getElementById('max-replies').value) || null,
            cooldown_minutes: parseInt(document.getElementById('cooldown').value) || 0
        };

        // فیلدهای شرطی بر اساس نوع
        if (ruleType === 'keyword') {
            const keywordsStr = document.getElementById('rule-keywords').value.trim();
            data.trigger_keywords = keywordsStr.split(',').map(k => k.trim()).filter(k => k);
            data.response_text = document.getElementById('rule-response').value.trim();
            data.trigger_pattern = null;
            data.ai_prompt = null;
            data.context_info = null;

        } else if (ruleType === 'pattern') {
            data.trigger_pattern = document.getElementById('rule-pattern').value.trim();
            data.response_text = document.getElementById('rule-response').value.trim();
            data.trigger_keywords = null;
            data.ai_prompt = null;
            data.context_info = null;

        } else if (ruleType === 'ai') {
            data.ai_prompt = document.getElementById('ai-prompt').value.trim();
            data.context_info = document.getElementById('context-info').value.trim() || null;
            data.trigger_keywords = null;
                        data.trigger_pattern = null;
            data.response_text = null;
        }

        return data;
    }

    async handleDeleteSubmit(e) {
        e.preventDefault();

        const ruleId = document.getElementById('delete-rule-id').value;

        try {
            const response = await fetch(`/messaging/auto-reply/${ruleId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('خطا در حذف قانون');
            }

            await this.loadRules();
            await this.loadStats();

            this.closeModal('delete-modal');
            this.showNotification('قانون با موفقیت حذف شد', 'success');

        } catch (error) {
            console.error('خطا در حذف قانون:', error);
            this.showNotification(error.message || 'خطا در حذف قانون', 'error');
        }
    }

    async toggleRule(ruleId) {
        try {
            const response = await fetch(`/messaging/auto-reply/${ruleId}/toggle/`, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': this.csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('خطا در تغییر وضعیت قانون');
            }

            await this.loadRules();
            this.showNotification('وضعیت قانون تغییر کرد', 'success');

        } catch (error) {
            console.error('خطا در تغییر وضعیت:', error);
            this.showNotification(error.message || 'خطا در تغییر وضعیت', 'error');
        }
    }

    async runTest() {
        const ruleId = document.getElementById('test-rule-id').value;
        const message = document.getElementById('test-message').value.trim();

        if (!message) {
            this.showNotification('پیام تست را وارد کنید', 'warning');
            return;
        }

        const btn = document.getElementById('run-test-btn');
        const originalText = btn.innerHTML;

        btn.disabled = true;
        btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i>';

        try {
            const response = await fetch(`/messaging/auto-reply/${ruleId}/test/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.csrfToken
                },
                body: JSON.stringify({
                    message: message
                })
            });

            if (!response.ok) {
                throw new Error('خطا در اجرای تست');
            }

            const result = await response.json();

            const resultBox = document.getElementById('test-result');
            resultBox.style.display = 'block';

            resultBox.innerHTML = `
                <div class="test-result-content ${result.matched ? 'matched' : 'not-matched'}">
                    <div class="test-status">
                        <i class="fas fa-${result.matched ? 'check-circle' : 'times-circle'}"></i>
                        ${result.matched ? 'قانون Match شد' : 'قانون Match نشد'}
                    </div>

                    ${
                        result.response
                            ? `
                        <div class="test-response">
                            <strong>پاسخ:</strong>
                            <div class="response-box">
                                ${this.escapeHtml(result.response)}
                            </div>
                        </div>
                    `
                            : ''
                    }
                </div>
            `;

        } catch (error) {
            console.error('خطا در تست قانون:', error);
            this.showNotification(error.message || 'خطا در تست قانون', 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = originalText;
        }
    }

    applyFilters() {
        const search = document.getElementById('search-input')?.value.toLowerCase() || '';
        const account = document.getElementById('account-filter')?.value || '';
        const status = document.getElementById('status-filter')?.value || '';
        const type = document.getElementById('type-filter')?.value || '';

        let filtered = [...this.rules];

        if (search) {
            filtered = filtered.filter(rule =>
                rule.name.toLowerCase().includes(search)
            );
        }

        if (account) {
            filtered = filtered.filter(rule =>
                String(rule.account) === String(account)
            );
        }

        if (status) {
            if (status === 'active') {
                filtered = filtered.filter(rule => rule.is_active);
            } else if (status === 'inactive') {
                filtered = filtered.filter(rule => !rule.is_active);
            } else {
                filtered = filtered.filter(rule => rule.status === status);
            }
        }

        if (type) {
            filtered = filtered.filter(rule =>
                rule.rule_type === type
            );
        }

        this.renderFilteredRules(filtered);
    }

    renderFilteredRules(filteredRules) {
        const grid = document.getElementById('rules-grid');
        const emptyState = document.getElementById('empty-state');

        if (!filteredRules.length) {
            grid.innerHTML = '';
            emptyState.style.display = 'flex';
            return;
        }

        emptyState.style.display = 'none';
        grid.innerHTML = '';

        filteredRules.forEach(rule => {
            grid.appendChild(this.createRuleCard(rule));
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.add('show');
        document.body.classList.add('modal-open');
    }

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (!modal) return;

        modal.classList.remove('show');
        document.body.classList.remove('modal-open');
    }

    hideLoading() {
        document.getElementById('loading-state')?.remove();
    }

    showNotification(message, type = 'info') {
        const container = document.getElementById('notification-container');

        if (!container) {
            alert(message);
            return;
        }

        const notification = document.createElement('div');
        notification.className = `notification ${type}`;

        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas ${this.getNotificationIcon(type)}"></i>
                <span>${this.escapeHtml(message)}</span>
            </div>
        `;

        container.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {
            notification.classList.remove('show');

            setTimeout(() => {
                notification.remove();
            }, 300);

        }, 4000);
    }

    getNotificationIcon(type) {
        const icons = {
            success: 'fa-check-circle',
            error: 'fa-times-circle',
            warning: 'fa-exclamation-triangle',
            info: 'fa-info-circle'
        };

        return icons[type] || icons.info;
    }

    escapeHtml(text) {
        if (text === null || text === undefined) return '';

        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
}

// اجرای برنامه
document.addEventListener('DOMContentLoaded', () => {
    new AutoReplyManager();
});
