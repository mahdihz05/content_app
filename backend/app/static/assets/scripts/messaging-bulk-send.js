/**
 * File: static/assets/scripts/messaging-bulk-send.js
 * Compatible with new messaging backend
 */

class BulkSendManager {

    constructor() {

        this.accounts = [];
        this.recipients = [];
        this.selectedFile = null;

        this.API_BASE = '/messaging/api/';

        this.csrfToken = this.getCSRFToken();

        this.init();
    }

    // ================= CSRF =================

    getCSRFToken() {

        return document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1] || '';
    }

    // ================= INIT =================

    init() {

        this.cacheDOMElements();
        this.attachEventListeners();

        this.loadAccounts();

        this.updateCharCount();
        this.updateRecipientsCount();
        this.updateStats();
        this.updatePreview();
    }

    cacheDOMElements() {

        this.form = document.getElementById('bulk-send-form');

        this.accountSelect = document.getElementById('account-select');

        this.messageTypeRadios =
            document.querySelectorAll('input[name="message_type"]');

        this.messageContent =
            document.getElementById('message-content');

        this.recipientsTextarea =
            document.getElementById('recipients');

        this.scheduleTypeRadios =
            document.querySelectorAll('input[name="schedule_type"]');

        this.delayInput =
            document.getElementById('delay');

        this.fileUploadGroup =
            document.getElementById('file-upload-group');

        this.fileUpload =
            document.getElementById('file-upload');

        this.filePreview =
            document.getElementById('file-preview');

        this.importFile =
            document.getElementById('import-file');

        this.scheduleDatetimeGroup =
            document.getElementById('schedule-datetime-group');

        this.scheduleDatetime =
            document.getElementById('schedule-datetime');

        this.submitBtn =
            document.getElementById('submit-btn');

        this.previewBtn =
            document.getElementById('preview-btn');

        this.previewMessage =
            document.getElementById('preview-message');

        this.charCount =
            document.getElementById('char-count');

        this.recipientsCount =
            document.getElementById('recipients-count');

        this.statRecipients =
            document.getElementById('stat-recipients');

        this.statTime =
            document.getElementById('stat-time');

        this.statCost =
            document.getElementById('stat-cost');
    }

    attachEventListeners() {

        this.form?.addEventListener(
            'submit',
            (e) => this.handleSubmit(e)
        );

        this.messageTypeRadios.forEach(radio => {

            radio.addEventListener('change', (e) => {

                this.handleMessageTypeChange(e.target.value);
                this.updatePreview();
            });
        });

        this.messageContent?.addEventListener('input', () => {

            this.updateCharCount();
            this.updatePreview();
        });

        this.recipientsTextarea?.addEventListener('input', () => {

            this.updateRecipientsCount();
            this.updateStats();
        });

        this.scheduleTypeRadios.forEach(radio => {

            radio.addEventListener('change', (e) => {

                this.handleScheduleTypeChange(e.target.value);
            });
        });

        this.delayInput?.addEventListener('input', () => {

            this.updateStats();
        });

        this.fileUpload?.addEventListener(
            'change',
            (e) => this.handleFileUpload(e)
        );

        this.importFile?.addEventListener(
            'change',
            (e) => this.handleImportContacts(e)
        );

        this.previewBtn?.addEventListener('click', () => {

            this.updatePreview();
        });
    }

    // ================= API =================

    async apiRequest(endpoint, options = {}) {

        const headers = {
            'X-Requested-With': 'XMLHttpRequest',
            ...(options.headers || {})
        };

        if (
            ['POST', 'PUT', 'PATCH', 'DELETE']
                .includes((options.method || 'GET').toUpperCase())
        ) {

            headers['X-CSRFToken'] = this.csrfToken;
        }

        const response = await fetch(
            `${this.API_BASE}${endpoint}`,
            {
                credentials: 'include',
                ...options,
                headers
            }
        );

        let data = {};

        const contentType =
            response.headers.get('content-type') || '';

        if (contentType.includes('application/json')) {

            data = await response.json();
        }

        if (!response.ok) {

            if (typeof data === 'object') {

                const message = Object.entries(data)
                    .map(([k, v]) => {

                        return `${k}: ${
                            Array.isArray(v)
                                ? v.join(', ')
                                : v
                        }`;
                    })
                    .join('\n');

                throw new Error(message || 'خطای سرور');
            }

            throw new Error('خطا در ارتباط با سرور');
        }

        return data;
    }

    // ================= ACCOUNTS =================

    async loadAccounts() {

        try {

            const data =
                await this.apiRequest('accounts/');

            this.accounts = Array.isArray(data)
                ? data
                : (data.results || []);

            this.renderAccounts();

        } catch (error) {

            console.error(error);

            this.showNotification(
                'خطا در بارگذاری اکانت‌ها',
                'error'
            );
        }
    }

    renderAccounts() {

        if (!this.accountSelect) return;

        this.accountSelect.innerHTML = `
            <option value="">
                اکانت مورد نظر را انتخاب کنید
            </option>
        `;

        this.accounts
            .filter(acc => acc.is_active)
            .forEach(acc => {

                const option =
                    document.createElement('option');

                option.value = acc.id;

                option.textContent =
                    acc.name ||
                    acc.account_identifier ||
                    `اکانت ${acc.id}`;

                this.accountSelect.appendChild(option);
            });
    }

    // ================= FORM =================

    handleMessageTypeChange(type) {

        if (!this.fileUploadGroup) return;

        this.fileUploadGroup.style.display =
            type === 'text'
                ? 'none'
                : 'block';
    }

    handleScheduleTypeChange(type) {

        if (!this.scheduleDatetimeGroup) return;

        this.scheduleDatetimeGroup.style.display =
            type === 'scheduled'
                ? 'block'
                : 'none';

        if (type !== 'scheduled') {

            this.scheduleDatetime.value = '';
        }
    }

    updateCharCount() {

        const len =
            this.messageContent?.value.length || 0;

        this.charCount.textContent = len;

        const parent = this.charCount.parentElement;

        parent?.classList.remove('warning', 'danger');

        if (len > 3000) {
            parent?.classList.add('danger');
        }
        else if (len > 2000) {
            parent?.classList.add('warning');
        }
    }

    normalizeRecipientsFromText(text) {

        return [...new Set(

            text
                .split(/\n|,|;/g)
                .map(x => x.trim())
                .filter(Boolean)
        )];
    }

    updateRecipientsCount() {

        this.recipients =
            this.normalizeRecipientsFromText(
                this.recipientsTextarea.value
            );

        this.recipientsCount.textContent =
            this.recipients.length;
    }

    updateStats() {

        const count = this.recipients.length;

        const delay =
            parseInt(this.delayInput.value || '0');

        const totalSeconds = count * delay;

        const minutes =
            Math.ceil(totalSeconds / 60);

        this.statRecipients.textContent = count;

        this.statTime.textContent =
            count
                ? `${minutes} دقیقه`
                : '0 دقیقه';

        this.statCost.textContent = 'رایگان';
    }

    updatePreview() {

        const message =
            this.messageContent.value.trim();

        if (!message && !this.selectedFile) {

            this.previewMessage.innerHTML = `
                <p class="preview-placeholder">
                    پیام شما اینجا نمایش داده می‌شود...
                </p>
            `;

            return;
        }

        let html = '';

        if (this.selectedFile) {

            if (
                this.selectedFile.type.startsWith('image/')
            ) {

                html += `
                    <img src="${URL.createObjectURL(this.selectedFile)}">
                `;
            }
            else {

                html += `
                    <div class="preview-file">
                        <span>
                            ${this.escapeHtml(this.selectedFile.name)}
                        </span>
                    </div>
                `;
            }
        }

        if (message) {

            html += `
                <p>
                    ${this.escapeHtml(message).replace(/\n/g, '<br>')}
                </p>
            `;
        }

        this.previewMessage.innerHTML = html;
    }

    handleFileUpload(e) {

        const file = e.target.files[0];

        if (!file) return;

        this.selectedFile = file;

        this.updatePreview();
    }

    async handleImportContacts(e) {

        const file = e.target.files[0];

        if (!file) return;

        try {

            const text = await file.text();

            const numbers = text
                .split(/\n|,|;/g)
                .map(x => x.trim())
                .filter(Boolean);

            const merged = [

                ...new Set([
                    ...this.recipients,
                    ...numbers
                ])
            ];

            this.recipientsTextarea.value =
                merged.join('\n');

            this.updateRecipientsCount();
            this.updateStats();

            this.showNotification(
                `${numbers.length} مخاطب وارد شد`,
                'success'
            );

        } catch {

            this.showNotification(
                'خطا در خواندن فایل',
                'error'
            );
        }

        this.importFile.value = '';
    }

    // ================= VALIDATION =================

    validateForm() {

        if (!this.accountSelect.value) {
            return 'اکانت را انتخاب کنید';
        }

        if (!this.recipients.length) {
            return 'حداقل یک مخاطب وارد کنید';
        }

        const messageType =
            document.querySelector(
                'input[name="message_type"]:checked'
            )?.value;

        if (
            messageType === 'text' &&
            !this.messageContent.value.trim()
        ) {

            return 'متن پیام نمی‌تواند خالی باشد';
        }

        if (
            messageType !== 'text' &&
            !this.selectedFile
        ) {

            return 'فایل موردنظر را انتخاب کنید';
        }

        return null;
    }

    // ================= SUBMIT =================

    async handleSubmit(e) {

        e.preventDefault();

        const validationError =
            this.validateForm();

        if (validationError) {

            this.showNotification(
                validationError,
                'error'
            );

            return;
        }

        const formData = new FormData();

        const messageType =
            document.querySelector(
                'input[name="message_type"]:checked'
            )?.value || 'text';

        const scheduleType =
            document.querySelector(
                'input[name="schedule_type"]:checked'
            )?.value || 'immediate';

        formData.append(
            'account_id',
            this.accountSelect.value
        );

        formData.append(
            'message_type',
            messageType
        );

        formData.append(
            'message',
            this.messageContent.value.trim()
        );

        formData.append(
            'recipients_json',
            JSON.stringify(this.recipients)
        );

        formData.append(
            'delay',
            this.delayInput.value || '0'
        );

        if (
            scheduleType === 'scheduled' &&
            this.scheduleDatetime.value
        ) {

            formData.append(
                'scheduled_at',
                this.scheduleDatetime.value
            );
        }

        if (this.selectedFile) {

            formData.append(
                'attachment',
                this.selectedFile
            );
        }

        try {

            this.submitBtn.disabled = true;

            const data = await this.apiRequest(
                'bulk-send/create/',
                {
                    method: 'POST',
                    body: formData
                }
            );

            this.showNotification(
                data.detail || 'پیام‌ها با موفقیت ثبت شدند',
                'success'
            );

            this.form.reset();

            this.selectedFile = null;
            this.recipients = [];

            this.updateCharCount();
            this.updateRecipientsCount();
            this.updateStats();
            this.updatePreview();

        } catch (error) {

            console.error(error);

            this.showNotification(
                error.message || 'خطا در ارسال پیام‌ها',
                'error'
            );

        } finally {

            this.submitBtn.disabled = false;
        }
    }

    // ================= HELPERS =================

    escapeHtml(str = '') {

        return String(str).replace(/[&<>"']/g, m => ({
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        }[m]));
    }

    showNotification(message, type = 'info') {

        alert(message);
    }
}

document.addEventListener('DOMContentLoaded', () => {

    window.bulkSendManager =
        new BulkSendManager();
});