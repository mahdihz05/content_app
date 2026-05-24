// static/assets/js/account-list.js

let accounts = [];

document.addEventListener('DOMContentLoaded', function() {
    loadAccounts();
    setupModalHandlers();
});

async function loadAccounts() {
    const container = document.getElementById('accounts-container');
    container.innerHTML = '<div class="loading">در حال بارگذاری...</div>';

    try {
        const response = await fetch('/api/messaging/accounts/');
        accounts = await response.json();

        if (accounts.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 60px; color: var(--text-muted); grid-column: 1/-1;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.5" style="margin-bottom: 20px; opacity: 0.5;">
                        <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                        <circle cx="9" cy="7" r="4"></circle>
                        <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                        <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                    </svg>
                    <h3 style="margin-bottom: 12px; color: var(--text-primary);">هنوز اکانتی اضافه نشده</h3>
                    <p style="margin-bottom: 24px;">برای شروع، اولین اکانت خود را متصل کنید</p>
                    <a href="/dashboard/messaging/accounts/create/" class="btn-primary">
                        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <line x1="12" y1="5" x2="12" y2="19"></line>
                            <line x1="5" y1="12" x2="19" y2="12"></line>
                        </svg>
                        افزودن اکانت
                    </a>
                </div>
            `;
            return;
        }

        container.innerHTML = accounts.map(account => `
            <div class="account-card">
                <div class="account-card-header">
                    <span class="platform-badge ${account.platform}">${getPlatformLabel(account.platform)}</span>
                    <span class="account-status ${account.status === 'active' ? '' : 'inactive'}"></span>
                </div>
                <div class="account-identifier">${account.identifier}</div>
                <div class="account-date">متصل شده: ${formatDate(account.created_at)}</div>
                <div class="account-actions">
                    <button class="btn-small" onclick="saveSession(${account.id})">ذخیره Session</button>
                    <button class="btn-small btn-danger" onclick="deleteAccount(${account.id})">حذف</button>
                </div>
            </div>
        `).join('');

    } catch (error) {
        console.error('خطا در بارگذاری اکانت‌ها:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 60px; color: #ef4444; grid-column: 1/-1;">
                خطا در بارگذاری اکانت‌ها. لطفاً دوباره تلاش کنید.
            </div>
        `;
    }
}

function getPlatformLabel(platform) {
    const labels = {
        'telegram': 'تلگرام',
        'whatsapp': 'واتساپ',
        'bale': 'بله'
    };
    return labels[platform] || platform;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('fa-IR');
}

async function saveSession(accountId) {
    const modal = document.getElementById('session-modal');
    modal.classList.add('active');

    // ذخیره ID برای استفاده بعدی
    modal.dataset.accountId = accountId;
}

function setupModalHandlers() {
    const modal = document.getElementById('session-modal');
    const closeBtn = modal.querySelector('.modal-close');
    const saveBtn = document.getElementById('save-session-btn');

    closeBtn.addEventListener('click', () => {
        modal.classList.remove('active');
    });

    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            modal.classList.remove('active');
        }
    });

    saveBtn.addEventListener('click', async () => {
        const accountId = modal.dataset.accountId;
        const sessionData = document.getElementById('session-data').value.trim();

        if (!sessionData) {
            alert('لطفاً داده Session را وارد کنید');
            return;
        }

        try {
            const response = await fetch(`/api/messaging/accounts/${accountId}/save_session/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ session_data: sessionData })
            });

            if (response.ok) {
                alert('Session با موفقیت ذخیره شد');
                modal.classList.remove('active');
                document.getElementById('session-data').value = '';
            } else {
                const error = await response.json();
                alert('خطا: ' + (error.error || 'خطای نامشخص'));
            }
        } catch (error) {
            console.error('خطا در ذخیره session:', error);
            alert('خطا در ذخیره session');
        }
    });
}

async function deleteAccount(accountId) {
    if (!confirm('آیا از حذف این اکانت اطمینان دارید؟')) {
        return;
    }

    try {
        const response = await fetch(`/api/messaging/accounts/${accountId}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        });

        if (response.ok) {
            alert('اکانت با موفقیت حذف شد');
            loadAccounts();
        } else {
            alert('خطا در حذف اکانت');
        }
    } catch (error) {
        console.error('خطا در حذف اکانت:', error);
        alert('خطا در حذف اکانت');
    }
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
