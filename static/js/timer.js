let countdown = 60;
let timerDisplay = document.getElementById("timer");
let resendButton = document.querySelector(".resend-otp");

function startCountdown() {
    resendButton.style.pointerEvents = "none";  // غیرفعال کردن دکمه
    resendButton.style.opacity = "0.5";  // تغییر ظاهر دکمه
    countdown = 60;

    let interval = setInterval(function() {
        timerDisplay.innerText = countdown;
        countdown--;

        if (countdown < 0) {
            clearInterval(interval);
            resendButton.style.pointerEvents = "auto";  // فعال کردن دکمه
            resendButton.style.opacity = "1";  // بازگرداندن ظاهر دکمه
            timerDisplay.innerText = "";
        }
    }, 1000);
}

// شروع شمارش معکوس هنگام بارگذاری صفحه
window.onload = startCountdown;

// ارسال درخواست AJAX برای ارسال مجدد OTP
resendButton.addEventListener("click", function() {
    fetch("{% url 'resend_otp' %}", {
        method: "POST",
        headers: {
            "X-CSRFToken": "{{ csrf_token }}",
            "Content-Type": "application/json"
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert("✅ کد جدید ارسال شد!");
            startCountdown(); // شروع مجدد شمارش معکوس
        } else {
            alert("❌ خطا در ارسال کد جدید! لطفاً دوباره تلاش کنید.");
        }
    })
    .catch(error => {
        console.error("Error:", error);
    });
});