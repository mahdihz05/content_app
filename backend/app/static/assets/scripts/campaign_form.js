// static/js/campaign_form.js

let currentStep = 1;

const form = document.getElementById('campaignForm');
const nextBtn = document.getElementById('nextBtn');
const prevBtn = document.getElementById('prevBtn');
const submitBtn = document.getElementById('submitBtn');

function showStep(step) {
    document.querySelectorAll('.form-step').forEach(el => {
        el.classList.remove('active');
    });

    document.querySelector(`.form-step[data-step="${step}"]`).classList.add('active');

    document.querySelectorAll('.step').forEach(el => {
        el.classList.remove('active', 'completed');

        const stepNum = parseInt(el.dataset.step);

        if (stepNum < step) {
            el.classList.add('completed');
        } else if (stepNum === step) {
            el.classList.add('active');
        }
    });

    prevBtn.style.display = step === 1 ? 'none' : 'inline-flex';

    if (step === 5) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'inline-flex';
        fillReview();
    } else {
        nextBtn.style.display = 'inline-flex';
        submitBtn.style.display = 'none';
    }
}

nextBtn.addEventListener('click', () => {
    if (currentStep < 5) {
        currentStep++;
        showStep(currentStep);
    }
});

prevBtn.addEventListener('click', () => {
    if (currentStep > 1) {
        currentStep--;
        showStep(currentStep);
    }
});

const messageContent = document.getElementById('messageContent');
const charCount = document.getElementById('charCount');
const preview = document.getElementById('messagePreview');

if (messageContent) {
    messageContent.addEventListener('input', () => {
        charCount.textContent = messageContent.value.length;

        preview.innerHTML = `
            <p>${messageContent.value.replace(/\n/g, '<br>')}</p>
        `;
    });
}

const mediaFile = document.getElementById('mediaFile');
const mediaPreview = document.getElementById('mediaPreview');

if (mediaFile) {
    mediaFile.addEventListener('change', e => {
        const file = e.target.files[0];

        if (!file) return;

        const url = URL.createObjectURL(file);

        mediaPreview.style.display = 'block';

        if (file.type.startsWith('image')) {
            mediaPreview.innerHTML = `<img src="${url}">`;
        } else {
            mediaPreview.innerHTML = `<video controls src="${url}"></video>`;
        }
    });
}

document.querySelectorAll('input[name="sendTime"]').forEach(radio => {
    radio.addEventListener('change', e => {
        const group = document.getElementById('scheduleGroup');

        group.style.display = e.target.value === 'scheduled'
            ? 'block'
            : 'none';
    });
});

const recipientSource = document.getElementById('recipientSource');

if (recipientSource) {
    recipientSource.addEventListener('change', e => {
        document.getElementById('manualRecipients').style.display = 'none';
        document.getElementById('fileRecipients').style.display = 'none';

        if (e.target.value === 'manual') {
            document.getElementById('manualRecipients').style.display = 'block';
        }

        if (e.target.value === 'file') {
            document.getElementById('fileRecipients').style.display = 'block';
        }
    });
}

const autoReply = document.getElementById('autoReply');

if (autoReply) {
    autoReply.addEventListener('change', e => {
        document.getElementById('autoReplyGroup').style.display =
            e.target.checked ? 'block' : 'none';
    });
}

function fillReview() {
    document.getElementById('reviewBasicInfo').innerHTML = `
        <p><strong>نام:</strong> ${document.getElementById('campaignName').value}</p>
        <p><strong>پلتفرم:</strong> ${document.getElementById('campaignPlatform').value}</p>
    `;

    document.getElementById('reviewMessage').innerHTML = `
        <p>${document.getElementById('messageContent').value}</p>
    `;

    document.getElementById('reviewSettings').innerHTML = `
        <p><strong>تاخیر:</strong> ${document.getElementById('sendDelay').value} ثانیه</p>
    `;
}

form.addEventListener('submit', e => {
    e.preventDefault();

    submitBtn.disabled = true;
    submitBtn.innerHTML = 'در حال ایجاد کمپین...';

    setTimeout(() => {
        alert('کمپین با موفقیت ایجاد شد');
        window.location.href = '/dashboard/messaging/campaigns/';
    }, 1500);
});

const aiModal = document.getElementById('aiModal');

document.querySelectorAll('[data-action="ai"]').forEach(btn => {
    btn.addEventListener('click', () => {
        aiModal.classList.add('show');
    });
});

document.querySelector('.close-modal').addEventListener('click', () => {
    aiModal.classList.remove('show');
});

document.getElementById('generateAI').addEventListener('click', () => {
    const prompt = document.getElementById('aiPrompt').value;
    const result = document.getElementById('aiResult');

    result.style.display = 'block';
    result.innerHTML = `
        <p>
        سلام {name} 👋
        <br><br>
        محصول جدید ما منتشر شد و خوشحال می‌شویم نظرتان را بدانیم.
        <br><br>
        برای اطلاعات بیشتر پیام دهید.
        </p>
    `;
});
