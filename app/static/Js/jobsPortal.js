// Job Portal JavaScript functionality

document.addEventListener("DOMContentLoaded", function () {
  const loadingElement = document.getElementById("loading");
  const jobListElement = document.getElementById("job-list");

  // Show loader first
  if (loadingElement) loadingElement.style.display = "block";
  if (jobListElement) jobListElement.style.display = "none";

  // Simulate loading delay (e.g., 2 seconds)
  setTimeout(() => {
    if (loadingElement) loadingElement.style.display = "none";
    if (jobListElement) {
      jobListElement.style.display = "block";
      animateJobCards(); // ✅ Animate appearance
      initShowMoreButtons(); // ✅ Enable 'Show more/less'
    }
  }, 2000);
});

// Animate job cards sliding in
function animateJobCards() {
  const jobCards = document.querySelectorAll(".job-card");
  jobCards.forEach((card, index) => {
    card.style.opacity = "0";
    card.style.transform = "translateY(20px)";
    setTimeout(() => {
      card.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      card.style.opacity = "1";
      card.style.transform = "translateY(0)";
    }, index * 100);
  });
}

// Toggle show more/less for job descriptions
function initShowMoreButtons() {
  const toggleButtons = document.querySelectorAll(".toggle-btn");
  toggleButtons.forEach((btn) => {
    btn.addEventListener("click", () => {
      const targetId = btn.getAttribute("data-target");
      const desc = document.getElementById(targetId);
      const moreText = desc.querySelector(".more-text");

      if (moreText.classList.contains("d-none")) {
        moreText.classList.remove("d-none");
        btn.textContent = "Show less";
      } else {
        moreText.classList.add("d-none");
        btn.textContent = "Show more";
      }
    });
  });
}

// Log apply button clicks
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("apply-btn")) {
    const jobTitle =
      e.target.closest(".job-card").querySelector("h3, h5")?.textContent ||
      "Unknown Job";
    console.log("Apply clicked for:", jobTitle);
  }
});
