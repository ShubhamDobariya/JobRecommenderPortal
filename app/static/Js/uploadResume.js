const resumeInput = document.getElementById("resume");
const uploadBtn = document.getElementById("uploadBtn");

resumeInput.addEventListener("change", () => {
  const file = resumeInput.files[0];
  const allowedTypes = /\.(pdf|doc|docx)$/i;
  uploadBtn.disabled = true;

  if (file) {
    if (!allowedTypes.test(file.name)) {
      alert("Invalid file type. Please upload PDF, DOC, or DOCX.");
      resumeInput.value = "";
      return;
    }

    if (file.size > 5 * 1024 * 1024) {
      alert("File too large. Maximum allowed size is 5MB.");
      resumeInput.value = "";
      return;
    }

    const reader = new FileReader();

    reader.onload = function () {
      uploadBtn.disabled = false;
    };

    reader.onerror = function () {
      alert("Error reading file. Please try again.");
      resumeInput.value = "";
      uploadBtn.disabled = true;
    };

    const blob = file.slice(0, 100);
    reader.readAsArrayBuffer(blob);
  }
});
