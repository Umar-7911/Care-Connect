// Global variables
let generatedOTP = '';
let resendTimeout;
let resendCountdown = 30;
let contactMethod = '';

// Page switching functions
function switchToSignIn() {
  document.getElementById('signupPage').classList.add('hidden');
  document.getElementById('forgotPasswordPage').classList.add('hidden');
  document.getElementById('signinPage').classList.remove('hidden');
  resetForgotPasswordForm();
}

function switchToSignUp() {
  document.getElementById('signinPage').classList.add('hidden');
  document.getElementById('forgotPasswordPage').classList.add('hidden');
  document.getElementById('signupPage').classList.remove('hidden');
  resetForgotPasswordForm();
}

function switchToForgotPassword() {
  document.getElementById('signupPage').classList.add('hidden');
  document.getElementById('signinPage').classList.add('hidden');
  document.getElementById('forgotPasswordPage').classList.remove('hidden');
  resetForgotPasswordForm();
}

function resetForgotPasswordForm() {
  document.getElementById('step1').classList.remove('hidden');
  document.getElementById('step2').classList.add('hidden');
  document.getElementById('step3').classList.add('hidden');
  document.getElementById('forgotPasswordForm').reset();
  document.getElementById('otpForm').reset();
  document.getElementById('newPasswordForm').reset();
  clearAllErrors();
}

function clearAllErrors() {
  document.querySelectorAll('.error-message').forEach(el => el.classList.remove('show'));
  document.querySelectorAll('.success-message').forEach(el => el.classList.remove('show'));
  document.querySelectorAll('input').forEach(el => el.classList.remove('error'));
}

// Toggle password visibility
function togglePassword(inputId, icon) {
  const input = document.getElementById(inputId);
  if (input.type === 'password') {
    input.type = 'text';
    icon.textContent = '🙈';
  } else {
    input.type = 'password';
    icon.textContent = '👁️';
  }
}

// OTP input navigation
function moveToNext(current, nextFieldId) {
  if (current.value.length === 1) {
    if (nextFieldId) {
      document.getElementById(nextFieldId).focus();
    }
  }
}

// Generate random OTP
function generateOTP() {
  return Math.floor(100000 + Math.random() * 900000).toString();
}

// Start resend countdown
function startResendCountdown() {
  resendCountdown = 30;
  const resendLink = document.getElementById('resendOtpLink');
  const resendTimer = document.getElementById('resendTimer');

  resendLink.classList.add('disabled');

  resendTimeout = setInterval(() => {
    resendCountdown--;
    resendTimer.textContent = `(${resendCountdown}s)`;

    if (resendCountdown <= 0) {
      clearInterval(resendTimeout);
      resendLink.classList.remove('disabled');
      resendTimer.textContent = '';
    }
  }, 1000);
}

// Resend OTP
function resendOTP() {
  generatedOTP = generateOTP();
  console.log('New OTP Generated:', generatedOTP);
  alert(`New OTP sent to ${contactMethod}: ${generatedOTP}`);
  startResendCountdown();

  // Clear OTP inputs
  for (let i = 1; i <= 6; i++) {
    document.getElementById(`otp${i}`).value = '';
  }
  document.getElementById('otp1').focus();
}

// Form validation for Sign Up
document.getElementById('signupForm').addEventListener('submit', function (e) {
  // Note: To make this work with Django backend, you usually remove e.preventDefault()
  // or use AJAX to submit the form data to the view.
  // keeping e.preventDefault() for now to show the alert as per original code.
  e.preventDefault();

  let isValid = true;

  const username = document.getElementById('username');
  const usernameError = document.getElementById('usernameError');
  if (username.value.length < 3) {
    username.classList.add('error');
    usernameError.classList.add('show');
    isValid = false;
  } else {
    username.classList.remove('error');
    usernameError.classList.remove('show');
  }

  const email = document.getElementById('email');
  const emailError = document.getElementById('emailError');
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    email.classList.add('error');
    emailError.classList.add('show');
    isValid = false;
  } else {
    email.classList.remove('error');
    emailError.classList.remove('show');
  }

  const phone = document.getElementById('phone');
  const phoneError = document.getElementById('phoneError');
  const phoneRegex = /^\d{10}$/;
  if (!phoneRegex.test(phone.value)) {
    phone.classList.add('error');
    phoneError.classList.add('show');
    isValid = false;
  } else {
    phone.classList.remove('error');
    phoneError.classList.remove('show');
  }

  const password = document.getElementById('password');
  const passwordError = document.getElementById('passwordError');
  if (password.value.length < 8) {
    password.classList.add('error');
    passwordError.classList.add('show');
    isValid = false;
  } else {
    password.classList.remove('error');
    passwordError.classList.remove('show');
  }

  if (isValid) {
    alert('Account created successfully! Submitting to backend...');
    switchToSignIn();
    this.reset();
    // this.submit(); // Uncomment this when backend logic is ready
  }
});

// Form validation for Sign In
document.getElementById('signinForm').addEventListener('submit', function (e) {
  e.preventDefault();

  let isValid = true;

  const email = document.getElementById('signinEmail');
  const emailError = document.getElementById('signinEmailError');
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailRegex.test(email.value)) {
    email.classList.add('error');
    emailError.classList.add('show');
    isValid = false;
  } else {
    email.classList.remove('error');
    emailError.classList.remove('show');
  }

  if (isValid) {
    alert('Signing in...');
    // Retrieve the Django URL from the data attribute on the form
    const redirectUrl = this.getAttribute('data-redirect-url');
    if (redirectUrl) {
      window.location.href = redirectUrl;
    } else {
      console.error("Redirect URL not found");
    }
  }
});

// Forgot Password - Step 1: Send OTP
document.getElementById('forgotPasswordForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const email = document.getElementById('resetEmail').value.trim();
  const phone = document.getElementById('resetPhone').value.trim();
  const emailError = document.getElementById('resetEmailError');
  const phoneError = document.getElementById('resetPhoneError');
  const emailInput = document.getElementById('resetEmail');
  const phoneInput = document.getElementById('resetPhone');

  let isValid = false;

  // Clear previous errors
  emailError.classList.remove('show');
  phoneError.classList.remove('show');
  emailInput.classList.remove('error');
  phoneInput.classList.remove('error');

  // Check if at least one field is filled
  if (!email && !phone) {
    emailError.textContent = 'Please enter either email or phone number';
    emailError.classList.add('show');
    emailInput.classList.add('error');
    phoneInput.classList.add('error');
    return;
  }

  // Validate email if provided
  if (email) {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      emailError.classList.add('show');
      emailInput.classList.add('error');
      return;
    } else {
      contactMethod = email;
      isValid = true;
    }
  }

  // Validate phone if provided (and email not provided or both provided)
  if (phone && !email) {
    const phoneRegex = /^\d{10}$/;
    if (!phoneRegex.test(phone)) {
      phoneError.classList.add('show');
      phoneInput.classList.add('error');
      return;
    } else {
      const countryCode = document.getElementById('resetCountryCode').value;
      contactMethod = countryCode + phone;
      isValid = true;
    }
  }

  if (isValid) {
    // Generate and send OTP
    generatedOTP = generateOTP();
    console.log('Generated OTP:', generatedOTP);

    // Simulate sending OTP
    alert(`OTP sent to ${contactMethod}: ${generatedOTP}\n\n(In production, this would be sent via email/SMS)`);

    // Show Step 2
    document.getElementById('step1').classList.add('hidden');
    document.getElementById('step2').classList.remove('hidden');
    document.getElementById('sentTo').textContent = contactMethod;
    document.getElementById('otpSentSuccess').classList.add('show');

    // Start countdown
    startResendCountdown();

    // Focus on first OTP input
    setTimeout(() => {
      document.getElementById('otp1').focus();
    }, 100);
  }
});

// OTP Verification - Step 2
document.getElementById('otpForm').addEventListener('submit', function (e) {
  e.preventDefault();

  // Get OTP from inputs
  let enteredOTP = '';
  for (let i = 1; i <= 6; i++) {
    enteredOTP += document.getElementById(`otp${i}`).value;
  }

  const otpError = document.getElementById('otpError');

  // Validate OTP length
  if (enteredOTP.length !== 6) {
    otpError.textContent = 'Please enter complete 6-digit OTP';
    otpError.classList.add('show');
    return;
  }

  // Verify OTP
  if (enteredOTP === generatedOTP) {
    otpError.classList.remove('show');

    // Show Step 3
    document.getElementById('step2').classList.add('hidden');
    document.getElementById('step3').classList.remove('hidden');

    // Clear resend timer
    clearInterval(resendTimeout);
  } else {
    otpError.textContent = 'Invalid OTP. Please try again.';
    otpError.classList.add('show');

    // Clear OTP inputs
    for (let i = 1; i <= 6; i++) {
      document.getElementById(`otp${i}`).value = '';
    }
    document.getElementById('otp1').focus();
  }
});

// New Password - Step 3
document.getElementById('newPasswordForm').addEventListener('submit', function (e) {
  e.preventDefault();

  const newPassword = document.getElementById('newPassword');
  const confirmPassword = document.getElementById('confirmPassword');
  const newPasswordError = document.getElementById('newPasswordError');
  const confirmPasswordError = document.getElementById('confirmPasswordError');

  let isValid = true;

  // Clear previous errors
  newPasswordError.classList.remove('show');
  confirmPasswordError.classList.remove('show');
  newPassword.classList.remove('error');
  confirmPassword.classList.remove('error');

  // Validate new password
  if (newPassword.value.length < 8) {
    newPassword.classList.add('error');
    newPasswordError.classList.add('show');
    isValid = false;
  }

  // Validate confirm password
  if (confirmPassword.value !== newPassword.value) {
    confirmPassword.classList.add('error');
    confirmPasswordError.classList.add('show');
    isValid = false;
  }

  if (isValid) {
    alert('Password reset successful! You can now sign in with your new password.');

    // Redirect to sign in page
    setTimeout(() => {
      switchToSignIn();
    }, 1000);
  }
});

// Real-time validation
document.getElementById('email').addEventListener('blur', function () {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  const emailError = document.getElementById('emailError');
  if (!emailRegex.test(this.value) && this.value !== '') {
    this.classList.add('error');
    emailError.classList.add('show');
  } else {
    this.classList.remove('error');
    emailError.classList.remove('show');
  }
});

document.getElementById('phone').addEventListener('blur', function () {
  const phoneRegex = /^\d{10}$/;
  const phoneError = document.getElementById('phoneError');
  if (!phoneRegex.test(this.value) && this.value !== '') {
    this.classList.add('error');
    phoneError.classList.add('show');
  } else {
    this.classList.remove('error');
    phoneError.classList.remove('show');
  }
});

// Auto-focus and allow backspace navigation in OTP inputs
document.querySelectorAll('.otp-input').forEach((input, index) => {
  input.addEventListener('keydown', function (e) {
    if (e.key === 'Backspace' && this.value === '' && index > 0) {
      document.getElementById(`otp${index}`).focus();
    }
  });

  // Only allow numbers
  input.addEventListener('input', function () {
    this.value = this.value.replace(/[^0-9]/g, '');
  });
});