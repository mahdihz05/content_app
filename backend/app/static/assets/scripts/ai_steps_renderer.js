function renderStep(step) {

    const box = document.getElementById("dynamicStepContent");
    box.innerHTML = "";

    if (!step) return;

    /* -------------------------
       انتخاب کمپین
    ------------------------- */

    if (step.type === "campaign_select") {

        const grid = document.createElement("div");
        grid.className = "campaign-grid";

        step.campaigns.forEach(c => {

            const card = document.createElement("div");
            card.className = "campaign-card";

            card.innerHTML = `
                <div class="campaign-title">${c.title}</div>
            `;

            card.onclick = () => {
                window.selectCampaign(c.id);
            };

            grid.appendChild(card);
        });

        box.appendChild(grid);
        return;
    }

    /* -------------------------
       فرم
    ------------------------- */

    if (step.type === "form") {

        const wrapper = document.createElement("div");
        wrapper.className = "ai-form";

        const title = document.createElement("h3");
        title.innerText = step.title || "تکمیل اطلاعات";

        const form = document.createElement("form");

        step.fields.forEach(f => {

            const group = document.createElement("div");
            group.className = "form-group";

            const label = document.createElement("label");
            label.innerText = f.label;

            const input = document.createElement("input");
            input.name = f.name;
            input.placeholder = f.label;

            group.appendChild(label);
            group.appendChild(input);

            form.appendChild(group);
        });

        const btn = document.createElement("button");
        btn.className = "form-submit";
        btn.innerText = "ثبت و ادامه";
        btn.type = "submit";

        form.appendChild(btn);

       form.onsubmit = e => {

            e.preventDefault();

            const formData = {};

            step.fields.forEach(f => {
                formData[f.name] =
                    form.querySelector(`[name="${f.name}"]`).value;
            });

            sendMessage(formData);
        };

        wrapper.appendChild(title);
        wrapper.appendChild(form);

        box.appendChild(wrapper);

        return;
    }

    /* -------------------------
       keyword
    ------------------------- */

    if (step.type === "keyword_list") {

        const container = document.createElement("div");
        container.className = "keyword-container";

        step.keywords.forEach(k => {

            const chip = document.createElement("span");
            chip.className = "keyword-chip";
            chip.innerText = k;

            container.appendChild(chip);
        });

        box.appendChild(container);

        return;
    }

    /* -------------------------
       خروجی
    ------------------------- */

    if (step.type === "output") {

        const div = document.createElement("div");
        div.className = "ai-output";

        div.innerHTML = `
            <h3>خروجی نهایی</h3>
            <div class="output-box">${step.content}</div>
        `;

        box.appendChild(div);
    }

}
