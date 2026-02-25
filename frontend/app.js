/**
 * app.js – TaskFlow Frontend
 * Vanilla JS (ES Modules), no build step required.
 *
 * Architecture:
 *   Config  → API URLs & constants
 *   State   → in-memory store
 *   API     → fetch() helpers for every CRUD endpoint
 *   Render  → pure functions that build DOM from data
 *   Handlers→ event callbacks that call API then re-render
 *   UI      → toast, spinner, modal utilities
 *   Init    → wires up all event listeners & initial load
 */

"use strict";

// ═══════════════════════════════════════════════════════════════════════════
// 1. CONFIG – swap BASE_URL to your Render URL in production
// ═══════════════════════════════════════════════════════════════════════════


// ── Production backend URL (fill in after Render deploy) ─────────────────────
const PROD_API = "https://your-taskflow-api.onrender.com";

const CONFIG = {
    // Auto-detect: local dev → localhost, everywhere else → Render backend
    BASE_URL: (window.location.hostname === "127.0.0.1" ||
        window.location.hostname === "localhost")
        ? "http://127.0.0.1:8000"
        : PROD_API,

    TASKS_PATH: "/tasks",
    TOAST_DURATION_MS: 3000,
};

const API = {
    tasks: () => `${CONFIG.BASE_URL}${CONFIG.TASKS_PATH}/`,
    task: (id) => `${CONFIG.BASE_URL}${CONFIG.TASKS_PATH}/${id}`,
    complete: (id) => `${CONFIG.BASE_URL}${CONFIG.TASKS_PATH}/${id}/complete`,
};

// ═══════════════════════════════════════════════════════════════════════════
// 2. STATE
// ═══════════════════════════════════════════════════════════════════════════

const state = {
    tasks: [],            // full list from API
    activeStatus: "all",  // current status filter
    activePriority: "all",// current priority filter
    editingId: null,      // task ID being edited (null = create mode)
    pendingDeleteId: null,// task ID waiting for modal confirmation
};

// ═══════════════════════════════════════════════════════════════════════════
// 3. DOM REFS
// ═══════════════════════════════════════════════════════════════════════════

const $ = (id) => document.getElementById(id);

const DOM = {
    form: $("task-form"),
    taskId: $("task-id"),
    title: $("task-title"),
    description: $("task-description"),
    priority: $("task-priority"),
    dueDate: $("task-due-date"),
    submitBtn: $("submit-btn"),
    submitLabel: $("submit-label"),
    cancelEditBtn: $("cancel-edit-btn"),
    formHeading: $("form-heading"),
    formPanel: document.querySelector(".form-panel"),
    taskList: $("task-list"),
    loading: $("loading-overlay"),
    emptyState: $("empty-state"),
    toastContainer: $("toast-container"),
    taskCountBadge: $("task-count-badge"),
    filterPills: document.querySelectorAll("[data-filter-status]"),
    priorityFilter: $("priority-filter"),
    refreshBtn: $("refresh-btn"),
    confirmModal: $("confirm-modal"),
    modalCancelBtn: $("modal-cancel-btn"),
    modalConfirmBtn: $("modal-confirm-btn"),
    titleError: $("title-error"),
};

// ═══════════════════════════════════════════════════════════════════════════
// 4. API HELPERS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Thin wrapper around fetch().
 * Automatically sets JSON headers; throws a descriptive error on non-2xx.
 *
 * @param {string} url
 * @param {RequestInit} [options]
 * @returns {Promise<any>} Parsed JSON response body
 */
async function fetchJSON(url, options = {}) {
    const defaults = {
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
    };
    const config = { ...defaults, ...options };
    if (config.body && typeof config.body !== "string") {
        config.body = JSON.stringify(config.body);
    }

    const res = await fetch(url, config);
    const data = await res.json().catch(() => ({}));

    if (!res.ok) {
        const msg = data?.detail || `HTTP ${res.status}: ${res.statusText}`;
        throw new Error(msg);
    }
    return data;
}

// ── CRUD wrappers ──────────────────────────────────────────────────────────

async function apiGetTasks({ status, priority } = {}) {
    const params = new URLSearchParams();
    if (status && status !== "all") params.set("status", status);
    if (priority && priority !== "all") params.set("priority", priority);
    const qs = params.toString() ? `?${params}` : "";
    return fetchJSON(`${API.tasks()}${qs}`);
}

async function apiCreateTask(payload) {
    return fetchJSON(API.tasks(), { method: "POST", body: payload });
}

async function apiUpdateTask(id, payload) {
    return fetchJSON(API.task(id), { method: "PUT", body: payload });
}

async function apiCompleteTask(id) {
    return fetchJSON(API.complete(id), { method: "PATCH" });
}

async function apiDeleteTask(id) {
    return fetchJSON(API.task(id), { method: "DELETE" });
}

// ═══════════════════════════════════════════════════════════════════════════
// 5. RENDER
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Returns the display label and chip CSS class for a given status string.
 */
function statusChip(status) {
    const map = {
        todo: { label: "To Do", cls: "chip-todo" },
        in_progress: { label: "In Progress", cls: "chip-in_progress" },
        done: { label: "Done", cls: "chip-done" },
    };
    return map[status] ?? { label: status, cls: "" };
}

/**
 * Returns the display label and chip CSS class for a given priority string.
 */
function priorityChip(priority) {
    const map = {
        low: { label: "🟢 Low", cls: "chip-low" },
        medium: { label: "🟡 Medium", cls: "chip-medium" },
        high: { label: "🔴 High", cls: "chip-high" },
    };
    return map[priority] ?? { label: priority, cls: "" };
}

/**
 * Formats an ISO datetime string for display. Returns "" if falsy.
 */
function formatDate(iso) {
    if (!iso) return "";
    const d = new Date(iso);
    return d.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" });
}

/**
 * Returns true if the given ISO datetime has already passed.
 */
function isOverdue(iso) {
    return iso && new Date(iso) < new Date();
}

/**
 * Build the HTML string for a single task card.
 * @param {Object} task – TaskOut from the API
 * @returns {string} HTML
 */
function buildCard(task) {
    const sc = statusChip(task.status);
    const pc = priorityChip(task.priority);
    const doneClass = task.is_completed ? " is-done" : "";
    const dueTxt = formatDate(task.due_date);
    const overdueClass = isOverdue(task.due_date) && !task.is_completed ? " overdue" : "";

    return `
    <li class="task-card${doneClass}" data-task-id="${task.id}" role="listitem">
      <div class="task-card-top">
        <h3 class="task-title">${escHtml(task.title)}</h3>
      </div>

      ${task.description
            ? `<p class="task-description">${escHtml(task.description)}</p>`
            : ""}

      <div class="task-meta">
        <span class="chip ${sc.cls}">${sc.label}</span>
        <span class="chip ${pc.cls}">${pc.label}</span>
        ${dueTxt
            ? `<span class="task-due${overdueClass}" title="Due date">📅 ${dueTxt}${overdueClass ? " (overdue)" : ""}</span>`
            : ""}
      </div>

      <div class="task-actions">
        ${!task.is_completed
            ? `<button class="btn btn-icon btn-ghost btn-complete"
               data-id="${task.id}" title="Mark complete" aria-label="Mark task complete">
               ✓ Complete
             </button>`
            : ""}
        <button class="btn btn-icon btn-ghost btn-edit"
          data-id="${task.id}" title="Edit task" aria-label="Edit task">
          ✏ Edit
        </button>
        <button class="btn btn-icon btn-danger btn-delete"
          data-id="${task.id}" title="Delete task" aria-label="Delete task">
          🗑 Delete
        </button>
      </div>
    </li>`.trim();
}

/**
 * Re-render the entire task list from state.tasks applying active filters.
 */
function renderTaskList() {
    const filtered = state.tasks.filter((t) => {
        const statusOk = state.activeStatus === "all" || t.status === state.activeStatus;
        const priorityOk = state.activePriority === "all" || t.priority === state.activePriority;
        return statusOk && priorityOk;
    });

    DOM.taskList.innerHTML = filtered.map(buildCard).join("");

    // Empty state
    if (filtered.length === 0) {
        DOM.emptyState.hidden = false;
    } else {
        DOM.emptyState.hidden = true;
    }

    // Badge
    DOM.taskCountBadge.textContent =
        `${state.tasks.length} task${state.tasks.length !== 1 ? "s" : ""}`;
}

// ═══════════════════════════════════════════════════════════════════════════
// 6. DATA LOADING
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Fetch tasks from the API, update state, and re-render.
 * Respects the active status / priority filter.
 */
async function loadTasks() {
    setLoading(true);
    try {
        const res = await apiGetTasks({
            status: state.activeStatus,
            priority: state.activePriority,
        });
        state.tasks = res.data?.tasks ?? [];
        renderTaskList();
    } catch (err) {
        showToast(`Failed to load tasks: ${err.message}`, "error");
    } finally {
        setLoading(false);
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// 7. FORM HANDLERS
// ═══════════════════════════════════════════════════════════════════════════

/**
 * Read form fields and return a payload object.
 * Returns null if validation fails.
 */
function readForm() {
    const title = DOM.title.value.trim();
    if (!title) {
        DOM.title.classList.add("is-invalid");
        DOM.titleError.textContent = "Title is required.";
        DOM.titleError.hidden = false;
        DOM.title.focus();
        return null;
    }
    clearValidation();

    const due = DOM.dueDate.value;
    return {
        title,
        description: DOM.description.value.trim() || null,
        priority: DOM.priority.value,
        due_date: due ? new Date(due).toISOString() : null,
    };
}

function clearValidation() {
    DOM.title.classList.remove("is-invalid");
    DOM.titleError.hidden = true;
}

/** Reset form back to "create" mode. */
function resetForm() {
    DOM.form.reset();
    DOM.taskId.value = "";
    state.editingId = null;
    DOM.formHeading.textContent = "Add New Task";
    DOM.submitLabel.textContent = "Create Task";
    DOM.cancelEditBtn.classList.add("hidden");
    DOM.formPanel.classList.remove("editing");
    clearValidation();
}

/** Populate the form with an existing task for editing. */
function populateForm(task) {
    state.editingId = task.id;
    DOM.taskId.value = task.id;
    DOM.title.value = task.title;
    DOM.description.value = task.description ?? "";
    DOM.priority.value = task.priority;

    if (task.due_date) {
        // datetime-local expects "YYYY-MM-DDTHH:MM"
        const d = new Date(task.due_date);
        const local = new Date(d.getTime() - d.getTimezoneOffset() * 60000)
            .toISOString()
            .slice(0, 16);
        DOM.dueDate.value = local;
    } else {
        DOM.dueDate.value = "";
    }

    DOM.formHeading.textContent = "Edit Task";
    DOM.submitLabel.textContent = "Save Changes";
    DOM.cancelEditBtn.classList.remove("hidden");
    DOM.formPanel.classList.add("editing");
    DOM.formPanel.scrollIntoView({ behavior: "smooth", block: "start" });
    DOM.title.focus();
}

/** Handle form submit: create or update. */
async function handleFormSubmit(e) {
    e.preventDefault();
    const payload = readForm();
    if (!payload) return;

    setSubmitting(true);
    try {
        if (state.editingId) {
            await apiUpdateTask(state.editingId, payload);
            showToast("Task updated successfully! ✓", "success");
        } else {
            await apiCreateTask(payload);
            showToast("Task created! ✓", "success");
        }
        resetForm();
        await loadTasks();
    } catch (err) {
        showToast(`Error: ${err.message}`, "error");
    } finally {
        setSubmitting(false);
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// 8. TASK LIST HANDLERS  (event delegation on #task-list)
// ═══════════════════════════════════════════════════════════════════════════

async function handleTaskListClick(e) {
    const completeBtn = e.target.closest(".btn-complete");
    const editBtn = e.target.closest(".btn-edit");
    const deleteBtn = e.target.closest(".btn-delete");

    if (completeBtn) {
        const id = Number(completeBtn.dataset.id);
        await handleComplete(id);
    } else if (editBtn) {
        const id = Number(editBtn.dataset.id);
        handleEdit(id);
    } else if (deleteBtn) {
        const id = Number(deleteBtn.dataset.id);
        openDeleteModal(id);
    }
}

async function handleComplete(id) {
    try {
        await apiCompleteTask(id);
        showToast("Task marked as done! 🎉", "success");
        await loadTasks();
    } catch (err) {
        showToast(`Could not complete task: ${err.message}`, "error");
    }
}

function handleEdit(id) {
    const task = state.tasks.find((t) => t.id === id);
    if (!task) { showToast("Task not found in local state.", "error"); return; }
    populateForm(task);
}

// ═══════════════════════════════════════════════════════════════════════════
// 9. DELETE MODAL
// ═══════════════════════════════════════════════════════════════════════════

function openDeleteModal(id) {
    state.pendingDeleteId = id;
    DOM.confirmModal.classList.add("show");
}

function closeDeleteModal() {
    state.pendingDeleteId = null;
    DOM.confirmModal.classList.remove("show");
}

async function confirmDelete() {
    const id = state.pendingDeleteId;
    if (!id) return;
    closeDeleteModal();
    try {
        await apiDeleteTask(id);
        showToast("Task deleted.", "info");
        await loadTasks();
    } catch (err) {
        showToast(`Could not delete task: ${err.message}`, "error");
    }
}

// ═══════════════════════════════════════════════════════════════════════════
// 10. FILTER HANDLERS
// ═══════════════════════════════════════════════════════════════════════════

function handleStatusPillClick(e) {
    const pill = e.target.closest("[data-filter-status]");
    if (!pill) return;

    state.activeStatus = pill.dataset.filterStatus;

    // Update aria + active class
    DOM.filterPills.forEach((p) => {
        const active = p === pill;
        p.classList.toggle("active", active);
        p.setAttribute("aria-pressed", String(active));
    });

    renderTaskList();
}

function handlePriorityFilterChange() {
    state.activePriority = DOM.priorityFilter.value;
    renderTaskList();
}

// ═══════════════════════════════════════════════════════════════════════════
// 11. UI UTILITIES
// ═══════════════════════════════════════════════════════════════════════════

/** Show / hide the loading spinner. */
function setLoading(visible) {
    DOM.loading.hidden = !visible;
    if (visible) DOM.taskList.innerHTML = "";
}

/** Disable the submit button while a request is in-flight. */
function setSubmitting(active) {
    DOM.submitBtn.disabled = active;
    DOM.submitLabel.textContent = active
        ? (state.editingId ? "Saving…" : "Creating…")
        : (state.editingId ? "Save Changes" : "Create Task");
}

/**
 * Display a toast notification.
 * @param {string} message
 * @param {"success"|"error"|"info"} type
 */
function showToast(message, type = "info") {
    const icons = { success: "✓", error: "✕", info: "ℹ" };
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.style.setProperty("--toast-dur", `${CONFIG.TOAST_DURATION_MS / 1000 - 0.3}s`);
    toast.innerHTML = `<span class="toast-icon">${icons[type] ?? "ℹ"}</span>${escHtml(message)}`;
    toast.setAttribute("role", "status");
    DOM.toastContainer.appendChild(toast);

    // Remove after animation completes
    setTimeout(() => toast.remove(), CONFIG.TOAST_DURATION_MS + 100);
}

/**
 * Escape a string for safe insertion as HTML text content.
 */
function escHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#39;");
}

// ═══════════════════════════════════════════════════════════════════════════
// 12. INITIALISATION
// ═══════════════════════════════════════════════════════════════════════════

function init() {
    // Form submit
    DOM.form.addEventListener("submit", handleFormSubmit);

    // Cancel edit
    DOM.cancelEditBtn.addEventListener("click", resetForm);

    // Task list (delegated)
    DOM.taskList.addEventListener("click", handleTaskListClick);

    // Status filter pills
    document.querySelector(".filter-pills").addEventListener("click", handleStatusPillClick);

    // Priority filter
    DOM.priorityFilter.addEventListener("change", handlePriorityFilterChange);

    // Refresh button
    DOM.refreshBtn.addEventListener("click", loadTasks);

    // Modal buttons
    DOM.modalCancelBtn.addEventListener("click", closeDeleteModal);
    DOM.modalConfirmBtn.addEventListener("click", confirmDelete);

    // Close modal on overlay click
    DOM.confirmModal.addEventListener("click", (e) => {
        if (e.target === DOM.confirmModal) closeDeleteModal();
    });

    // Clear validation on title input
    DOM.title.addEventListener("input", clearValidation);

    // Close modal on Escape
    document.addEventListener("keydown", (e) => {
        if (e.key === "Escape" && !DOM.confirmModal.hidden) closeDeleteModal();
    });

    // Initial data load
    loadTasks();
}

// Run after DOM is ready
document.addEventListener("DOMContentLoaded", init);
