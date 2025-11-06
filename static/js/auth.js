// Simulate biometric authentication
function simulateBiometric() {
    alert('Biometric authentication simulated!\n\nIn production, this would:\n1. Capture face/fingerprint\n2. Verify against database\n3. Authenticate user');
}

// Simulate RFID card tap
function simulateRFID() {
    alert('RFID card tap simulated!\n\nIn production, this would:\n1. Read RFID card\n2. Verify card credentials\n3. Authenticate user');
}

// Auto-refresh OTP code display (if needed)
function updateOTPCode() {
    // This would be implemented with a backend endpoint
    // that generates and displays the current OTP
    console.log('OTP code refresh functionality');
}

// Form validation
document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.querySelector('.login-form');
    if (loginForm) {
        loginForm.addEventListener('submit', function(e) {
            const otpCode = document.getElementById('otp_code');
            if (otpCode && otpCode.value.length !== 6) {
                alert('Please enter a valid 6-digit OTP code');
                e.preventDefault();
            }
        });
    }
});

