// ==================== API CONFIG ====================

const API_BASE = "/messaging/api/";

async function apiRequest(endpoint, options = {}) {

    const response = await fetch(API_BASE + endpoint, {
        credentials: "include",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        ...options
    });

    if (!response.ok) {
        console.error("API ERROR:", response.status, endpoint);
        throw new Error(`API Error ${response.status}`);
    }

    const data = await response.json();

    // اگر pagination فعال باشد
    if (data.results) return data.results;

    return data;
}

function getCSRFToken() {

    const name = "csrftoken";
    const cookies = document.cookie.split(";");

    for (let cookie of cookies) {

        cookie = cookie.trim();

        if (cookie.startsWith(name + "=")) {
            return cookie.substring(name.length + 1);
        }
    }

    return "";
}


// ==================== Simple Chart Library ====================

class SimpleChart {

    constructor(canvasId) {

        this.canvas = document.getElementById(canvasId);

        if (!this.canvas) return;

        this.ctx = this.canvas.getContext("2d");

        this.width = this.canvas.width = this.canvas.offsetWidth;
        this.height = this.canvas.height = this.canvas.offsetHeight;
    }

    drawLineChart(data, labels, options = {}) {

        const padding = 40;
        const chartWidth = this.width - padding * 2;
        const chartHeight = this.height - padding * 2;

        this.ctx.clearRect(0, 0, this.width, this.height);

        const maxValue = Math.max(...data, 1);
        const step = chartWidth / (data.length - 1 || 1);

        this.ctx.strokeStyle = "#e0e0e0";
        this.ctx.lineWidth = 1;

        for (let i = 0; i <= 5; i++) {

            const y = padding + (chartHeight / 5) * i;

            this.ctx.beginPath();
            this.ctx.moveTo(padding, y);
            this.ctx.lineTo(this.width - padding, y);
            this.ctx.stroke();
        }

        this.ctx.strokeStyle = options.color || "#4CAF50";
        this.ctx.lineWidth = 3;

        this.ctx.beginPath();

        data.forEach((value, index) => {

            const x = padding + step * index;
            const y = padding + chartHeight - (value / maxValue) * chartHeight;

            if (index === 0) this.ctx.moveTo(x, y);
            else this.ctx.lineTo(x, y);
        });

        this.ctx.stroke();
    }

    drawPieChart(data, labels, colors) {

        const centerX = this.width / 2;
        const centerY = this.height / 2;
        const radius = Math.min(this.width, this.height) / 2 - 60;

        this.ctx.clearRect(0, 0, this.width, this.height);

        const total = data.reduce((s, v) => s + v, 0) || 1;

        let currentAngle = -Math.PI / 2;

        data.forEach((value, index) => {

            const sliceAngle = (value / total) * Math.PI * 2;

            this.ctx.fillStyle = colors[index];

            this.ctx.beginPath();
            this.ctx.moveTo(centerX, centerY);
            this.ctx.arc(centerX, centerY, radius, currentAngle, currentAngle + sliceAngle);
            this.ctx.closePath();
            this.ctx.fill();

            currentAngle += sliceAngle;
        });
    }
}


// ==================== Dashboard ====================

class MessagingDashboard {

    constructor() {

        this.messagesChart = null;
        this.platformsChart = null;

        this.init();
    }

    async init() {

        this.attachEventListeners();

        await this.loadStats();
        await this.loadActivity();
        await this.initCharts();
    }


    // ==================== STATS ====================

    async loadStats() {

        try {

            const accounts = await apiRequest("accounts/");
            const bulkJobs = await apiRequest("bulk-send/");
            const autoReplyJobs = await apiRequest("auto-reply/");

            const activeAccounts = accounts.filter(a => a.is_active).length;

            const activeCampaigns =
                bulkJobs.filter(j => j.status === "running").length +
                autoReplyJobs.filter(j => j.status === "running").length;

            const today = new Date().toISOString().slice(0, 10);

            let messagesToday = 0;
            let sentTotal = 0;
            let failedTotal = 0;

            bulkJobs.forEach(job => {

                sentTotal += job.sent_count || 0;
                failedTotal += job.failed_count || 0;

                if (job.started_at && job.started_at.startsWith(today)) {
                    messagesToday += job.sent_count || 0;
                }
            });

            const successRate =
                (sentTotal + failedTotal) === 0
                    ? 0
                    : (sentTotal / (sentTotal + failedTotal)) * 100;

            this.updateStats({
                activeAccounts,
                messagesToday,
                activeCampaigns,
                successRate
            });

        } catch (err) {

            console.error("dashboard stats error", err);
        }
    }


    updateStats(stats) {

        this.setValue("active-accounts", stats.activeAccounts);
        this.setValue("messages-today", stats.messagesToday);
        this.setValue("active-campaigns", stats.activeCampaigns);
        this.setValue("success-rate", stats.successRate.toFixed(1) + "%");
    }

    setValue(id, value) {

        const el = document.getElementById(id);

        if (el) el.textContent = value;
    }


    // ==================== ACTIVITY ====================

    async loadActivity() {

        const container = document.getElementById("activity-list");

        try {

            const bulkJobs = await apiRequest("bulk-send/");
            const autoJobs = await apiRequest("auto-reply/");

            const activities = [];

            bulkJobs.slice(0, 5).forEach(job => {

                activities.push({
                    icon: "fa-paper-plane",
                    color: "blue",
                    title: "ارسال انبوه",
                    description: `${job.sent_count || 0} پیام ارسال شده`,
                    time: job.created_at
                });
            });

            autoJobs.slice(0, 5).forEach(job => {

                activities.push({
                    icon: "fa-robot",
                    color: "purple",
                    title: "پاسخگویی خودکار",
                    description: `${job.conversation_count || 0} مکالمه`,
                    time: job.created_at
                });
            });

            activities.sort((a, b) => new Date(b.time) - new Date(a.time));

            container.innerHTML = activities.slice(0, 6).map(a => `
                <div class="activity-item">
                    <div class="activity-icon ${a.color}">
                        <i class="fas ${a.icon}"></i>
                    </div>
                    <div class="activity-content">
                        <div class="activity-title">${a.title}</div>
                        <div class="activity-description">${a.description}</div>
                    </div>
                    <div class="activity-time">
                        ${new Date(a.time).toLocaleString("fa-IR")}
                    </div>
                </div>
            `).join("");

        } catch (err) {

            container.innerHTML = `
            <div class="empty-state">
                <i class="fas fa-inbox"></i>
                <p>فعالیتی یافت نشد</p>
            </div>`;
        }
    }


    // ==================== CHARTS ====================

    async initCharts() {

        const bulkJobs = await apiRequest("bulk-send/");
        const accounts = await apiRequest("accounts/");

        const days = ["شنبه","یکشنبه","دوشنبه","سه‌شنبه","چهارشنبه","پنجشنبه","جمعه"];
        const data = [0,0,0,0,0,0,0];

        bulkJobs.forEach(job => {

            if (!job.started_at) return;

            const d = new Date(job.started_at);
            const day = d.getDay();

            data[day] += job.sent_count || 0;
        });

        this.messagesChart = new SimpleChart("messages-chart");
        this.messagesChart.drawLineChart(data, days, { color:"#2196F3" });

        const platformCount = { telegram:0, whatsapp:0, bale:0 };

        accounts.forEach(a => {

            if (platformCount[a.platform] !== undefined) {
                platformCount[a.platform]++;
            }
        });

        this.platformsChart = new SimpleChart("platforms-chart");

        this.platformsChart.drawPieChart(
            [platformCount.telegram, platformCount.whatsapp, platformCount.bale],
            ["تلگرام","واتساپ","بله"],
            ["#0088cc","#25D366","#00A6FF"]
        );
    }


    // ==================== EVENTS ====================

    attachEventListeners() {

        const btn = document.getElementById("refresh-stats-btn");

        if (btn) {
            btn.addEventListener("click", () => this.refreshDashboard());
        }
    }


    async refreshDashboard() {

        const btn = document.getElementById("refresh-stats-btn");

        if (!btn) return;

        const icon = btn.querySelector("i");

        icon.classList.add("fa-spin");
        btn.disabled = true;

        await this.loadStats();
        await this.loadActivity();
        await this.initCharts();

        icon.classList.remove("fa-spin");
        btn.disabled = false;
    }
}


// ==================== START ====================

document.addEventListener("DOMContentLoaded", () => {
    new MessagingDashboard();
});
