// static/assets/js/ai-chat.js

let chatHistory = [];

document.addEventListener('DOMContentLoaded', function() {
    setupChatHandlers();
    loadChatHistory();
});

function setupChatHandlers() {
    const sendBtn = document.getElementById('send-btn');
    const chatInput = document.getElementById('chat-input');
    const clearBtn = document.getElementById('clear-chat-btn');

    // ارسال پیام با کلیک روی دکمه
    sendBtn.addEventListener('click', sendMessage);

    // ارسال پیام با Enter (Shift+Enter برای خط جدید)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // پاک کردن چت
    clearBtn.addEventListener('click', clearChat);

    // دکمه‌های پیشنهاد سریع
    const promptBtns = document.querySelectorAll('.prompt-btn');
    promptBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            chatInput.value = this.textContent.trim();
            chatInput.focus();
        });
    });

    // تنظیم ارتفاع خودکار textarea
    chatInput.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = Math.min(this.scrollHeight, 150) + 'px';
    });
}

async function sendMessage() {
    const chatInput = document.getElementById('chat-input');
    const message = chatInput.value.trim();

    if (!message) return;

    // نمایش پیام کاربر
    addMessage('user', message);
    chatInput.value = '';
    chatInput.style.height = 'auto';

    // غیرفعال کردن دکمه ارسال
    const sendBtn = document.getElementById('send-btn');
    sendBtn.disabled = true;

    // نمایش typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/api/messaging/ai-chat/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                message: message,
                history: chatHistory
            })
        });

        if (!response.ok) {
            throw new Error('خطا در دریافت پاسخ');
        }

        const data = await response.json();

        // مخفی کردن typing indicator
        hideTypingIndicator();

        // نمایش پاسخ AI
        addMessage('assistant', data.response);

        // ذخیره در تاریخچه
        chatHistory.push({
            role: 'user',
            content: message
        });
        chatHistory.push({
            role: 'assistant',
            content: data.response
        });

        saveChatHistory();

    } catch (error) {
        console.error('خطا در ارسال پیام:', error);
        hideTypingIndicator();
        addMessage('assistant', 'متأسفم، خطایی رخ داد. لطفاً دوباره تلاش کنید.');
    } finally {
        sendBtn.disabled = false;
        chatInput.focus();
    }
}

function addMessage(role, content) {
    const messagesContainer = document.getElementById('chat-messages');
    const emptyState = document.getElementById('empty-state');

    // مخفی کردن empty state
    if (emptyState) {
        emptyState.style.display = 'none';
    }

    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    const now = new Date();
    const timeString = now.toLocaleTimeString('fa-IR', {
        hour: '2-digit',
        minute: '2-digit'
    });

    const avatar = role === 'user' ? '👤' : '🤖';

    messageDiv.innerHTML = `
        <div class="message-avatar">${avatar}</div>
        <div class="message-content">
            ${escapeHtml(content)}
            <span class="message-time">${timeString}</span>
        </div>
    `;

    messagesContainer.appendChild(messageDiv);

    // اسکرول به پایین
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function showTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.classList.add('active');

    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
}

function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    indicator.classList.remove('active');
}

function clearChat() {
    if (!confirm('آیا از پاک کردن تاریخچه چت اطمینان دارید؟')) {
        return;
    }

    chatHistory = [];
    saveChatHistory();

    const messagesContainer = document.getElementById('chat-messages');
    messagesContainer.innerHTML = `
        <div class="typing-indicator" id="typing-indicator">
            <div class="message-avatar">🤖</div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    const emptyState = document.getElementById('empty-state');
    if (emptyState) {
        emptyState.style.display = 'flex';
    }
}

function saveChatHistory() {
    try {
        localStorage.setItem('ai_chat_history', JSON.stringify(chatHistory));
    } catch (error) {
        console.error('خطا در ذخیره تاریخچه:', error);
    }
}

function loadChatHistory() {
    try {
        const saved = localStorage.getItem('ai_chat_history');
        if (saved) {
            chatHistory = JSON.parse(saved);

            // بازیابی پیام‌ها
            chatHistory.forEach(msg => {
                addMessage(msg.role, msg.content);
            });
        }
    } catch (error) {
        console.error('خطا در بارگذاری تاریخچه:', error);
        chatHistory = [];
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML.replace(/\n/g, '<br>');
}

function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
