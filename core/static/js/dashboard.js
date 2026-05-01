// Store open/close toggle
const toggle = document.getElementById("storeToggle");

if (toggle) {
  toggle.addEventListener("click", () => {
    if (toggle.textContent === "Open") {
      toggle.textContent = "Closed";
      toggle.style.background = "red";
    } else {
      toggle.textContent = "Open";
      toggle.style.background = "green";
    }
  });
}