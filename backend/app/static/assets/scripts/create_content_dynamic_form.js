// مسئول ساخت و خواندن فرم داینامیک مرحله ۳

// ساخت فیلدها از روی schema
function renderDynamicFormFromSchema(schemaObj) {
    const container = document.getElementById("dynamicFormFields");
    container.innerHTML = "";

    if (!schemaObj || !schemaObj.fields) return;

    schemaObj.fields.forEach((field) => {
        let fieldHtml = "";
        const label = field.label || field.name;

        if (field.type === "text") {
            fieldHtml = `
                <div class="form-group">
                    <label>${label}</label>
                    <input type="text" name="${field.name}" ${field.required ? "required" : ""}>
                </div>`;
        } else if (field.type === "textarea") {
            fieldHtml = `
                <div class="form-group">
                    <label>${label}</label>
                    <textarea name="${field.name}" rows="3" ${field.required ? "required" : ""}></textarea>
                </div>`;
        } else if (field.type === "select") {
            const options = (field.options || [])
                .map((opt) => `<option value="${opt}">${opt}</option>`)
                .join("");
            fieldHtml = `
                <div class="form-group">
                    <label>${label}</label>
                    <select name="${field.name}" ${field.required ? "required" : ""}>
                        ${options}
                    </select>
                </div>`;
        } else if (field.type === "number") {
            fieldHtml = `
                <div class="form-group">
                    <label>${label}</label>
                    <input type="number" name="${field.name}" ${field.required ? "required" : ""}>
                </div>`;
        }
        // می‌توانی انواع دیگر مثل checkbox/date/file را هم اضافه کنی

        container.insertAdjacentHTML("beforeend", fieldHtml);
    });
}

// خواندن داده‌های فرم داینامیک
function collectDynamicFormData() {
    const form = document.getElementById("dynamicPlatformForm");
    const formData = new FormData(form);
    const obj = {};
    formData.forEach((value, key) => {
        obj[key] = value;
    });
    return obj;
}

/* ============================================
   STEP 4 - Keywords (Chips/Tags) - Full Bundle
   Place in: create_content_step4_keywords.js
   Requires HTML IDs:
   - primaryKeywordInput, primaryKeywordList
   - secondaryKeywordInput, secondaryKeywordList
   - aiKeywordSuggestBtn
   - keywordsForm
   Depends on:
   - apiGenerateKeywordSuggestions (async)
   - apiSaveKeywords (async)
   - setCurrentStep(stepNumber)
   - window.ContentFlowState (global object)
=============================================== */

/* ---------------------------
   Global Keyword Store
---------------------------- */
window.KeywordStore = window.KeywordStore || {
  primary: [],   // user/ai keywords as plain text
  secondary: [], // user/ai keywords as plain text
};

/* ---------------------------
   Utilities: Chip Creation & Input Setup
---------------------------- */

/**
 * Create a chip element with a remove button
 * type: 'user' | 'ai'
 */
function createKeywordChip(text, type = "user") {
  const chip = document.createElement("span");
  chip.className = `kw-chip ${type === "ai" ? "kw-chip--ai" : "kw-chip--user"}`;
  chip.textContent = text;

  const removeBtn = document.createElement("button");
  removeBtn.type = "button";
  removeBtn.className = "kw-chip__remove";
  removeBtn.setAttribute("aria-label", "حذف");
  removeBtn.innerHTML = "×";

  chip.appendChild(removeBtn);
  return chip;
}

/**
 * Add keyword to UI and store if not duplicate (case-insensitive)
 * - wrapper: chips container element
 * - storeArray: target array in KeywordStore (primary | secondary)
 * - type: 'user' | 'ai'
 */
function addKeywordToUIAndStore(text, wrapper, storeArray, type = "user") {
  const value = (text || "").trim();
  if (!value) return;

  const exists = storeArray.some((k) => k.toLowerCase() === value.toLowerCase());
  if (exists) return;

  // push to store
  storeArray.push(value);

  // create chip
  const chip = createKeywordChip(value, type);

  // remove handler
  chip.querySelector(".kw-chip__remove").addEventListener("click", () => {
    chip.remove();
    const idx = storeArray.findIndex((k) => k === value);
    if (idx > -1) storeArray.splice(idx, 1);
  });

  wrapper.appendChild(chip);
}

/**
 * Setup input behavior: on Enter, split by , ; ، or newline and add as 'user' chips
 */
function setupKeywordInput(inputEl, wrapperEl, storeArray) {
  if (!inputEl || !wrapperEl) return;

  inputEl.addEventListener("keydown", (e) => {
    if (e.key === "Enter") {
      e.preventDefault();
      const raw = inputEl.value;

      const parts = raw
        .split(/[\n,;،]/g)
        .map((s) => s.trim())
        .filter(Boolean);

      parts.forEach((p) => addKeywordToUIAndStore(p, wrapperEl, storeArray, "user"));
      inputEl.value = "";
    }
  });
}

/* ---------------------------
   DOM Ready: Inputs wiring
---------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const primaryInput = document.getElementById("primaryKeywordInput");
  const primaryList = document.getElementById("primaryKeywordList");
  const secondaryInput = document.getElementById("secondaryKeywordInput");
  const secondaryList = document.getElementById("secondaryKeywordList");

  setupKeywordInput(primaryInput, primaryList, window.KeywordStore.primary);
  setupKeywordInput(secondaryInput, secondaryList, window.KeywordStore.secondary);
});

/* ---------------------------
   AI Suggestion Handler
---------------------------- */
document.addEventListener("DOMContentLoaded", () => {
  const aiBtn = document.getElementById("aiKeywordSuggestBtn");
  if (!aiBtn) return;

  aiBtn.addEventListener("click", async () => {
    aiBtn.disabled = true;
    aiBtn.innerText = "در حال تولید...";

    try {
      // Expected shape:
      // {
      //   primary_keyword: "Main term",
      //   secondary_keywords: ["kw1", "kw2"],
      //   long_tail_keywords: ["kw3", "kw4"]
      // }
      const result = await apiGenerateKeywordSuggestions();
      console.log("KEYWORD RESULT:", result);

      const primaryList = document.getElementById("primaryKeywordList");
      const secondaryList = document.getElementById("secondaryKeywordList");

      if (result?.primary_keyword) {
        addKeywordToUIAndStore(
          result.primary_keyword,
          primaryList,
          window.KeywordStore.primary,
          "ai"
        );
      }

      const secondaryAll = [
        ...(Array.isArray(result?.secondary_keywords) ? result.secondary_keywords : []),
        ...(Array.isArray(result?.long_tail_keywords) ? result.long_tail_keywords : []),
      ]
        .map((s) => (s || "").trim())
        .filter(Boolean);

      secondaryAll.forEach((kw) => {
        addKeywordToUIAndStore(
          kw,
          secondaryList,
          window.KeywordStore.secondary,
          "ai"
        );
      });
    } catch (err) {
      console.error(err);
      alert("خطا در دریافت پیشنهاد کلیدواژه");
    } finally {
      aiBtn.disabled = false;
      aiBtn.innerText = "پیشنهاد کلیدواژه با AI";
    }
  });
});

/* ---------------------------
   Submit Handler (Step 4)
---------------------------- */
(function setupStep4SubmitHandler() {
  document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("keywordsForm");
    if (!form) return;

    form.addEventListener("submit", async (e) => {
      e.preventDefault();

      // Collect from KeywordStore instead of FormData
      window.ContentFlowState = window.ContentFlowState || {};
      window.ContentFlowState.keywordsData = {
        primary_keywords: [...window.KeywordStore.primary],
        secondary_keywords: [...window.KeywordStore.secondary],
      };

      try {
        await apiSaveKeywords();
        setCurrentStep(5);
      } catch (err) {
        console.error(err);
        alert("خطا در ذخیره کلیدواژه‌ها");
      }
    });
  });
})();




