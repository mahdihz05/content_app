document.addEventListener("DOMContentLoaded", () => {
    loadContentItems();
});

async function loadContentItems() {

    try {

        const res = await fetch("/content/api/v1/get-content-items/");
        const result = await res.json();

        if (!result.success) {
            console.error("خطا در دریافت داده");
            return;
        }

        renderContentCards(result.data);

    } catch (err) {
        console.error("API Error:", err);
    }

}


function renderContentCards(campaigns) {

    const grid = document.getElementById("contentGrid");

    if (!campaigns || campaigns.length === 0) {

        const empty = document.createElement("div");
        empty.className = "empty-box";
        empty.innerText = "هیچ محتوایی وجود ندارد";

        grid.appendChild(empty);
        return;
    }

    campaigns.forEach(campaign => {

        const campaignTitle = campaign.campaign_title || "";

        campaign.items.forEach(item => {

            const card = document.createElement("div");
            card.className = "content-card";

            card.innerHTML = `
                <div class="color-line"></div>

                <div class="content-title">
                    ${item.title || ""}
                </div>

                <div class="content-meta">

                    ${campaignTitle ? `
                    <span class="meta-tag">
                        ${campaignTitle}
                    </span>` : ""}

                    ${item.platform ? `
                    <span class="meta-tag">
                        ${item.platform}
                    </span>` : ""}

                    ${item.language ? `
                    <span class="meta-tag">
                        ${item.language}
                    </span>` : ""}

                    ${item.status ? `
                    <span class="meta-tag">
                        ${item.status}
                    </span>` : ""}

                </div>

                <a href="/content/edit/${item.id}/" class="btn-small">
                    ویرایش
                </a>
            `;

            grid.appendChild(card);

        });

    });

}
