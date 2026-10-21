document.querySelectorAll("[data-topic]").forEach((button) => {
  button.addEventListener("click", () => {
    const field = document.getElementById("topic");
    if (field) {
      field.value = button.dataset.topic;
      field.focus();
    }
  });
});

const form = document.getElementById("topicForm");
const generateBtn = document.getElementById("generateBtn");
if (form && generateBtn) {
  form.addEventListener("submit", () => {
    generateBtn.disabled = true;
    generateBtn.innerHTML = '<span class="spinner"></span> Creating your kit…';
  });
}
