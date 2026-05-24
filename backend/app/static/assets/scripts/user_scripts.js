// لاگین
document.getElementById('loginForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const phone = document.getElementById('phone').value;
  const password = document.getElementById('password').value;

  fetch('/api/v1/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ phone_number: phone, password: password }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('ورود موفقیت‌آمیز! ' + JSON.stringify(data.data));
      // می‌تونی اینجا redirect کنی
    } else {
      alert('خطا: ' + data.error);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('خطایی رخ داد: ' + error);
  });
});

// ثبت‌نام
document.getElementById('registerForm').addEventListener('submit', function(e) {
  e.preventDefault();
  const name = document.getElementById('name').value;
  const phone = document.getElementById('phone').value;
  const password = document.getElementById('password').value;

  fetch('/api/v1/register', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ name, phone_number: phone, password: password }),
  })
  .then(response => response.json())
  .then(data => {
    if (data.success) {
      alert('ثبت‌نام موفقیت‌آمیز! ' + JSON.stringify(data.data));
      // می‌تونی اینجا redirect کنی
    } else {
      alert('خطا: ' + data.error);
    }
  })
  .catch(error => {
    console.error('Error:', error);
    alert('خطایی رخ داد: ' + error);
  });
});
