document.addEventListener("DOMContentLoaded", function () {
  const signupForm = document.getElementById("signup-form");
  const loginForm = document.getElementById("login-form");

  function setLoading(form, isLoading) {
    const submitBtn = form.querySelector('button[type="submit"]');
    const originalText = submitBtn.textContent;

    if (isLoading) {
      form.classList.add("loading");
      submitBtn.disabled = true;
    } else {
      form.classList.remove("loading");
      submitBtn.textContent = originalText;
      submitBtn.disabled = false;
    }
  }

  if (signupForm) {
    signupForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      setLoading(signupForm, true);

      const formData = new FormData(signupForm);
      const userData = {
        username: formData.get("username"),
        email: formData.get("email"),
        password: formData.get("password"),
      };

      // Basic client-side validation
      if (userData.password.length < 8) {
        alert("Password must be at least 8 characters long");
        setLoading(signupForm, false);
        return;
      }

      try {
        const response = await fetch("/signup", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        });

        const result = await response.json();

        if (response.ok) {
          setTimeout(() => {
            // window.location.href = "/login";
            signupForm.reset();
          }, 2000);
        } else {
          alert(result.detail || "Registration failed. Please try again.");
        }
      } catch (error) {
        alert("Network error. Please check your connection and try again.");
      } finally {
        setLoading(signupForm, false);
      }
    });
  }

  if (loginForm) {
    loginForm.addEventListener("submit", async function (e) {
      e.preventDefault();
      setLoading(loginForm, true);

      const formData = new FormData(loginForm);
      const userData = {
        email: formData.get("email"),
        password: formData.get("password"),
      };

      try {
        const response = await fetch("/login", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify(userData),
        });

        const result = await response.json();

        if (response.ok) {
          localStorage.setItem("access_token", result.access_token);
          localStorage.setItem("user", JSON.stringify(result.user));

          setTimeout(() => {
            // window.location.href = "/dashboard";
            loginForm.reset();
          }, 1000);
        } else {
          alert(
            result.detail || "Login failed. Please check your credentials."
          );
        }
      } catch (error) {
        alert("Network error. Please check your connection and try again.");
      } finally {
        setLoading(loginForm, false);
      }
    });
  }

  // Add input validation feedback
  const inputs = document.querySelectorAll("input");
  inputs.forEach((input) => {
    input.addEventListener("blur", function () {
      if (this.type === "email" && this.value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        this.style.borderColor = emailRegex.test(this.value)
          ? "#10b981"
          : "#ef4444";
      }

      if (this.type === "password" && this.value) {
        this.style.borderColor = this.value.length < 8 ? "#ef4444" : "#10b981";
      }
    });

    input.addEventListener("input", function () {
      this.style.borderColor = "#e5e7eb";
    });
  });
});
