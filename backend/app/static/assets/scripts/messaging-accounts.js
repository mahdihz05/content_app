class AccountsManager {
    constructor() {
        this.accounts = [];
        this.filteredAccounts = [];
        this.currentFilter = '';
        this.searchQuery = '';
        this.editingAccountId = null;
        this.API_BASE = '/messaging/';

        this.init();
    }

    init() {
        this.cacheDOMElements();
        this.attachEventListeners();
        this.loadAccounts();
    }

    cacheDOMElements() {

        this.addAccountBtn = document.getElementById('add-account-btn');

        this.closeModalBtns = document.querySelectorAll('.modal-close');
        this.cancelBtns = document.querySelectorAll('#cancel-btn, #cancel-delete-btn');
        this.confirmDeleteBtn = document.getElementById('confirm-delete-btn');

        this.accountModal = document.getElementById('account-modal');
        this.deleteModal = document.getElementById('delete-modal');

        this.accountForm = document.getElementById('account-form');

        this.searchInput = document.getElementById('search-input');
        this.platformFilter = document.getElementById('platform-filter');

        this.accountsTableBody = document.getElementById('accounts-tbody');
        this.emptyState = document.getElementById('empty-state');
        this.accountsTable = document.querySelector('.accounts-table');

        this.baleAccountsEl = document.getElementById('bale-count');
        this.telegramAccountsEl = document.getElementById('telegram-count');
        this.whatsappAccountsEl = document.getElementById('whatsapp-count');
        this.activeAccountsEl = document.getElementById('active-count');

        this.modalTitle = document.getElementById('modal-title');
        this.accountIdInput = document.getElementById('account-id');

        this.accountNameInput = document.getElementById('account-name');
        this.platformInput = document.getElementById('account-platform');
        this.accountIdentifierInput = document.getElementById('account-identifier');
        this.phoneNumberInput = document.getElementById('phone-number');
        this.apiTokenInput = document.getElementById('api-token');
        this.isActiveInput = document.getElementById('is-active');
    }

    attachEventListeners() {

        this.addAccountBtn?.addEventListener('click', () => this.openAddModal());

        this.closeModalBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                this.closeModal(e.target.closest('.modal'));
            });
        });

        this.cancelBtns.forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                this.closeModal(e.target.closest('.modal'));
            });
        });

        this.confirmDeleteBtn?.addEventListener('click', async () => {
            if (this.editingAccountId) {
                await this.deleteAccount(this.editingAccountId);
            }
        });

        window.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal(e.target);
            }
        });

        this.accountForm?.addEventListener('submit', (e) => {
            this.handleAccountSubmit(e);
        });

        this.searchInput?.addEventListener('input', (e) => {
            this.handleSearch(e.target.value);
        });

        this.platformFilter?.addEventListener('change', (e) => {
            this.handleFilter(e.target.value);
        });
    }

    async apiRequest(endpoint, options = {}) {

        const url = `${this.API_BASE}${endpoint}`;

        const defaultHeaders = {
            'X-Requested-With': 'XMLHttpRequest'
        };

        if (!(options.body instanceof FormData)) {
            defaultHeaders['Content-Type'] = 'application/json';
        }

        if (
            ['POST', 'PUT', 'PATCH', 'DELETE']
                .includes((options.method || 'GET').toUpperCase())
        ) {
            defaultHeaders['X-CSRFToken'] = this.getCSRFToken();
        }

        const response = await fetch(url, {
            credentials: 'include',
            ...options,
            headers: {
                ...defaultHeaders,
                ...(options.headers || {})
            }
        });

        let data = null;

        const contentType = response.headers.get('content-type') || '';

        if (contentType.includes('application/json')) {
            data = await response.json();
        }

        if (!response.ok) {

            if (data && typeof data === 'object' && !Array.isArray(data)) {

                const messages = Object.entries(data).map(([f, v]) => {
                    return `${f}: ${Array.isArray(v) ? v.join(', ') : v}`;
                });

                throw new Error(messages.join(' | ') || 'خطای سرور');
            }

            throw new Error(data?.detail || 'خطای ارتباط با سرور');
        }

        return data;
    }

    async loadAccounts() {

        try {

            const data = await this.apiRequest('api/accounts/');

            this.accounts = Array.isArray(data)
                ? data
                : (data?.results || []);

            this.updateStats();
            this.applyFilters();

        } catch (error) {

            this.showNotification(error.message, 'error');
        }
    }

    async saveAccount() {

        const accountId = this.accountIdInput.value;

        const payload = {
            name: this.accountNameInput.value.trim(),
            platform: this.platformInput.value,
            account_identifier: this.accountIdentifierInput.value.trim(),
            phone_number: this.phoneNumberInput.value.trim(),
            api_token: this.apiTokenInput.value.trim(),
            is_active: this.isActiveInput.checked
        };

        // فقط این بخش اصلاح شده
        const endpoint = accountId
            ? `api/accounts/${accountId}/`
            : 'api/accounts/create/';

        const method = accountId
            ? 'PATCH'
            : 'POST';

        try {

            await this.apiRequest(endpoint, {
                method,
                body: JSON.stringify(payload)
            });

            this.showNotification(
                'تغییرات با موفقیت ذخیره شد',
                'success'
            );

            this.closeModal(this.accountModal);

            this.loadAccounts();

        } catch (error) {

            this.showNotification(error.message, 'error');
        }
    }

    async deleteAccount(accountId) {

        try {

            await this.apiRequest(
                `api/accounts/${accountId}/`,
                {
                    method: 'DELETE'
                }
            );

            this.showNotification('اکانت حذف شد', 'success');

            this.closeModal(this.deleteModal);

            this.loadAccounts();

        } catch (error) {

            this.showNotification(error.message, 'error');
        }
    }

    updateStats() {

        const stats = {
            bale: this.accounts.filter(a => a.platform === 'bale').length,
            telegram: this.accounts.filter(a => a.platform === 'telegram').length,
            whatsapp: this.accounts.filter(a => a.platform === 'whatsapp').length,
            active: this.accounts.filter(a => a.is_active).length
        };

        if (this.baleAccountsEl) {
            this.baleAccountsEl.textContent = stats.bale;
        }

        if (this.telegramAccountsEl) {
            this.telegramAccountsEl.textContent = stats.telegram;
        }

        if (this.whatsappAccountsEl) {
            this.whatsappAccountsEl.textContent = stats.whatsapp;
        }

        if (this.activeAccountsEl) {
            this.activeAccountsEl.textContent = stats.active;
        }
    }

    applyFilters() {

        let filtered = [...this.accounts];

        if (this.currentFilter) {
            filtered = filtered.filter(
                a => a.platform === this.currentFilter
            );
        }

        if (this.searchQuery) {

            const query = this.searchQuery.toLowerCase();

            filtered = filtered.filter(a =>
                (a.account_identifier || '')
                    .toLowerCase()
                    .includes(query)
                ||
                (a.name || '')
                    .toLowerCase()
                    .includes(query)
            );
        }

        this.filteredAccounts = filtered;

        this.renderAccounts();
    }

    renderAccounts() {

        if (!this.accountsTableBody) return;

        if (this.filteredAccounts.length === 0) {

            this.showEmptyState();

            this.accountsTableBody.innerHTML = '';

            return;
        }

        this.hideEmptyState();

        this.accountsTableBody.innerHTML =
            this.filteredAccounts.map(account => `
                <tr data-account-id="${account.id}">
                    <td>${this.escapeHtml(account.name || 'بدون نام')}</td>

                    <td>
                        <span class="platform-badge platform-${account.platform}">
                            ${this.escapeHtml(account.platform_display || account.platform)}
                        </span>
                    </td>

                    <td>
                        <code style="font-size:0.85rem;">
                            ${this.escapeHtml(account.account_identifier)}
                        </code>
                    </td>

                    <td>
                        ${this.escapeHtml(account.phone_number || '—')}
                    </td>

                    <td>
                        <span class="status-badge status-${account.is_active ? 'active' : 'inactive'}">
                            ${account.is_active ? 'فعال' : 'غیرفعال'}
                        </span>
                    </td>

                    <td>
                        ${this.formatDate(account.created_at)}
                    </td>

                    <td class="actions-cell">
                        <button class="action-btn edit-btn" data-id="${account.id}">
                            ویرایش
                        </button>

                        <button class="action-btn delete-btn" data-id="${account.id}">
                            حذف
                        </button>
                    </td>
                </tr>
            `).join('');

        this.accountsTableBody
            .querySelectorAll('.edit-btn')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    this.openEditModal(Number(btn.dataset.id));
                });
            });

        this.accountsTableBody
            .querySelectorAll('.delete-btn')
            .forEach(btn => {
                btn.addEventListener('click', () => {
                    this.openDeleteModal(Number(btn.dataset.id));
                });
            });
    }

    showEmptyState() {
        if (this.accountsTable) {
            this.accountsTable.style.display = 'none';
        }

        if (this.emptyState) {
            this.emptyState.style.display = 'flex';
        }
    }

    hideEmptyState() {
        if (this.accountsTable) {
            this.accountsTable.style.display = 'table';
        }

        if (this.emptyState) {
            this.emptyState.style.display = 'none';
        }
    }

    openAddModal() {

        this.editingAccountId = null;

        this.modalTitle.textContent = 'افزودن اکانت جدید';

        this.accountForm.reset();

        this.accountIdInput.value = '';

        this.openModal(this.accountModal);
    }

    openEditModal(accountId) {

        const account = this.accounts.find(a => a.id === accountId);

        if (!account) return;

        this.editingAccountId = accountId;

        this.modalTitle.textContent = 'ویرایش اکانت';

        this.accountIdInput.value = account.id;
        this.accountNameInput.value = account.name || '';
        this.platformInput.value = account.platform || '';
        this.accountIdentifierInput.value = account.account_identifier || '';
        this.phoneNumberInput.value = account.phone_number || '';
        this.apiTokenInput.value = account.api_token || '';
        this.isActiveInput.checked = !!account.is_active;

        this.openModal(this.accountModal);
    }

    openDeleteModal(accountId) {

        this.editingAccountId = accountId;

        this.openModal(this.deleteModal);
    }

    openModal(modal) {

        if (modal) {

            modal.classList.add('active');

            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {

        if (modal) {

            modal.classList.remove('active');

            document.body.style.overflow = '';
        }
    }

    handleSearch(query) {

        this.searchQuery = query.trim();

        this.applyFilters();
    }

    handleFilter(platform) {

        this.currentFilter = platform;

        this.applyFilters();
    }

    async handleAccountSubmit(e) {

        e.preventDefault();

        await this.saveAccount();
    }

    formatDate(dateString) {

        if (!dateString) return '—';

        const date = new Date(dateString);

        if (isNaN(date.getTime())) return '—';

        return new Intl.DateTimeFormat('fa-IR', {
            year: 'numeric',
            month: '2-digit',
            day: '2-digit',
            hour: '2-digit',
            minute: '2-digit'
        }).format(date);
    }

    escapeHtml(text) {

        const div = document.createElement('div');

        div.textContent = text ?? '';

        return div.innerHTML;
    }

    getCSRFToken() {

        return document.cookie
            .split('; ')
            .find(row => row.startsWith('csrftoken='))
            ?.split('=')[1] || '';
    }

    showNotification(message, type = 'info') {

        const notification = document.createElement('div');

        notification.className =
            `notification notification-${type}`;

        notification.innerHTML =
            `<span>${this.escapeHtml(message)}</span>`;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('show');
        }, 10);

        setTimeout(() => {

            notification.classList.remove('show');

            setTimeout(() => {
                notification.remove();
            }, 300);

        }, 3000);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    window.accountsManager = new AccountsManager();
});