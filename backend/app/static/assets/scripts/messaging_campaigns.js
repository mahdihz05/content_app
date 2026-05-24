// static/js/messaging_campaigns.js

const campaignsList = document.getElementById('campaignsList');
const loadingState = document.getElementById('loadingState');

const campaigns = [
    {
        id: 1,
        name: 'کمپین فروش تابستان',
        status: 'active',
        platform: 'instagram',
        messages: 1200,
        success: 94
    },
    {
        id: 2,
        name: 'کمپین معرفی محصول',
        status: 'paused',
        platform: 'telegram',
        messages: 800,
        success: 88
    }
];

function renderCampaigns() {
    loadingState.style.display = 'none';

    if (!campaigns.length) {
        document.getElementById('emptyState').style.display = 'block';
        return;
    }

    campaignsList.innerHTML = campaigns.map(campaign => `
        <div class="campaign-card">
            <div class="campaign-top">
                <div>
                    <h3>${campaign.name}</h3>
                    <span class="campaign-platform">${campaign.platform}</span>
                </div>

                <span class="status-badge ${campaign.status}">
                    ${campaign.status}
                </span>
            </div>

            <div class="campaign-stats">
                <div>
                    <strong>${campaign.messages}</strong>
                    <span>پیام</span>
                </div>

                <div>
                    <strong>${campaign.success}%</strong>
                    <span>موفقیت</span>
                </div>
            </div>

            <div class="campaign-actions">
                <a href="/dashboard/messaging/campaign/${campaign.id}/"
                   class="btn btn-primary">
                   مشاهده
                </a>
            </div>
        </div>
    `).join('');

    document.getElementById('totalCampaigns').textContent = campaigns.length;
}

setTimeout(renderCampaigns, 800);
