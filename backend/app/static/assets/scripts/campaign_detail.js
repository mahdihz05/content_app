// static/js/campaign_detail.js

// Sample campaign data
const campaignData = {
    id: 1,
    name: 'کمپین فروش تابستان',
    platform: 'instagram',
    type: 'bulk',
    status: 'active',
    startDate: '1405/02/15',
    account: '@my_business_account',
    message: 'سلام {name} عزیز 👋\n\nکمپین فروش تابستانه ما شروع شد!\nتخفیف ویژه تا 50% روی تمام محصولات.\n\nبرای سفارش پیام بدید 🛍️',
    delay: 5,
    maxMessages: 100,
    autoReply: true,
    stats: {
        sent: 1250,
        delivered: 1180,
        read: 890,
        replied: 145,
        failed: 70,
        progress: 75
    },
    recipients: [
        { username: '@user1', status: 'read', sentAt: '10:30', readAt: '10:35', replied: true },
        { username: '@user2', status: 'delivered', sentAt: '10:31', readAt: '-', replied: false },
        { username: '@user3', status: 'sent', sentAt: '10:32', readAt: '-', replied: false },
        { username: '@user4', status: 'failed', sentAt: '10:33', readAt: '-', replied: false },
        { username: '@user5', status: 'replied', sentAt: '10:34', readAt: '10:40', replied: true }
    ],
    activities: [
        { type: 'sent', message: '50 پیام جدید ارسال شد', time: '5 دقیقه پیش' },
        { type: 'reply', message: '12 پاسخ جدید دریافت شد', time: '15 دقیقه پیش' },
        { type: 'delivered', message: '45 پیام تحویل داده شد', time: '30 دقیقه پیش' },
        { type: 'error', message: '3 پیام ناموفق بود', time: '1 ساعت پیش' }
    ]
};

// Load campaign data
function loadCampaignData() {
    // Update title
    document.getElementById('campaignTitle').textContent = campaignData.name;

    // Update status
    const statusBadge = document.getElementById('statusBadge');
    statusBadge.textContent = getStatusText(campaignData.status);
    statusBadge.className = `status-badge ${campaignData.status}`;

    document.getElementById('statusText').textContent = getStatusDescription(campaignData.status);

    // Update progress
    const progress = campaignData.stats.progress;
    document.getElementById('progressFill').style.width = `${progress}%`;
    document.getElementById('progressText').textContent =
        `${campaignData.stats.sent} از ${Math.round(campaignData.stats.sent / progress * 100)} پیام ارسال شده`;

    // Update stats
    document.getElementById('sentCount').textContent = campaignData.stats.sent;
    document.getElementById('deliveredCount').textContent = campaignData.stats.delivered;
    document.getElementById('readCount').textContent = campaignData.stats.read;
    document.getElementById('replyCount').textContent = campaignData.stats.replied;
    document.getElementById('failedCount').textContent = campaignData.stats.failed;

    const successRate = Math.round((campaignData.stats.delivered / campaignData.stats.sent) * 100);
    document.getElementById('successRate').textContent = `${successRate}%`;

    // Update details
    document.getElementById('detailName').textContent = campaignData.name;
    document.getElementById('detailPlatform').textContent = getPlatformText(campaignData.platform);
    document.getElementById('detailType').textContent = getTypeText(campaignData.type);
    document.getElementById('detailStartDate').textContent = campaignData.startDate;
    document.getElementById('detailAccount').textContent = campaignData.account;

    // Update message content
    document.getElementById('messageContent').innerHTML =
        `<p>${campaignData.message.replace(/\n/g, '<br>')}</p>`;

    // Update send settings
    document.getElementById('detailDelay').textContent = `${campaignData.delay} ثانیه`;
    document.getElementById('detailMaxMessages').textContent = `${campaignData.maxMessages} پیام`;
    document.getElementById('detailAutoReply').textContent = campaignData.autoReply ? 'فعال' : 'غیرفعال';

    // Load activities
    loadActivities();

    // Load recipients
    loadRecipients();
}

function loadActivities() {
    const activityList = document.getElementById('activityList');

    activityList.innerHTML = campaignData.activities.map(activity => `
        <div class="activity-item">
            <div class="activity-icon ${activity.type}">
                <i class="fas fa-${getActivityIcon(activity.type)}"></i>
            </div>
            <div class="activity-content">
                <h5>${activity.message}</h5>
                <span class="activity-time">${activity.time}</span>
            </div>
        </div>
    `).join('');
}

function loadRecipients() {
    const tbody = document.getElementById('recipientsTableBody');

    tbody.innerHTML = campaignData.recipients.map(recipient => `
        <tr>
            <td><strong>${recipient.username}</strong></td>
            <td><span class="status-badge ${recipient.status}">${getStatusText(recipient.status)}</span></td>
            <td>${recipient.sentAt}</td>
            <td>${recipient.readAt}</td>
            <td>${recipient.replied ? '<i class="fas fa-check text-success"></i>' : '-'}</td>
            <td>
                <button class="btn-icon" title="مشاهده جزئیات">
                    <i class="fas fa-eye"></i>
                </button>
            </td>
        </tr>
    `).join('');
}

function getStatusText(status) {
    const statusMap = {
        active: 'فعال',
        paused: 'متوقف شده',
        completed: 'تکمیل شده',
        draft: 'پیش‌نویس',
        sent: 'ارسال شده',
        delivered: 'تحویل داده شده',
        read: 'خوانده شده',
        replied: 'پاسخ داده شده',
        failed: 'ناموفق'
    };
    return statusMap[status] || status;
}

function getStatusDescription(status) {
    const descMap = {
        active: 'کمپین در حال اجرا است',
        paused: 'کمپین موقتاً متوقف شده',
        completed: 'کمپین با موفقیت تکمیل شد',
        draft: 'کمپین هنوز شروع نشده'
    };
    return descMap[status] || '';
}

function getPlatformText(platform) {
    const platformMap = {
        instagram: 'اینستاگرام',
        telegram: 'تلگرام',
        whatsapp: 'واتساپ'
    };
    return platformMap[platform] || platform;
}

function getTypeText(type) {
    const typeMap = {
        direct: 'پیام مستقیم',
        bulk: 'ارسال انبوه',
        scheduled: 'زمان‌بندی شده',
        triggered: 'رویداد محور'
    };
    return typeMap[type] || type;
}

function getActivityIcon(type) {
    const iconMap = {
        sent: 'paper-plane',
        reply: 'reply',
        delivered: 'check-circle',
        error: 'exclamation-triangle'
    };
    return iconMap[type] || 'info-circle';
}

// Button actions
document.getElementById('pauseBtn')?.addEventListener('click', () => {
    if (confirm('آیا می‌خواهید این کمپین را متوقف کنید؟')) {
        alert('کمپین متوقف شد');
        location.reload();
    }
});

document.getElementById('stopBtn')?.addEventListener('click', () => {
    if (confirm('آیا می‌خواهید این کمپین را به طور کامل پایان دهید؟ این عمل قابل بازگشت نیست.')) {
        alert('کمپین پایان یافت');
        window.location.href = '/dashboard/messaging/campaigns/';
    }
});

document.getElementById('editBtn')?.addEventListener('click', () => {
    window.location.href = `/dashboard/messaging/campaign/${campaignData.id}/edit/`;
});

// Search and filter
document.getElementById('recipientSearch')?.addEventListener('input', (e) => {
    // Implement search logic
    console.log('Searching:', e.target.value);
});

document.getElementById('recipientStatusFilter')?.addEventListener('change', (e) => {
    // Implement filter logic
    console.log('Filtering by:', e.target.value);
});

// Load data on page load
document.addEventListener('DOMContentLoaded', loadCampaignData);
