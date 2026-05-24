// این فایل فقط مسئول:
// - نگه داشتن state
// - زدن درخواست‌های API
// - برگرداندن Promise به سایر اسکریپت‌هاست

// ---------------------
// Global State
// ---------------------
window.ContentFlowState = {
    currentStep: 1,
    selectedCampaign: null,
    selectedPlatform: null,
    selectedGoal: null,
    contentItemId: null,       // بعد از ساخت ContentItem ست می‌شود
    basicContentData: {},      // اطلاعات پایه مرحله ۲
    dynamicFormData: {},       // داده فرم پلتفرم (مرحله ۳)
    keywordsData: {},          // مرحله ۴
    knowledgeBaseData: {},     // مرحله ۵
    finalGeneratedContent: "", // خروجی مرحله ۷
};

// ---------------------
// Helper: CSRF
// ---------------------
function getCSRFToken() {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
        const cookies = document.cookie.split(";");
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.startsWith("csrftoken=")) {
                cookieValue = cookie.substring("csrftoken=".length, cookie.length);
                break;
            }
        }
    }
    return cookieValue;
}

// ---------------------
// API 1: دریافت لیست کمپین‌ها
// ---------------------
async function apiFetchCampaignList() {
    // به این URL درخواست GET می‌زند:
    // /campaign/api/v1/get-campaign-list
    // انتظار پاسخ:
    // {
    //   success: true,
    //   data: [
    //     { id, title, main_keywords, status, ... },
    //     ...
    //   ]
    // }
    const res = await fetch("/campaign/api/v1/campaign_list");
    if (!res.ok) {
        throw new Error(`خطا در دریافت لیست کمپین‌ها: ${res.status}`);
    }
    const data = await res.json();
    return data;
}

// ---------------------
// API 2: دریافت لیست Goals
// ---------------------
async function apiFetchGoalList() {
    // به این URL درخواست GET می‌زند:
    // /campaign/api/v1/get_goal_list
    // انتظار پاسخ:
    // {
    //   success: true,
    //   data: [
    //     { id, goal, short_description, description },
    //     ...
    //   ]
    // }
    const res = await fetch("/campaign/api/v1/get_goal_list");
    if (!res.ok) {
        throw new Error(`خطا در دریافت لیست اهداف: ${res.status}`);
    }
    const data = await res.json();
    return data;
}

// ---------------------
// API 3: ایجاد ContentItem
// ---------------------
async function apiCreateContentItem() {
    const st = window.ContentFlowState;

    const payload = {
        campaign_id: st.selectedCampaign,
        platform: st.selectedPlatform,
        goal: st.selectedGoal,   // با ویوی Django تو هماهنگ شد
        title: st.basicContentData.title,
        main_keyword: st.basicContentData.main_keyword,
        additional_keywords: st.basicContentData.additional_keywords,
        description: st.basicContentData.description,
        language: st.basicContentData.language,
    };

    const res = await fetch("/content/api/v1/create/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(payload),
    });

    const data = await res.json();

    console.log("CREATE CONTENT RESPONSE:", data);

    if (!data.success) {
        throw new Error(data.error || "خطا در ایجاد آیتم محتوا");
    }

    // مقاوم در برابر ساختارهای مختلف پاسخ
    const contentId =
        data?.data?.content_item_id ||
        data?.content_item_id ||
        data?.data?.id ||
        data?.id ||
        null;

    if (!contentId) {
        console.warn("content_item_id در پاسخ API پیدا نشد");
    }

    window.ContentFlowState.contentItemId = contentId;

    return data;
}

// ---------------------
// API 4: دریافت schema فرم پلتفرم
// ---------------------
async function apiFetchPlatformFormSchema() {
    const platformId = window.ContentFlowState.selectedPlatform;

    // GET به:
    // /content/api/v1/get_form_schema/?platform_id=<platformId>
    //
    // انتظار پاسخ:
    // {
    //   success: true,
    //   data: [
    //     {
    //       id: ...,
    //       schema: {
    //          fields: [
    //             { name, label, type, required, options? },
    //             ...
    //          ]
    //       },
    //       ...
    //     }
    //   ]
    // }

    const res = await fetch(`/content/api/v1/get_form_schema/?platform_id=${platformId}`);
    if (!res.ok) {
        throw new Error(`خطا در دریافت اسکیما فرم پلتفرم: ${res.status}`);
    }
    const data = await res.json();
    return data;
}

// ---------------------
// API 5: ذخیره داده فرم پلتفرم
// ---------------------
async function apiSavePlatformFormData() {
    const platformId = window.ContentFlowState.selectedPlatform;
    const st = window.ContentFlowState;
    const payload = {
        content_item_id: st.contentItemId,
        platform_id:platformId,
        form_data: st.dynamicFormData,
    };

    // POST به:
    // /content/api/v1/save_content_form/
    //
    // بدنه:
    // {
    //   "content_item_id": ...,
    //   "form_data": { ... }
    // }
    //
    // پاسخ:
    // { success: true/false, ... }

    const res = await fetch("/content/api/v1/save_content_form/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!data.success) {
        throw new Error(data.error || "خطا در ذخیره فرم پلتفرم");
    }
    const contentFormId = data.data.content_form_id
    window.ContentFlowState.contentFormId = contentFormId
    window.globalStore = {};
    window.globalStore.form_data = contentFormId
    console.log(window.globalStore.form_data)
    console.log(data.data)
    return data;
}

// ---------------------
// API 6: ذخیره کلیدواژه‌ها (در صورت داشتن API خاص)
// ---------------------
// اگر API جداگانه داری اینجا تعریف کن، فعلاً Mock:
async function apiSaveKeywords() {
    // اینجا می‌توانی به یک API واقعی مانند:
    // POST /content/api/v1/save_keywords/
    // payload = {
    //    content_item_id,
    //    primary_keywords: [...],
    //    secondary_keywords: [...]
    // }
    //
    // فعلاً فقط Promise resolve می‌دهیم:
    return Promise.resolve({ success: true });
}

// ---------------------
// API 7: ذخیره پایگاه دانش (در صورت داشتن API خاص)
// ---------------------
async function apiSaveKnowledgeBase() {
    // مشابه بالا می‌توانی API واقعی بزنی
    return Promise.resolve({ success: true });
}

// ---------------------
// API 8: تایید و تولید محتوا (مثلاً call به LLM)
// ---------------------
async function apiGenerateFinalContent() {
    const st = window.ContentFlowState;

    // اگر API داری مثل:
    // POST /content/api/v1/generate/
    // payload = { content_item_id: ... }
    //
    // انتظار پاسخ:
    // { success: true, data: { generated_content: "..." } }

    // فعلاً Mock:
    const fakeContent = `
        این یک متن نمونه از محتوای تولید شده برای
        "${st.basicContentData.title}"
        روی پلتفرم ${st.selectedPlatform} است.
    `.trim();

    return Promise.resolve({
        success: true,
        data: { generated_content: fakeContent },
    });
}
// ---------------------
// API 9: دریافت پیشنهاد کلیدواژه از AI (Final & Clean)
// ---------------------
// ---------------------
// API: دریافت پیشنهاد کلیدواژه (نسخه نهایی بدون regex)
// ---------------------
async function apiGenerateKeywordSuggestions() {

    const st = window.ContentFlowState;

    if (!st.contentFormId) {
        throw new Error("contentFormId is missing");
    }

    const payload = {
        content_id: st.contentItemId,
        content_form_id: st.contentFormId,
    };

    const res = await fetch("/content/api/v1/generate_keyword/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(payload),
    });

    const json = await res.json();

    if (!json.success) {
        throw new Error(json.error || "خطا در دریافت پیشنهاد کلیدواژه");
    }

    // حالا خروجی همیشه JSON واقعی است
    return json.data;
}



// ---------------------
// API 6: ذخیره کلیدواژه‌ها (نسخه کامل و واقعی)
// ---------------------
async function apiSaveKeywords() {
    const st = window.ContentFlowState;

    const keywords = [];

    (st.keywordsData.primary_keywords || []).forEach((kw) => {
        keywords.push({
            keyword: kw,
            source: "primary",
            is_proccessed: false,
        });
    });

    (st.keywordsData.secondary_keywords || []).forEach((kw) => {
        keywords.push({
            keyword: kw,
            source: "secondary",
            is_proccessed: false,
        });
    });

    const payload = {
        content_item_id: st.contentItemId,
        keywords: keywords
    };

    console.log("FINAL PAYLOAD → ", payload);

    const res = await fetch("/content/api/v1/bulk_create_keywords/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(payload)
    });

    return await res.json();
}


//===============================================================
// add source to content item
//===============================================================

document.getElementById("knowledgeBaseForm").addEventListener("submit", async function(e) {
    e.preventDefault();

    // جمع کردن چک‌باکس‌های انتخاب‌شده
    const selected = [];
    document.querySelectorAll('input[name="kb"]:checked').forEach(cb => {
        selected.push(cb.value);
    });
    const st = window.ContentFlowState;
    // دریافت contentItemId از state
    const contentId = st.contentItemId;

    if (!contentId) {
        alert("شناسه محتوا یافت نشد!");
        return;
    }

    const response = await fetch(`/content/api/v1/add_source_to_content_item/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie("csrftoken")  // اگر csrf_exempt حذف شد لازم میشه
        },
        body: JSON.stringify({
            selected_kb: selected,
            contentItem_id: contentId
        })
    });

    const result = await response.json();
    console.log("Saved:", result);

    if (result.success === true) {
        // پیام موفقیت
//        alert("منابع با موفقیت ذخیره شد.");

        // رفتن به مرحله ۶
        document.getElementById("step-5").classList.add("hidden");
        document.getElementById("step-6").classList.remove("hidden");
    } else {
        alert("خطا در ذخیره منابع!");
    }
});


// اگر لازم بود CSRF را بخوانی (در صورتی که csrf_exempt برداشته شود)
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




//=====================================
// API 7. search and ai box
//=====================================
// -------------------------
// RESEARCH STEP APIs
// -------------------------

async function apiGenerateSearchQueries() {
    const st = window.ContentFlowState;

    const countInput = document.getElementById("researchQueryCount");

    let count = 5;

    if (countInput && countInput.value) {
        count = parseInt(countInput.value);
    }

    // گرفتن کوئری‌های موجود برای جلوگیری از تکرار
    const existingQueries = [];

    document.querySelectorAll(".research-card .card-title").forEach(el => {
        existingQueries.push(el.innerText.trim());
    });

    const res = await fetch(`/research/api/v1/ai/research/${st.contentItemId}/generate-queries/`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
            count: count,
            existing_queries: existingQueries
        })
    });

    const json = await res.json();

    if (!json.success) throw new Error(json.error);

    return json.data.queries;
}


async function apiSelectResearchSource(sourceId) {

    const res = await fetch(`/research/api/v1/ai/research/source/${sourceId}/select/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    });

    return await res.json();
}


async function apiFetchResearchSourceData(sourceId) {

    const res = await fetch(`/research/api/v1/ai/research/source/${sourceId}/fetch/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    });

    return await res.json();
}


async function apiFinalizeResearch() {
    const st = window.ContentFlowState;

    const res = await fetch(`/research/api/v1/ai/research/${st.contentItemId}/finalize/`, {
        method: "POST",
        headers: { "X-CSRFToken": getCSRFToken() }
    });

    const json = await res.json();

    if (!json.success) throw new Error(json.error);

    return json.data.research;
}


// ---------------------
// API: تولید Outline مرحله 7
// ---------------------
async function apiGenerateOutline() {
    const st = window.ContentFlowState;

    const payload = {
        content_id: st.contentItemId,
    };

    const res = await fetch("/content/api/v1/generate_outline/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(payload)
    });

    const json = await res.json();
    if (!json.success) throw new Error(json.error);

    return json.data.outline;
}

// ---------------------
// API: تولید محتوای نهایی (مرحله 8)
// ---------------------
// ---------------------
// API: Final Content
// ---------------------
async function apiGenerateFinalContentAI() {
    const st = window.ContentFlowState;

    const payload = {
        content_id: st.contentItemId
    };

    const res = await fetch("/content/api/v1/generate_final_content/", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify(payload)
    });

    const json = await res.json();
    if (!json.success) throw new Error(json.error);

    return json.data.content; // ← شامل meta / html / images
}
