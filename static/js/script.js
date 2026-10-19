
const password = document.getElementById("password");
const showPassword = document.getElementById("show-password");

if (password && showPassword) {
    showPassword.addEventListener("change", () => {
        password.type = showPassword.checked ? "text" : "password";
    });
}

const form = document.getElementById("feedback-form");
const progress = document.getElementById("progress-bar");
const progressText = document.getElementById("progress-text");

if (form && progress && progressText) {
    const updateProgress = () => {
        const answered = new Set(
            [...form.querySelectorAll('input[type="radio"]:checked')]
                .map(input => input.name)
        ).size;

        const percent = Math.round(answered / 30 * 100);
        progress.value = answered;
        progressText.textContent =
            `${answered} of 30 questions answered (${percent}%)`;
    };

    form.addEventListener("change", updateProgress);

    form.addEventListener("submit", event => {
        if (!confirm("Are you sure you want to submit your feedback?")) {
            event.preventDefault();
        }
    });

    updateProgress();
}
