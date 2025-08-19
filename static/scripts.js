/* static/scripts.js – fixed for proper form submit and UI updates */

(function () {
  /* global backend */
  const base =
    typeof backend !== "undefined" && backend && backend !== "None" ? backend : "";

  // ===== Utilities =====
  const qs  = (sel) => document.querySelector(sel);

  // ===== Modal controls (used by inline HTML handlers) =====
  function openModal() {
    const m = qs("#personModal");
    if (m) m.style.display = "block";
  }
  function closeModal() {
    const m = qs("#personModal");
    if (m) m.style.display = "none";
    const form = qs("#addPersonForm");
    if (form) form.reset();
  }
  window.handleClick = openModal;
  window.closeModal  = closeModal;

  // Close modal on backdrop click / ESC
  window.addEventListener("click", (e) => {
    const m = qs("#personModal");
    if (m && e.target === m) closeModal();
  });
  window.addEventListener("keydown", (e) => {
    if (e.key === "Escape") closeModal();
  });

  // ===== Delete card click (inline handler in HTML) =====
  /**
   * @param {HTMLDivElement} div
   * @param {number} id
   */
  window.handlePersonClick = async function (div, id) {
    const cssClass = div?.className || "";
    if (cssClass === "person-disabled") return;
    if (!id) return;

    const doRemoveInDom = () => {
      const parent = div.parentElement;
      if (!parent) return;
      parent.removeChild(div);
      if (parent.children.length === 0) {
        const grandparent = parent.parentElement;
        if (grandparent) grandparent.removeChild(parent);
      }
    };

    try {
      // First try DELETE, then gracefully fallback to POST (some servers only allow POST)
      let res = await fetch(`${base}/delete/${id}`, { method: "DELETE" });
      if (res.status === 405 || res.status === 404) {
        res = await fetch(`${base}/delete/${id}`, { method: "POST" });
      }
      if (res.ok) {
        doRemoveInDom();
      } else {
        alert("Delete failed");
      }
    } catch (err) {
      console.error(err);
      alert("Network error");
    }
  };

  // ===== Add-person form submit =====
  document.addEventListener("DOMContentLoaded", () => {
    const form = qs("#addPersonForm");
    if (!form) return;

    form.addEventListener("submit", async (event) => {
      event.preventDefault();

      // Collect form values by ID
      const val = (id) => (qs(`#${id}`)?.value ?? "").toString().trim();
      const firstName = val("firstName");
      const lastName  = val("lastName");
      const age       = val("age");
      const address   = val("address");
      const workplace = val("workplace");

      // Send as application/x-www-form-urlencoded (what the Flask endpoint expects)
      const body = new URLSearchParams();
      body.append("firstName", firstName);
      body.append("lastName",  lastName);
      body.append("age",       age);
      body.append("address",   address);
      body.append("workplace", workplace);

      try {
        const res = await fetch(`${base}/add`, {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body
        });

        if (!res.ok) {
          const t = await res.text().catch(() => "");
          console.error("Save failed:", res.status, t);
          alert("Something went wrong");
          return;
        }

        // Server returns plain text (id) or redirects; reload to show latest list
        closeModal();
        window.location.reload();
      } catch (err) {
        console.error(err);
        alert("Network error");
      }
    });
  });

})();

