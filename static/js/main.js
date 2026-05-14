/* ─────────────────────────────────────────────
   CS665 Bookstore — main.js
   ───────────────────────────────────────────── */

document.addEventListener("DOMContentLoaded", () => {

  // ── Confirm delete dialogs ──
  document.querySelectorAll("form.confirm-delete").forEach(form => {
    form.addEventListener("submit", e => {
      if (!confirm("Are you sure you want to delete this record? This action cannot be undone.")) {
        e.preventDefault();
      }
    });
  });

  // ── Auto-dismiss flash messages after 5 seconds ──
  document.querySelectorAll(".alert.alert-success, .alert.alert-danger").forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // ── Highlight active nav link ──
  const path = window.location.pathname;
  document.querySelectorAll(".navbar-nav .nav-link").forEach(link => {
    const href = link.getAttribute("href");
    if (href && href !== "/" && path.startsWith(href)) {
      link.classList.add("active");
    }
  });

  // ── Book price preview on order form ──
  const bookSelect = document.querySelector('select[name="book_id"]');
  const qtyInput   = document.querySelector('input[name="quantity"]');
  const preview    = document.getElementById("price-preview");

  if (bookSelect && qtyInput && preview) {
    const prices = {};
    bookSelect.querySelectorAll("option[data-price]").forEach(opt => {
      prices[opt.value] = parseFloat(opt.dataset.price);
    });

    function updatePreview() {
      const price = prices[bookSelect.value];
      const qty   = parseInt(qtyInput.value) || 1;
      if (price) {
        preview.textContent = `Subtotal: $${(price * qty).toFixed(2)}`;
        preview.classList.remove("d-none");
      } else {
        preview.classList.add("d-none");
      }
    }

    bookSelect.addEventListener("change", updatePreview);
    qtyInput.addEventListener("input", updatePreview);
  }

});
