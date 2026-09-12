// Minimal vanilla-JS viewer: fetches comments and posts new ones.
// The Artifact YAML remains the source of truth; this only talks to the
// small local Review Server's JSON API.

async function fetchComments() {
  const res = await fetch("/api/comments");
  if (!res.ok) return;
  const comments = await res.json();

  document.querySelectorAll(".section-comments").forEach((el) => {
    el.innerHTML = "";
  });

  comments.forEach((comment) => {
    const container = document.querySelector(
      `.section-comments[data-section-id="${comment.target}"]`
    );
    if (!container) return;

    const item = document.createElement("div");
    item.className = `comment comment-status-${comment.status}`;

    const meta = document.createElement("div");
    meta.className = "comment-meta";
    meta.innerHTML = `<span class="comment-id">${comment.id}</span><span class="comment-status">${comment.status}</span>`;

    const body = document.createElement("div");
    body.className = "comment-body";
    body.textContent = comment.comment;

    item.appendChild(meta);
    item.appendChild(body);
    container.appendChild(item);
  });
}

function setupCommentForms() {
  document.querySelectorAll(".add-comment-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const sectionId = btn.dataset.sectionId;
      const form = document.querySelector(
        `.comment-form[data-section-id="${sectionId}"]`
      );
      if (form) form.hidden = !form.hidden;
    });
  });

  document.querySelectorAll(".comment-form").forEach((form) => {
    const cancelBtn = form.querySelector(".cancel-btn");
    cancelBtn.addEventListener("click", () => {
      form.hidden = true;
      form.querySelector("textarea").value = "";
    });

    form.addEventListener("submit", async (event) => {
      event.preventDefault();
      const sectionId = form.dataset.sectionId;
      const textarea = form.querySelector("textarea");
      const comment = textarea.value.trim();
      if (!comment) return;

      const res = await fetch("/api/comments", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ target: sectionId, comment }),
      });

      if (!res.ok) {
        const body = await res.json().catch(() => ({}));
        alert(`コメントの保存に失敗しました: ${body.detail || res.statusText}`);
        return;
      }

      textarea.value = "";
      form.hidden = true;
      await fetchComments();
    });
  });
}

document.addEventListener("DOMContentLoaded", () => {
  setupCommentForms();
  fetchComments();
});
