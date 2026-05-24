document.addEventListener('DOMContentLoaded', function() {

    // ==================== Real-time Validation ====================

    const phoneInput = document.getElementById('phone_number');
    const passwordInput = document.getElementById('password');

    // اعتبارسنجی شماره تلفن
    if (phoneInput) {
        // ایجاد المان پیام خطا
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        phoneInput.parentElement.appendChild(errorMsg);

        phoneInput.addEventListener('input', function() {
            const value = this.value.trim();

            // بررسی خالی بودن
            if (value === '') {
                this.classList.remove('success', 'error');
                errorMsg.textContent = '';
                errorMsg.classList.remove('show');
                return;
            }

            // بررسی فرمت شماره تلفن ایرانی (09xxxxxxxxx)
            const phoneRegex = /^09\d{9}$/;

            if (!phoneRegex.test(value)) {
                this.classList.add('error');
                this.classList.remove('success');
                errorMsg.textContent = 'شماره تلفن باید با 09 شروع شود و 11 رقم باشد';
                errorMsg.classList.add('show');
            } else {
                this.classList.add('success');
                this.classList.remove('error');
                errorMsg.textContent = '';
                errorMsg.classList.remove('show');
            }
        });
    }

    // اعتبارسنجی رمز عبور
    if (passwordInput) {
        // ایجاد المان پیام خطا
        const errorMsg = document.createElement('div');
        errorMsg.className = 'error-message';
        passwordInput.parentElement.appendChild(errorMsg);

        // ==================== Password Toggle ====================

        // ایجاد دکمه نمایش/مخفی رمز عبور
        const toggleBtn = document.createElement('button');
        toggleBtn.type = 'button';
        toggleBtn.className = 'password-toggle';
        toggleBtn.innerHTML = '👁️';
        toggleBtn.setAttribute('aria-label', 'نمایش رمز عبور');

        passwordInput.parentElement.classList.add('has-toggle');
        passwordInput.parentElement.appendChild(toggleBtn);

        toggleBtn.addEventListener('click', function() {
            if (passwordInput.type === 'password') {
                passwordInput.type = 'text';
                this.innerHTML = '🙈';
                this.setAttribute('aria-label', 'مخفی کردن رمز عبور');
            } else {
                passwordInput.type = 'password';
                this.innerHTML = '👁️';
                this.setAttribute('aria-label', 'نمایش رمز عبور');
            }
        });

        // اعتبارسنجی رمز عبور
        passwordInput.addEventListener('input', function() {
            const value = this.value;

            // بررسی خالی بودن
            if (value === '') {
                this.classList.remove('success', 'error');
                errorMsg.textContent = '';
                errorMsg.classList.remove('show');
                return;
            }

            // بررسی حداقل طول
            if (value.length < 8) {
                this.classList.add('error');
                this.classList.remove('success');
                errorMsg.textContent = 'رمز عبور باید حداقل 8 کاراکتر باشد';
                errorMsg.classList.add('show');
            } else {
                this.classList.add('success');
                this.classList.remove('error');
                errorMsg.textContent = '';
                errorMsg.classList.remove('show');
            }
        });
    }

    // ==================== Form Submit with Loading State ====================

    const form = document.getElementById('login-form');
    const submitButton = form.querySelector('.submit-button');

    form.addEventListener('submit', function(e) {
        // اعتبارسنجی نهایی قبل از ارسال
        let isValid = true;

        if (phoneInput) {
            const phoneValue = phoneInput.value.trim();
            const phoneRegex = /^09\d{9}$/;

            if (!phoneRegex.test(phoneValue)) {
                phoneInput.classList.add('error');
                isValid = false;
            }
        }

        if (passwordInput) {
            const passwordValue = passwordInput.value;

            if (passwordValue.length < 8) {
                passwordInput.classList.add('error');
                isValid = false;
            }
        }

        if (!isValid) {
            e.preventDefault();
            return false;
        }

        // فعال کردن حالت loading
        if (submitButton) {
            submitButton.classList.add('loading');
            submitButton.disabled = true;
        }
    });

    // ==================== Input Animations ====================

    const inputs = document.querySelectorAll('.form-group input');
    inputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'translateX(-2px)';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'translateX(0)';
        });
    });

});
