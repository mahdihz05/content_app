// ============================================
// اعتبارسنجی و UX بهبود یافته برای فرم ثبت‌نام
// ============================================

document.addEventListener('DOMContentLoaded', function() {

    // دریافت المان‌ها
    const usernameInput = document.getElementById('username');
    const phoneInput = document.getElementById('phone_number');
    const passwordInput = document.getElementById('password');
    const passwordConfirmInput = document.getElementById('password_confirm');

    // ============================================
    // تابع نمایش خطا
    // ============================================

    function showError(input, message) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('error');
        formGroup.classList.remove('success');

        let errorDiv = formGroup.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            input.parentNode.insertAdjacentElement('afterend', errorDiv);
        }
        errorDiv.textContent = message;
    }

    function showSuccess(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('success');
        formGroup.classList.remove('error');

        const errorDiv = formGroup.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.textContent = '';
        }
    }

    function clearValidation(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.remove('error', 'success');

        const errorDiv = formGroup.querySelector('.error-message');
        if (errorDiv) {
            errorDiv.textContent = '';
        }
    }

    // ============================================
    // اعتبارسنجی نام کاربری
    // ============================================

    function validateUsername() {
        const value = usernameInput.value.trim();

        if (value === '') {
            showError(usernameInput, 'نام کاربری الزامی است');
            return false;
        }

        if (value.length < 3) {
            showError(usernameInput, 'نام کاربری باید حداقل ۳ کاراکتر باشد');
            return false;
        }

        if (!/^[a-zA-Z0-9_]+$/.test(value)) {
            showError(usernameInput, 'فقط حروف انگلیسی، اعداد و _ مجاز است');
            return false;
        }

        showSuccess(usernameInput);
        return true;
    }

    // ============================================
    // اعتبارسنجی شماره تلفن
    // ============================================

    function validatePhone() {
        const value = phoneInput.value.trim();

        if (value === '') {
            showError(phoneInput, 'شماره تلفن الزامی است');
            return false;
        }

        const phoneRegex = /^09\d{9}$/;
        if (!phoneRegex.test(value)) {
            showError(phoneInput, 'شماره تلفن باید با ۰۹ شروع شود و ۱۱ رقم باشد');
            return false;
        }

        showSuccess(phoneInput);
        return true;
    }

    // ============================================
    // بررسی قدرت رمز عبور
    // ============================================

    function checkPasswordStrength(password) {
        let strength = 0;

        if (password.length >= 8) strength++;
        if (password.length >= 12) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z0-9]/.test(password)) strength++;

        if (strength <= 2) return 'weak';
        if (strength <= 4) return 'medium';
        return 'strong';
    }

    function updatePasswordStrength() {
        const value = passwordInput.value;
        const formGroup = passwordInput.closest('.form-group');

        let strengthDiv = formGroup.querySelector('.password-strength');
        if (!strengthDiv) {
            strengthDiv = document.createElement('div');
            strengthDiv.className = 'password-strength';
            strengthDiv.innerHTML = `
                <div class="strength-bar">
                    <div class="strength-fill"></div>
                </div>
                <div class="strength-text"></div>
            `;
            passwordInput.parentNode.insertAdjacentElement('afterend', strengthDiv);
        }

        if (value === '') {
            strengthDiv.classList.remove('active');
            return;
        }

        strengthDiv.classList.add('active');

        const strength = checkPasswordStrength(value);
        const fill = strengthDiv.querySelector('.strength-fill');
        const text = strengthDiv.querySelector('.strength-text');

        fill.className = 'strength-fill ' + strength;
        text.className = 'strength-text ' + strength;

        if (strength === 'weak') {
            text.textContent = 'ضعیف - رمز قوی‌تری انتخاب کنید';
        } else if (strength === 'medium') {
            text.textContent = 'متوسط - می‌توانید بهتر کنید';
        } else {
            text.textContent = 'قوی - عالی است!';
        }
    }

    // ============================================
    // اعتبارسنجی رمز عبور
    // ============================================

    function validatePassword() {
        const value = passwordInput.value;

        if (value === '') {
            showError(passwordInput, 'رمز عبور الزامی است');
            return false;
        }

        if (value.length < 8) {
            showError(passwordInput, 'رمز عبور باید حداقل ۸ کاراکتر باشد');
            return false;
        }

        const strength = checkPasswordStrength(value);
        if (strength === 'weak') {
            showError(passwordInput, 'رمز عبور خیلی ضعیف است');
            return false;
        }

        showSuccess(passwordInput);
        return true;
    }

    // ============================================
    // اعتبارسنجی تکرار رمز
    // ============================================

    function validatePasswordConfirm() {
        const value = passwordConfirmInput.value;
        const passwordValue = passwordInput.value;

        if (value === '') {
            showError(passwordConfirmInput, 'تکرار رمز عبور الزامی است');
            return false;
        }

        if (value !== passwordValue) {
            showError(passwordConfirmInput, 'رمزهای عبور مطابقت ندارند');
            return false;
        }

        showSuccess(passwordConfirmInput);
        return true;
    }

    // ============================================
    // رویدادها
    // ============================================

    usernameInput.addEventListener('blur', validateUsername);
    usernameInput.addEventListener('input', function() {
        if (this.value.trim() !== '') {
            validateUsername();
        } else {
            clearValidation(this);
        }
    });

    phoneInput.addEventListener('blur', validatePhone);
    phoneInput.addEventListener('input', function() {
        if (this.value.trim() !== '') {
            validatePhone();
        } else {
            clearValidation(this);
        }
    });

    passwordInput.addEventListener('input', function() {
        updatePasswordStrength();
        if (this.value !== '') {
            validatePassword();
        } else {
            clearValidation(this);
        }

        // بررسی تطابق رمزها اگر تکرار رمز پر شده
        if (passwordConfirmInput.value !== '') {
            validatePasswordConfirm();
        }
    });

    passwordInput.addEventListener('blur', validatePassword);

    passwordConfirmInput.addEventListener('input', function() {
        if (this.value !== '') {
            validatePasswordConfirm();
        } else {
            clearValidation(this);
        }
    });

    passwordConfirmInput.addEventListener('blur', validatePasswordConfirm);

    // ============================================
    // آیکون نمایش/مخفی رمز
    // ============================================

    function addPasswordToggle(input) {
        const formGroup = input.closest('.form-group');
        formGroup.classList.add('has-icon');

        const wrapper = document.createElement('div');
        wrapper.className = 'input-wrapper';

        input.parentNode.insertBefore(wrapper, input);
        wrapper.appendChild(input);

        const toggle = document.createElement('span');
        toggle.className = 'toggle-password';
        wrapper.appendChild(toggle);

        toggle.addEventListener('click', function() {
            if (input.type === 'password') {
                input.type = 'text';
            } else {
                input.type = 'password';
            }
        });
    }

    addPasswordToggle(passwordInput);
    addPasswordToggle(passwordConfirmInput);

});
