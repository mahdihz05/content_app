// مطمئن باش در یک جای مناسب (مثلاً در create_content_api.js) این آبجکت مقداردهی می‌شود
window.ContentFlowState = window.ContentFlowState || {
    currentStep: 1,
};

/* ---------------------------
   Init
---------------------------- */
document.addEventListener("DOMContentLoaded", async () => {
    setupStepperUI();
    await initStep1();  // بارگذاری کمپین‌ها
    await initStep2();  // بارگذاری پلتفرم‌ها و goals
});

/* ---------------------------
   Stepper UI Helpers
---------------------------- */
function setCurrentStep(step) {
    window.ContentFlowState.currentStep = step;

    // نمایش/مخفی کردن سکشن‌ها
    document.querySelectorAll(".step-section").forEach((sec) => {
        const id = sec.id; // مثلاً "step-1"
        const secStep = parseInt(id.split("-")[1], 10);
        sec.classList.toggle("hidden", secStep !== step);
    });

    // فعال کردن در stepper
    document.querySelectorAll(".step-item").forEach((item) => {
        const s = parseInt(item.getAttribute("data-step"), 10);
        item.classList.toggle("active", s <= step); // steps قبلی + جاری active
    });

    // در HTML:
    // 5: تحقیق اولیه (AI)
    // 6: پایگاه دانش
    // 7: تایید محتوا  => خلاصه
    // 8: خروجی نهایی => خروجی
    if (step === 7) {
        renderContentSummary();
    }
    if (step === 8) {
        renderFinalOutput();
    }
}

function setupStepperUI() {
    // دکمه‌های "بازگشت" generic
    document.querySelectorAll("button[data-prev-step]").forEach((btn) => {
        btn.addEventListener("click", () => {
            const prev = parseInt(btn.getAttribute("data-prev-step"), 10);
            setCurrentStep(prev);
        });
    });
}

/* ---------------------------
   STEP 1 - انتخاب کمپین
---------------------------- */
async function initStep1() {
    try {
        const res = await apiFetchCampaignList();
        const list = res.data || [];
        const tbody = document.getElementById("campaignTableBody");
        tbody.innerHTML = "";

        list.forEach((c) => {
            const tr = document.createElement("tr");
            tr.innerHTML = `
                <td>
                    <button class="btn-primary btn-sm" data-campaign-id="${c.id}">
                        انتخاب
                    </button>
                </td>
                <td>${c.title || "-"}</td>
                <td>${c.main_keywords || "-"}</td>
                <td>${c.status || "-"}</td>
            `;
            tbody.appendChild(tr);
        });

        tbody.addEventListener("click", (e) => {
            const btn = e.target.closest("button[data-campaign-id]");
            if (!btn) return;

            const id = parseInt(btn.getAttribute("data-campaign-id"), 10);
            window.ContentFlowState.selectedCampaign = id;

            // دکمه ادامه را فعال کن
            document.getElementById("goToStep2Btn").disabled = false;
        });

        document.getElementById("goToStep2Btn").addEventListener("click", () => {
            if (!window.ContentFlowState.selectedCampaign) {
                alert("لطفاً یک کمپین انتخاب کنید.");
                return;
            }
            setCurrentStep(2);
        });

        setCurrentStep(1);
    } catch (err) {
        console.error(err);
        alert("خطا در بارگذاری کمپین‌ها");
    }
}

/* ---------------------------
   STEP 2 - اطلاعات پایه + ایجاد ContentItem
---------------------------- */
async function initStep2() {
    // رندر کارت‌های پلتفرم از PLATFORMS
    const platformGrid = document.getElementById("platformGrid");
    platformGrid.innerHTML = "";
    (PLATFORMS || []).forEach((p) => {
        const div = document.createElement("div");
        div.className = "card-item";
        div.dataset.platformId = p.id;
        div.innerHTML = `
            <div class="card-item-title">${p.name}</div>
        `;
        platformGrid.appendChild(div);
    });

    platformGrid.addEventListener("click", (e) => {
        const card = e.target.closest(".card-item");
        if (!card) return;

        document
            .querySelectorAll("#platformGrid .card-item")
            .forEach((c) => c.classList.remove("active"));

        card.classList.add("active");

        const platformId = parseInt(card.dataset.platformId, 10);
        const platformName = card.querySelector(".card-item-title")?.innerText || "";

        window.ContentFlowState.selectedPlatform = platformId;
        window.ContentFlowState.selectedPlatformName = platformName;
    });

    // بارگذاری goals از API
    try {
        const res = await apiFetchGoalList();
        const goals = res.data || [];
        const goalGrid = document.getElementById("goalGrid");
        goalGrid.innerHTML = "";

        goals.forEach((g) => {
            const div = document.createElement("div");
            div.className = "card-item";
            div.dataset.goalId = g.id;
            div.innerHTML = `
                <div class="card-item-title">${g.goal}</div>
                <div class="card-item-desc">
                    ${g.short_description || g.description || ""}
                </div>
            `;
            goalGrid.appendChild(div);
        });

        goalGrid.addEventListener("click", (e) => {
            const card = e.target.closest(".card-item");
            if (!card) return;

            document
                .querySelectorAll("#goalGrid .card-item")
                .forEach((c) => c.classList.remove("active"));
            card.classList.add("active");

            window.ContentFlowState.selectedGoal = parseInt(card.dataset.goalId, 10);
        });
    } catch (err) {
        console.error(err);
        alert("خطا در بارگذاری اهداف");
    }

    // هندل submit فرم اطلاعات پایه
    const basicForm = document.getElementById("basicContentForm");
    basicForm.addEventListener("submit", async (e) => {
        e.preventDefault();

        const st = window.ContentFlowState;
        if (!st.selectedCampaign) {
            alert("ابتدا یک کمپین انتخاب کنید.");
            setCurrentStep(1);
            return;
        }
        if (!st.selectedPlatform) {
            alert("لطفاً یک پلتفرم انتخاب کنید.");
            return;
        }
        if (!st.selectedGoal) {
            alert("لطفاً یک هدف انتخاب کنید.");
            return;
        }

        // ذخیره داده فرم در state
        const fd = new FormData(basicForm);
        st.basicContentData = {
            title: fd.get("title") || "",
            main_keyword: fd.get("main_keyword") || "",
            additional_keywords: fd.get("additional_keywords") || "",
            description: fd.get("description") || "",
            language: fd.get("language") || "fa",
        };

        try {
            // ایجاد ContentItem در بک‌اند
            await apiCreateContentItem();
            // گرفتن schema و ساخت فرم
            await loadDynamicFormForStep3();
            // حرکت به مرحله ۳
            setCurrentStep(3);
        } catch (err) {
            console.error(err);
            alert(err.message || "خطا در ایجاد آیتم محتوا");
        }
    });
}

/* ---------------------------
   STEP 3 - فرم داینامیک پلتفرم
---------------------------- */
async function loadDynamicFormForStep3() {
    try {
        const res = await apiFetchPlatformFormSchema();
        if (!res.success || !res.data || !res.data.length) {
            alert("هیچ اسکیما برای این پلتفرم یافت نشد.");
            return;
        }
        const schemaObj = res.data[0].schema;
        renderDynamicFormFromSchema(schemaObj);
    } catch (err) {
        console.error(err);
        alert("خطا در دریافت اسکیما فرم پلتفرم");
    }
}

(function setupStep3Handler() {
    const form = document.getElementById("dynamicPlatformForm");
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const st = window.ContentFlowState;

        if (!st.contentItemId) {
            alert("ContentItem هنوز ساخته نشده است.");
            setCurrentStep(2);
            return;
        }

        // داده فرم داینامیک را در state ذخیره کن
        st.dynamicFormData = collectDynamicFormData();

        try {
            await apiSavePlatformFormData();
            setCurrentStep(4); // بعد از ذخیره موفق، برو مرحله ۴ (کلیدواژه‌ها)
        } catch (err) {
            console.error(err);
            alert(err.message || "خطا در ذخیره داده فرم پلتفرم");
        }
    });
})();

/* ---------------------------
   STEP 4 - کلیدواژه‌ها
   (اگر خواستی فعالش کن)
---------------------------- */
// (function setupStep4Handler() {
//     const form = document.getElementById("keywordsForm");
//     if (!form) return;
//
//     form.addEventListener("submit", handleKeywordFormSubmit);
// })();
//
// async function handleKeywordFormSubmit(e) {
//     e.preventDefault();
//
//     if (window._savingKeywords) return;
//     window._savingKeywords = true;
//
//     window.ContentFlowState.keywordsData = {
//         primary_keywords: [...window.KeywordStore.primary],
//         secondary_keywords: [...window.KeywordStore.secondary],
//     };
//
//     try {
//         await apiSaveKeywords();
//         setCurrentStep(5); // بعد از ذخیره، برو مرحله ۵ (تحقیق AI)
//     } catch (err) {
//         console.error(err);
//         alert(err.message || "خطا در ذخیره کلیدواژه‌ها");
//     } finally {
//         window._savingKeywords = false;
//     }
// }

/* ---------------------------
   STEP 5 - Research Step (AI)
---------------------------- */
(function setupStep5ResearchHandler() {

    const startBtn = document.getElementById("startResearchBtn");
    const fetchSelectedBtn = document.getElementById("fetchSelectedResearchBtn");
    const finalizeBtn = document.getElementById("finalizeResearchBtn");
    const container = document.getElementById("researchQueryList");

    if (!startBtn || !fetchSelectedBtn || !finalizeBtn || !container) return;

    /* ----------------------------------------------------
       1) تولید عناوین جست‌وجو
    ---------------------------------------------------- */
    startBtn.addEventListener("click", async () => {

        startBtn.innerText = "در حال تولید...";
        startBtn.disabled = true;

        try {

            const queries = await apiGenerateSearchQueries();

            container.innerHTML = queries
                .map(q => `
                    <div class="research-card" data-id="${q.id}">
                        <div class="card-title">${q.title}</div>
                        <div class="card-description">برای انتخاب کلیک کنید</div>
                    </div>
                `)
                .join("");

            document.querySelectorAll(".research-card").forEach(card => {

                card.addEventListener("click", () => {
                    card.classList.toggle("selected");
                    updateFetchButtonState();
                });

            });

            fetchSelectedBtn.classList.remove("hidden");

        } catch (err) {

            console.error(err);
            alert("خطا در تولید عناوین جست‌وجو");

        } finally {

            startBtn.innerText = "تولید عناوین جست‌وجو با AI";
            startBtn.disabled = false;

        }

    });

    function updateFetchButtonState() {
        const selectedCards = document.querySelectorAll(".research-card.selected");
        fetchSelectedBtn.disabled = (selectedCards.length === 0);
    }

    /* ----------------------------------------------------
       Accordion toggle
    ---------------------------------------------------- */
    function toggleSource(el){
        const body = el.nextElementSibling;
        body.classList.toggle("open");
    }

    /* ----------------------------------------------------
       HTML escape (برای امنیت)
    ---------------------------------------------------- */
    function escapeHtml(str){
        const div = document.createElement("div");
        div.innerText = str;
        return div.innerHTML;
    }

    /* ----------------------------------------------------
       Render Sources UI
    ---------------------------------------------------- */
    function renderSources(sources){

        return sources.map((s,i)=>`

            <div class="source-item">

                <div class="source-header" onclick="this.classList.toggle('active'); this.nextElementSibling.classList.toggle('open');">
                    <div class="source-title">
                        ${i+1}. ${escapeHtml(s.title)}
                    </div>

                    <div class="source-url">
                        <a href="${s.url}" target="_blank">${s.url}</a>
                    </div>

                    <div class="source-toggle">▼</div>
                </div>

                <div class="source-body">
                    <div class="source-html">
                        ${s.raw_html}
                    </div>
                </div>

            </div>

        `).join("");

    }

    /* ----------------------------------------------------
       2) دریافت منابع تحقیق
    ---------------------------------------------------- */
    fetchSelectedBtn.addEventListener("click", async () => {

        fetchSelectedBtn.innerText = "در حال دریافت...";
        fetchSelectedBtn.disabled = true;

        const selectedIds = Array.from(
            document.querySelectorAll(".research-card.selected")
        ).map(card => card.dataset.id);

        if (!selectedIds.length) {
            alert("حداقل یک مورد را انتخاب کنید");
            resetFetchBtn();
            return;
        }

        try {

            for (let sourceId of selectedIds) {

                const card = document.querySelector(`.research-card[data-id="${sourceId}"]`);
                if (!card) continue;

                card.classList.add("loading");

                card.insertAdjacentHTML(
                    "beforeend",
                    `<div class="loading-spinner"></div>`
                );

                await apiSelectResearchSource(sourceId);

                const res = await apiFetchResearchSourceData(sourceId);

                card.classList.remove("loading");

                const spinner = card.querySelector(".loading-spinner");
                if (spinner) spinner.remove();

                const data = res.data;

                let sources = [];
                let summary = "";

                if(data.sources){
                    sources = data.sources;
                }else if(data.raw_text){
                    try{
                        const parsed = JSON.parse(data.raw_text);
                        sources = parsed.sources || [];
                        summary = parsed.summary?.paragraph || "";
                    }catch(e){}
                }

                summary = data.summary || summary;

                card.insertAdjacentHTML(
                    "beforeend",
                    `
                    <div class="research-details">

                        <div class="research-summary-box">
                            <div class="summary-title">خلاصه تحقیق</div>
                            <p>${summary}</p>
                        </div>

                        <div class="sources-container">
                            ${renderSources(sources)}
                        </div>

                    </div>
                    `
                );

                card.classList.add("expanded");

            }

            finalizeBtn.classList.remove("hidden");
            fetchSelectedBtn.classList.add("hidden");

        } catch (err) {

            console.error(err);
            alert("خطا در دریافت داده منابع");

        } finally {

            resetFetchBtn();

        }

    });

    function resetFetchBtn() {
        fetchSelectedBtn.innerText = "دریافت اطلاعات انتخاب‌شده";
        fetchSelectedBtn.disabled = false;
    }

    /* ----------------------------------------------------
       3) نهایی‌سازی تحقیق
    ---------------------------------------------------- */
    finalizeBtn.addEventListener("click", async () => {

        try {

            const results = await apiFinalizeResearch();

            console.log("FINAL RESEARCH RESULTS:", results);

            setCurrentStep(6);

        } catch (err) {

            console.error(err);
            alert("خطا در نهایی‌سازی تحقیق");

        }

    });

})();


/* ---------------------------
   STEP 6 - پایگاه دانش
---------------------------- */
(function setupStep6KnowledgeBaseHandler() {
    const form = document.getElementById("knowledgeBaseForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
        e.preventDefault();

        const fd = new FormData(form);
        const selectedKBs = fd.getAll("kb"); // لیست value چک‌باکس‌های تیک‌خورده

        if (!selectedKBs.length) {
            alert("لطفاً حداقل یک پایگاه دانش انتخاب کنید.");
            return;
        }

        window.ContentFlowState.knowledgeBaseData = {
            knowledge_bases: selectedKBs,
        };

        try {
            // اگر API اختصاصی داری، اینجا صدا بزن:
            // await apiSaveKnowledgeBase();
            // setCurrentStep(7);

            // نسخه مبتنی بر API که خودت دادی:
            const st = window.ContentFlowState;
            const contentId = st.contentItemId;
            if (!contentId) {
                alert("شناسه محتوا یافت نشد!");
                return;
            }

            const response = await fetch(`/content/api/v1/add_source_to_content_item/`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": getCookie("csrftoken") || ""
                },
                body: JSON.stringify({
                    selected_kb: selectedKBs,
                    contentItem_id: contentId
                })
            });

            if (!response.ok) {
                console.error("HTTP Error:", response.status, response.statusText);
                alert("خطا در ارتباط با سرور هنگام ذخیره پایگاه دانش.");
                return;
            }

            const result = await response.json();
            console.log("Saved KB:", result);

            const success =
                result &&
                (result.success === true ||
                 result.success === "true" ||
                 result.status === "ok" ||
                 result.status === true);

            if (!success) {
                alert("خطا در ذخیره پایگاه دانش!");
                return;
            }

            // ذخیره موفق → برو به مرحله ۷ (تایید محتوا)
            setCurrentStep(7);
        } catch (err) {
            console.error(err);
            alert("خطا در ذخیره پایگاه دانش");
        }
    });
})();

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let cookie of cookies) {
            cookie = cookie.trim();
            if (cookie.startsWith(name + "=")) {
                cookieValue = cookie.substring(name.length + 1);
                break;
            }
        }
    }
    return cookieValue;
}

/* ---------------------------
   STEP 7 - تایید محتوا (خلاصه)
---------------------------- */
function renderContentSummary() {
    const st = window.ContentFlowState;
    const box = document.getElementById("contentSummaryBox");
    if (!box) return;

        box.innerHTML = `
            <div class="summary-card">

            <div class="summary-header">
            <h3 class="summary-title">مرور تنظیمات محتوا</h3>
            </div>

            <div class="summary-grid">

            <div class="summary-item">
            <span class="label">کمپین</span>
            <span class="value">${st.selectedCampaign || "-"}</span>
            </div>

            <div class="summary-item">
            <span class="label">پلتفرم</span>
            <span class="value">${st.selectedPlatformName || "-"}</span>
            </div>

            <div class="summary-item">
            <span class="label">هدف</span>
            <span class="value">${st.selectedGoal || "-"}</span>
            </div>

            <div class="summary-item">
            <span class="label">عنوان محتوا</span>
            <span class="value">${st.basicContentData?.title || "-"}</span>
            </div>

            </div>

            <div class="keywords-box">

            <span class="label">کلیدواژه‌ها</span>

            <div class="keywords-list">
            ${(st.keywordsData?.primary_keywords || [])
            .map(k => `<span class="keyword-chip">${k}</span>`)
            .join("")}
            </div>

            </div>

            <div id="outlinePreviewBox" class="outline-preview">

            <div class="outline-placeholder">
            برای تولید ساختار مقاله روی دکمه زیر کلیک کنید
            </div>

            </div>

            </div>
        `;
};
/* ============================================================
   رندر خروجی نهایی مرحله ۸ (نسخه مینیمال و زیبا)
============================================================ */
function renderFinalOutput() {
    const state = window.ContentFlowState;
    const data = state.finalGeneratedContent;
    if (!data) return;

    const box = document.getElementById("finalOutputBox");
    const empty = document.getElementById("finalEmptyState");
    if (empty) empty.classList.add("hidden");

    const meta = data.meta || {};
    const html = data.html || "";
    const images = Array.isArray(data.images) ? data.images : [];

    // بیلد سکشن پرامپت‌ها
    let imagePromptsHTML = "";
    if (images.length > 0) {
        imagePromptsHTML = `
            <div class="image-prompts">
                <h4>پرامپت‌های تصاویر</h4>
                <ul>
                    ${images.map(p => `<li>${p}</li>`).join("")}
                </ul>
            </div>
        `;
    }

    // بیلد خروجی اصلی
    box.innerHTML = `
        <div class="output-rendered-content">

            <div class="seo-box">
                <h4>اطلاعات سئو</h4>
                <p><strong>Title:</strong> ${meta.title || "—"}</p>
                <p><strong>Description:</strong> ${meta.description || "—"}</p>
            </div>

            <div class="article-preview">
                <article>${html}</article>
            </div>

            ${imagePromptsHTML}
        </div>
    `;

    setupFinalActions(data);
}

function setupFinalActions(data) {
    const meta = data.meta || {};
    const html = data.html || "";
    const images = Array.isArray(data.images) ? data.images : [];

    const safeAlert = msg => {
        const toast = document.createElement("div");
        toast.textContent = msg;
        toast.className = "ai-toast";
        document.body.appendChild(toast);
        setTimeout(() => toast.remove(), 2500);
    };

    // کپی محتوا
    const copyBtn = document.getElementById("copyFinalContentBtn");
    if (copyBtn) copyBtn.onclick = () => {
        navigator.clipboard.writeText(html);
        safeAlert("✅ محتوای مقاله کپی شد");
    };

    // دانلود HTML
    const downloadBtn = document.getElementById("downloadHTMLBtn");
    if (downloadBtn) downloadBtn.onclick = () => {
        const fileHTML = `
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>${meta.title || ""}</title>
<meta name="description" content="${meta.description || ""}">
</head>
<body>
${html}
</body>
</html>
        `;
        const blob = new Blob([fileHTML], { type: "text/html" });
        const url = URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        a.download = "article.html";
        a.click();
        URL.revokeObjectURL(url);
        safeAlert("⬇️ فایل HTML دانلود شد");
    };

    // کپی متا
    const metaBtn = document.getElementById("copyMetaBtn");
    if (metaBtn) metaBtn.onclick = () => {
        const text = `Title: ${meta.title}\nDescription: ${meta.description}`;
        navigator.clipboard.writeText(text);
        safeAlert("📝 متا کپی شد");
    };

    // کپی پرامپت تصاویر
    const promptBtn = document.getElementById("copyImagePromptsBtn");
    if (promptBtn) promptBtn.onclick = () => {
        if (!images.length) {
            safeAlert("⚠️ پرامپتی وجود ندارد");
            return;
        }
        navigator.clipboard.writeText(images.join("\n\n"));
        safeAlert("🎨 پرامپت‌های تصاویر کپی شد");
    };
}


/* ============================================================
   هندل مرحله ۷ → رفتن به مرحله ۸ + تولید محتوا
============================================================ */

(function setupStep7Handler() {
    const btn = document.getElementById("confirmContentBtn");
    if (!btn) return;

    btn.addEventListener("click", async function () {
        btn.disabled = true;
        const original = btn.textContent;
        btn.textContent = "در حال تولید مقاله نهایی...";

        try {
            const final = await apiGenerateFinalContentAI();
            window.ContentFlowState.finalGeneratedContent = final;

            document.getElementById("step-6").classList.add("hidden");
            document.getElementById("step-7").classList.add("hidden");
            document.getElementById("step-8").classList.remove("hidden");

            window.scrollTo(0, 0);

            renderFinalOutput();

        } catch (err) {
            console.error(err);
            alert(err.message || "خطا در تولید محتوا");

            document.getElementById("step-8").classList.add("hidden");
            document.getElementById("step-7").classList.remove("hidden");

        } finally {
            btn.disabled = false;
            btn.textContent = original;
        }
    });
})();
