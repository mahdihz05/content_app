/* Campaign List Script - AI Minimal Design */

const baseUrl = "/campaign/api/v1";
const grid = document.getElementById("campaignGrid");

const fallbackCampaigns = [
    { id: 1, title: "کمپین سئو فروشگاه", status: "active" },
    { id: 2, title: "کمپین محتوای بلاگ", status: "draft" },
    { id: 3, title: "کمپین شبکه اجتماعی", status: "active" }
];

window.onload = loadCampaigns;

/* LOAD CAMPAIGN LIST */

async function loadCampaigns() {
    try {
        const res = await fetch(`${baseUrl}/campaign_list`, {
            method: "GET",
            credentials: "include"
        });

        const data = await res.json();

        if (data.success) {
            renderCampaigns(data.data);
        } else {
            renderCampaigns(fallbackCampaigns);
        }

    } catch (error) {
        renderCampaigns(fallbackCampaigns);
    }
}

/* RENDER CARDS */

function renderCampaigns(campaigns) {
    grid.innerHTML = "";

    /* ADD NEW CAMPAIGN CARD */

    grid.innerHTML += `
        <div class="campaign-card add-card" onclick="createCampaign()">
            +
            <span>ایجاد کمپین جدید</span>
        </div>
    `;

    /* EXISTING CAMPAIGNS */

    campaigns.forEach(c => {

        let statusClass = "status-draft";
        let statusText = "پیش‌نویس";

        if (c.status === "active") {
            statusClass = "status-active";
            statusText = "فعال";
        }

        const card = document.createElement("div");
        card.className = "campaign-card";

        card.innerHTML = `
            <h3>${c.title}</h3>
            <div class="campaign-status ${statusClass}">
                ${statusText}
            </div>
        `;

        card.onclick = () => {
            window.location.href = `/dashboard/campaign/content-items/${c.id}/`;
        };

        grid.appendChild(card);
    });
}

/* REDIRECT TO CREATE PAGE */

function createCampaign() {
    window.location.href = "/dashboard/create-campaign";
}
