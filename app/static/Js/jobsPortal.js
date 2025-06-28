// Job Portal JavaScript functionality

document.addEventListener("DOMContentLoaded", function () {
  // Elements
  const loadingElement = document.getElementById("loading");
  const jobListElement = document.getElementById("job-list");

  // Show loading initially
  if (loadingElement) {
    loadingElement.style.display = "block";
  }
  if (jobListElement) {
    jobListElement.style.display = "none";
  }

  // Simulate loading time and then show jobs
  setTimeout(() => {
    if (loadingElement) {
      loadingElement.style.display = "none";
    }
    if (jobListElement) {
      jobListElement.style.display = "block";
      animateJobCards();
    }
  }, 2000);
});

// Animate job cards appearing
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

// Add click tracking for apply buttons
document.addEventListener("click", function (e) {
  if (e.target.classList.contains("apply-btn")) {
    console.log(
      "Apply button clicked for job:",
      e.target.closest(".job-card").querySelector("h3").textContent
    );
  }
});
