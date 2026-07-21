/* Expense Tracker — global UI behaviors */
document.addEventListener("DOMContentLoaded", function () {
  // ---------- Mobile sidebar toggle ----------
  const sidebar = document.getElementById("appSidebar");
  const backdrop = document.getElementById("sidebarBackdrop");
  const openBtn = document.getElementById("sidebarToggle");
  const closeBtn = document.getElementById("sidebarClose");

  function openSidebar() {
    sidebar && sidebar.classList.add("show");
    backdrop && backdrop.classList.add("show");
  }
  function closeSidebar() {
    sidebar && sidebar.classList.remove("show");
    backdrop && backdrop.classList.remove("show");
  }
  openBtn && openBtn.addEventListener("click", openSidebar);
  closeBtn && closeBtn.addEventListener("click", closeSidebar);
  backdrop && backdrop.addEventListener("click", closeSidebar);

  // ---------- Dark mode toggle ----------
  const themeBtn = document.getElementById("themeToggleBtn");
  const iconDark = document.getElementById("themeIconDark");
  const iconLight = document.getElementById("themeIconLight");
  const htmlEl = document.documentElement;

  function reflectTheme(theme) {
    htmlEl.setAttribute("data-bs-theme", theme);
    if (theme === "dark") {
      iconDark && iconDark.classList.add("d-none");
      iconLight && iconLight.classList.remove("d-none");
    } else {
      iconDark && iconDark.classList.remove("d-none");
      iconLight && iconLight.classList.add("d-none");
    }
  }
  reflectTheme(htmlEl.getAttribute("data-bs-theme") || "light");

  themeBtn && themeBtn.addEventListener("click", function () {
    const current = htmlEl.getAttribute("data-bs-theme") || "light";
    const next = current === "dark" ? "light" : "dark";
    reflectTheme(next);

    fetch("/profile/settings/theme", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content,
      },
      body: JSON.stringify({ theme: next }),
    }).catch(() => {});
  });

  // ---------- Confirm-delete modals ----------
  document.querySelectorAll("form.confirm-delete").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const msg = form.dataset.confirmMessage || "Are you sure you want to delete this item?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });

  // ---------- Auto-dismiss flash alerts ----------
  document.querySelectorAll(".flash-container .alert").forEach(function (alertEl) {
    setTimeout(function () {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alertEl);
      bsAlert && bsAlert.close();
    }, 6000);
  });

  // ---------- Transaction type -> category filtering (add/edit form) ----------
  const typeSelect = document.getElementById("type");
  const categorySelect = document.getElementById("category_id");

  function filterCategoryOptions() {
    if (!typeSelect || !categorySelect) return;
    const selectedType = typeSelect.value;
    let firstVisibleValue = null;
    let currentStillVisible = false;

    Array.from(categorySelect.options).forEach(function (opt) {
      const matches = opt.dataset.type === selectedType;
      opt.hidden = !matches;
      opt.disabled = !matches;
      if (matches && firstVisibleValue === null) firstVisibleValue = opt.value;
      if (matches && opt.value === categorySelect.value) currentStillVisible = true;
    });

    if (!currentStillVisible && firstVisibleValue !== null) {
      categorySelect.value = firstVisibleValue;
    }
  }

  if (typeSelect && categorySelect) {
    filterCategoryOptions();
    typeSelect.addEventListener("change", filterCategoryOptions);
  }

  // ---------- File input preview label ----------
  const fileInput = document.getElementById("receipt");
  if (fileInput) {
    fileInput.addEventListener("change", function () {
      const label = document.getElementById("receiptFileName");
      if (label) {
        label.textContent = fileInput.files.length ? fileInput.files[0].name : "No file selected";
      }
    });
  }
});
