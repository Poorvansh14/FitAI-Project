// Theme toggle and hamburger nav — identically copied from workout.js
const themeToggle = document.getElementById("themeToggle");
const body = document.body;
const moonIcon = '<i class="ri-moon-fill"></i>';
const sunIcon = '<i class="ri-sun-fill"></i>';
let currentTheme = localStorage.getItem("theme") || "light";

body.setAttribute("data-theme", currentTheme);
themeToggle.innerHTML = currentTheme === "dark" ? sunIcon : moonIcon;

themeToggle.onclick = () => {
  const newTheme = body.getAttribute("data-theme") === "dark" ? "light" : "dark";
  body.setAttribute("data-theme", newTheme);
  localStorage.setItem("theme", newTheme);
  themeToggle.innerHTML = newTheme === "dark" ? sunIcon : moonIcon;
};

const navToggle = document.getElementById("navToggle");
const navMenu = document.getElementById("navMenu");
navToggle.onclick = () => navMenu.classList.toggle("open");

// ======================= AI DIET GENERATOR INTEGRATION =======================

// Smoothly reveal results
function showResultWithSmoothEffect(html) {
  const resultDiv = document.getElementById("diet-result");
  resultDiv.classList.remove("visible");
  requestAnimationFrame(() => {
    resultDiv.innerHTML = html;
    requestAnimationFrame(() => {
      resultDiv.classList.add("visible");
    });
  });
}

// Handle diet form submission
document.querySelector(".diet-form").addEventListener("submit", async function (e) {
  e.preventDefault();

  showResultWithSmoothEffect(
    `<span style="color:var(--muted);">Generating your personalized AI Diet Plan...</span>`
  );

  const payload = {
    weight: document.getElementById("weight").value,
    goal: document.getElementById("goal").value,
    cuisine: document.getElementById("cuisine").value,
    food_preference: document.getElementById("food-preference").value,
    restrictions: document.getElementById("restrictions").value,
    meals: document.getElementById("meals").value,
  };

  try {
    const response = await fetch("http://127.0.0.1:5000/api/generate_diet", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) throw new Error("Network response was not ok");

    const data = await response.json();

    if (data && data.plan) {
      showResultWithSmoothEffect(
        `<h3>Your AI Diet Plan</h3><p>${data.plan.replace(/\n/g, "<br>")}</p>`
      );
    } else {
      showResultWithSmoothEffect(
        `<span style="color:red;">Error: Could not generate plan. Please try again.</span>`
      );
    }
  } catch (err) {
    console.error(err);
    showResultWithSmoothEffect(
      `<span style="color:red;">Something went wrong. Check your server or API key.</span>`
    );
  }
});
