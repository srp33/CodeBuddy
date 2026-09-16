/**
 * Canvas gradebook wizard for CodeBuddy.
 * Steps: credentials → align students → select assignments → push scores.
 */
(function (window) {
  "use strict";

  function esc(value) {
    return String(value == null ? "" : value)
      .replace(/&/g, "&amp;")
      .replace(/</g, "&lt;")
      .replace(/>/g, "&gt;")
      .replace(/"/g, "&quot;");
  }

  function normalizeKey(value) {
    let s = String(value == null ? "" : value).trim().toLowerCase();
    if (s.indexOf("@") !== -1) {
      s = s.split("@", 1)[0].trim();
    }
    return s;
  }

  function normalizeAssignmentName(value) {
    return String(value == null ? "" : value)
      .trim()
      .toLowerCase()
      .replace(/\s+/g, " ");
  }

  function formatCanvasSubmissionTimestamp(text) {
    if (!text) {
      return "No submissions yet";
    }
    const date = new Date(text);
    if (Number.isNaN(date.getTime())) {
      return String(text);
    }
    const months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];
    const month = months[date.getMonth()];
    const day = String(date.getDate()).padStart(2, "0");
    const year = date.getFullYear();
    const hour = String(date.getHours()).padStart(2, "0");
    const minute = String(date.getMinutes()).padStart(2, "0");
    return `${month} ${day}, ${year}, ${hour}:${minute}`;
  }

  function formatScoreValue(value) {
    if (value == null || value === "") {
      return "—";
    }
    const number = Number(value);
    if (Number.isNaN(number)) {
      return "—";
    }
    const rounded = Math.round(number * 10) / 10;
    return Number.isInteger(rounded) ? String(rounded) : rounded.toFixed(1);
  }

  function canvasScoreAsPercent(entry, pointsPossible) {
    if (!entry || entry.score == null || entry.score === "") {
      return null;
    }
    const score = Number(entry.score);
    if (Number.isNaN(score)) {
      return null;
    }
    const points = Number(pointsPossible);
    if (points > 0) {
      return (score / points) * 100;
    }
    return score;
  }

  class CanvasGradeWizard {
    constructor(options) {
      this.options = options || {};
      this.codebuddyCourseId = String(this.options.codebuddyCourseId || "");
      this.modal = document.getElementById("canvas_modal");
      this.errorEl = document.getElementById("canvas_modal_error");
      this.statusEl = document.getElementById("canvas_modal_status");
      this.nextBtn = document.getElementById("canvas_modal_next_btn");
      this.backBtn = document.getElementById("canvas_modal_back_btn");
      this.nextLabel = document.getElementById("canvas_modal_next_label");
      this.spinner = document.getElementById("canvas_modal_spinner");
      this.matchFieldEl = document.getElementById("canvas_match_field");
      this.state = this._emptyState();
      this._bind();
    }

    _emptyState() {
      return {
        step: 1,
        credentials: null,
        hasSavedToken: false,
        canvasAssignments: [],
        canvasStudents: [],
        gradebook: null,
        matchField: "login_id",
        alignment: new Map(),
        pushing: false,
        pushNotes: {},
        canvasScores: {},
        selectedAssignments: {},
      };
    }

    _bind() {
      document.getElementById("canvas_modal_close")?.addEventListener("click", () => this.close());
      document.getElementById("canvas_modal_cancel_btn")?.addEventListener("click", () => this.close());
      this.backBtn?.addEventListener("click", () => this._back());
      this.nextBtn?.addEventListener("click", () => this._next());
      document.getElementById("canvas_clear_saved_btn")?.addEventListener("click", (event) => {
        event.preventDefault();
        this._clearSavedCredentials();
      });
      this.matchFieldEl?.addEventListener("change", () => {
        this.state.matchField = this.matchFieldEl.value;
        this._renderAlignTable();
      });
      document.getElementById("canvas_push_scores_btn")?.addEventListener("click", () => {
        this._pushSelectedAssignments();
      });
      for (let i = 1; i <= 4; i++) {
        document.getElementById(`canvas_step_pill_${i}`)?.addEventListener("click", () => {
          if (this.state.pushing) return;
          if (i < this.state.step) this._showStep(i);
        });
      }
      window.addEventListener("click", (event) => {
        if (event.target === this.modal && !this.state.pushing) {
          this.close();
        }
      });
    }

    async open() {
      if (!this.modal) return;
      this.state = this._emptyState();
      this._setError("");
      this._setStatus("");
      const tokenInput = document.getElementById("canvas_access_token");
      if (tokenInput) tokenInput.value = "";
      document.getElementById("canvas_base_url").value = "";
      document.getElementById("canvas_course_id").value = "";
      const includeZeros = document.getElementById("canvas_include_zero_scores");
      if (includeZeros) includeZeros.checked = true;
      this._showStep(1);
      this.modal.style.display = "flex";
      await this._loadSavedCredentials();
      document.getElementById("canvas_base_url")?.focus();
    }

    close() {
      if (this.state.pushing) return;
      if (this.modal) this.modal.style.display = "none";
      this.state = this._emptyState();
      this._setError("");
      this._setStatus("");
      this._setLoading(false);
    }

    _setError(message) {
      if (!this.errorEl) return;
      if (!message) {
        this.errorEl.classList.add("is-hidden");
        this.errorEl.textContent = "";
        return;
      }
      this.errorEl.textContent = message;
      this.errorEl.classList.remove("is-hidden");
    }

    _setStatus(message, kind) {
      if (!this.statusEl) return;
      this.statusEl.classList.remove("is-warning", "is-primary", "success-message");
      if (!message) {
        this.statusEl.classList.add("is-hidden");
        this.statusEl.textContent = "";
        return;
      }
      if (kind === "pending") {
        this.statusEl.classList.add("is-warning");
      } else {
        this.statusEl.classList.add("is-primary");
      }
      this.statusEl.textContent = message;
      this.statusEl.classList.remove("is-hidden");
    }

    _assignmentTitle(codebuddyAssignmentId) {
      const assignments = (this.state.gradebook && this.state.gradebook.assignments) || [];
      const assignment = assignments.find((item) => String(item.id) === String(codebuddyAssignmentId));
      const title = assignment && assignment.title ? String(assignment.title).trim() : "";
      return title || "this assignment";
    }

    _setLoading(loading) {
      if (this.spinner) this.spinner.classList.toggle("is-hidden", !loading);
      if (this.nextBtn) this.nextBtn.disabled = loading || this.state.pushing;
      if (this.backBtn) this.backBtn.disabled = loading || this.state.pushing;
      const pushBtn = document.getElementById("canvas_push_scores_btn");
      const includeZeros = document.getElementById("canvas_include_zero_scores");
      if (pushBtn) pushBtn.disabled = loading || this.state.pushing;
      if (includeZeros) includeZeros.disabled = loading || this.state.pushing;
      document.querySelectorAll(".canvas-select-checkbox").forEach((box) => {
        box.disabled = loading || this.state.pushing;
      });
      document.querySelectorAll(".canvas-group-select").forEach((button) => {
        button.disabled = loading || this.state.pushing;
      });
    }

    _credentialsFromForm() {
      return {
        base_url: (document.getElementById("canvas_base_url")?.value || "").trim(),
        course_id: (document.getElementById("canvas_course_id")?.value || "").trim(),
        access_token: (document.getElementById("canvas_access_token")?.value || "").trim(),
        codebuddy_course_id: this.codebuddyCourseId,
      };
    }

    _activeCredentials() {
      const form = this._credentialsFromForm();
      const saved = this.state.credentials || {};
      return {
        base_url: form.base_url || saved.base_url || "",
        course_id: form.course_id || saved.course_id || "",
        access_token: form.access_token || "",
        codebuddy_course_id: this.codebuddyCourseId,
      };
    }

    _showStep(step) {
      this.state.step = step;
      for (let i = 1; i <= 4; i++) {
        const panel = document.getElementById(`canvas_step_${i}`);
        if (panel) panel.classList.toggle("is-hidden", i !== step);
        const pill = document.getElementById(`canvas_step_pill_${i}`);
        if (pill) {
          pill.classList.toggle("is-active", i === step);
          pill.classList.toggle("is-done", i < step);
          pill.classList.toggle("is-clickable", i < step);
        }
      }
      if (this.backBtn) {
        this.backBtn.classList.toggle("is-hidden", step === 1);
        this.backBtn.textContent = step === 4 ? "Back to assignments" : "Back";
      }
      if (this.nextBtn) {
        this.nextBtn.classList.toggle("is-hidden", step === 4);
      }
      if (this.nextLabel) {
        this.nextLabel.textContent = "Continue";
      }
      if (step === 3) {
        this._renderAssignmentsTable();
      }
      if (step === 4) {
        this._renderPushScoresTable();
      }
    }

    async _loadSavedCredentials() {
      try {
        const res = await fetch(`/api/canvas/saved-credentials?codebuddy_course_id=${encodeURIComponent(this.codebuddyCourseId)}`, {
          credentials: "same-origin",
        });
        const data = await res.json().catch(() => ({}));
        if (!res.ok) return;
        this.state.hasSavedToken = !!data.has_token;
        this.state.credentials = {
          base_url: data.base_url || "",
          course_id: data.course_id || "",
        };
        if (data.base_url) document.getElementById("canvas_base_url").value = data.base_url;
        if (data.course_id) document.getElementById("canvas_course_id").value = data.course_id;
        const note = document.getElementById("canvas_saved_creds_note");
        if (note) note.classList.toggle("is-hidden", !data.has_token);
        const tokenInput = document.getElementById("canvas_access_token");
        if (tokenInput) {
          tokenInput.required = !data.has_token;
          tokenInput.placeholder = data.has_token
            ? "Saved token on file (leave blank to reuse)"
            : "Canvas API access token";
        }
      } catch (e) {
        // Ignore prefills on network failure.
      }
    }

    async _clearSavedCredentials() {
      try {
        await fetch(`/api/canvas/saved-credentials?codebuddy_course_id=${encodeURIComponent(this.codebuddyCourseId)}`, {
          method: "DELETE",
          credentials: "same-origin",
        });
      } catch (e) {
        // Ignore.
      }
      this.state.hasSavedToken = false;
      this.state.credentials = null;
      const note = document.getElementById("canvas_saved_creds_note");
      if (note) note.classList.add("is-hidden");
      const tokenInput = document.getElementById("canvas_access_token");
      if (tokenInput) {
        tokenInput.value = "";
        tokenInput.required = true;
        tokenInput.placeholder = "Canvas API access token";
      }
    }

    async _next() {
      this._setError("");
      this._setStatus("");
      if (this.state.step === 1) {
        await this._connectAndLoad();
      } else if (this.state.step === 2) {
        this._showStep(3);
      } else if (this.state.step === 3) {
        await this._continueToPushScores();
      }
    }

    _back() {
      if (this.state.pushing) return;
      this._setError("");
      if (this.state.step === 4) {
        this._backToAssignments();
        return;
      }
      this._setStatus("");
      if (this.state.step > 1) {
        this._showStep(this.state.step - 1);
      }
    }

    _backToAssignments() {
      if (this.state.pushing) return;
      this._setError("");
      this._showStep(3);
    }

    async _connectAndLoad() {
      const credentials = this._credentialsFromForm();
      if (!credentials.base_url || !credentials.course_id) {
        this._setError("Canvas base URL and course ID are required.");
        return;
      }
      if (!credentials.access_token && !this.state.hasSavedToken) {
        this._setError("Access token is required.");
        return;
      }

      this._setLoading(true);
      try {
        const [assignRes, studentRes, gradebookRes] = await Promise.all([
          fetch("/api/canvas/assignments", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(credentials),
          }),
          fetch("/api/canvas/students", {
            method: "POST",
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(credentials),
          }),
          fetch(`/api/canvas/course_gradebook/${encodeURIComponent(this.codebuddyCourseId)}`, {
            credentials: "same-origin",
          }),
        ]);

        const assignData = await assignRes.json().catch(() => ({}));
        const studentData = await studentRes.json().catch(() => ({}));
        const gradebookData = await gradebookRes.json().catch(() => ({}));

        if (!assignRes.ok) {
          this._setError(assignData.error || "Could not load Canvas assignments.");
          if (assignRes.status === 401) await this._clearSavedCredentials();
          return;
        }
        if (!studentRes.ok) {
          this._setError(studentData.error || "Could not load Canvas students.");
          if (studentRes.status === 401) await this._clearSavedCredentials();
          return;
        }
        if (!gradebookRes.ok) {
          this._setError(gradebookData.error || "Could not load CodeBuddy scores.");
          return;
        }

        this.state.credentials = {
          base_url: assignData.base_url || credentials.base_url,
          course_id: assignData.course_id || credentials.course_id,
        };
        this.state.hasSavedToken = true;
        this.state.canvasAssignments = assignData.assignments || [];
        this.state.canvasStudents = studentData.students || [];
        this.state.gradebook = gradebookData;
        this.state.pushNotes = {};
        this.state.canvasScores = {};
        this.state.selectedAssignments = {};

        const note = document.getElementById("canvas_saved_creds_note");
        if (note) note.classList.remove("is-hidden");
        const tokenInput = document.getElementById("canvas_access_token");
        if (tokenInput) {
          tokenInput.value = "";
          tokenInput.required = false;
          tokenInput.placeholder = "Saved token on file (leave blank to reuse)";
        }

        this._renderAlignTable();
        this._showStep(2);
      } catch (e) {
        this._setError("Network error while contacting Canvas or CodeBuddy.");
      } finally {
        this._setLoading(false);
      }
    }

    _codebuddyKeyMap() {
      const map = new Map();
      const students = (this.state.gradebook && this.state.gradebook.students) || [];
      students.forEach((student) => {
        const userId = String(student.user_id || "");
        const keys = [
          normalizeKey(userId),
          normalizeKey(student.email),
        ];
        keys.forEach((key) => {
          if (key && !map.has(key)) {
            map.set(key, student);
          }
        });
      });
      return map;
    }

    _renderAlignTable() {
      const tbody = document.getElementById("canvas_align_tbody");
      const summary = document.getElementById("canvas_align_summary");
      const header = document.getElementById("canvas_align_field_header");
      const field = this.state.matchField || "login_id";
      if (header) header.textContent = `Canvas ${field}`;
      if (!tbody) return;

      const keyMap = this._codebuddyKeyMap();
      this.state.alignment = new Map();
      let aligned = 0;
      const students = (this.state.canvasStudents || []).slice().sort((a, b) => {
        const nameA = String(a && a.name ? a.name : "");
        const nameB = String(b && b.name ? b.name : "");
        return nameA.localeCompare(nameB, navigator.languages[0] || navigator.language, {
          numeric: true,
          ignorePunctuation: true,
          sensitivity: "base",
        });
      });
      const rows = students.map((student) => {
        const canvasValue = student[field] || "";
        const key = normalizeKey(canvasValue);
        const match = key ? keyMap.get(key) : null;
        if (match) {
          aligned += 1;
          this.state.alignment.set(String(student.id), match);
        }
        return `
          <tr>
            <td>${esc(student.name || "")}</td>
            <td class="is-family-monospace">${esc(canvasValue || "—")}</td>
            <td>${match ? esc(`${match.name} (${match.user_id})`) : "<em>Not aligned</em>"}</td>
          </tr>
        `;
      });
      tbody.innerHTML = rows.join("") || `<tr><td colspan="3"><em>No Canvas students found.</em></td></tr>`;
      if (summary) {
        const total = (this.state.canvasStudents || []).length;
        summary.textContent = `${aligned} of ${total} Canvas student${total === 1 ? "" : "s"} aligned`;
      }
    }

    _canvasAssignmentByName() {
      const map = new Map();
      (this.state.canvasAssignments || []).forEach((assignment) => {
        const key = normalizeAssignmentName(assignment.name);
        if (!key) return;
        if (!map.has(key)) map.set(key, []);
        map.get(key).push(assignment);
      });
      return map;
    }

    _matchedCanvasAssignmentIds() {
      const byName = this._canvasAssignmentByName();
      const ids = [];
      const seen = new Set();
      this._groupedAssignments().forEach((assignment) => {
        const matches = byName.get(normalizeAssignmentName(assignment.title)) || [];
        if (matches.length !== 1 || matches[0].id == null) return;
        const id = String(matches[0].id);
        if (seen.has(id)) return;
        seen.add(id);
        ids.push(id);
      });
      return ids;
    }

    async _loadCanvasScores(assignmentIds, options) {
      const silent = !!(options && options.silent);
      const ids = assignmentIds && assignmentIds.length
        ? assignmentIds.map((id) => String(id))
        : this._matchedCanvasAssignmentIds();
      if (!ids.length) {
        if (!assignmentIds) this.state.canvasScores = {};
        return true;
      }

      const credentials = this._activeCredentials();
      const res = await fetch("/api/canvas/submissions", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...credentials,
          assignment_ids: ids,
        }),
      });
      const data = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (!silent) {
          this._setError(data.error || "Could not load Canvas scores.");
        }
        if (res.status === 401) await this._clearSavedCredentials();
        return false;
      }

      if (!this.state.canvasScores) this.state.canvasScores = {};
      ids.forEach((id) => {
        this.state.canvasScores[id] = (data.scores && data.scores[id]) || {};
      });
      Object.keys(data.scores || {}).forEach((id) => {
        this.state.canvasScores[id] = data.scores[id] || {};
      });
      return true;
    }

    async _continueToPushScores() {
      const selected = this._selectedAssignmentList();
      if (!selected.length) {
        this._setError("Select at least one assignment.");
        return;
      }
      this._setLoading(true);
      this._setStatus("Loading Canvas scores…", "pending");
      try {
        const canvasIds = selected.map((item) => item.canvasId);
        const ok = await this._loadCanvasScores(canvasIds);
        if (!ok) return;
        this._setStatus("");
        this._showStep(4);
      } catch (e) {
        this._setStatus("");
        this._setError("Network error while loading Canvas scores.");
      } finally {
        this._setLoading(false);
      }
    }

    _selectedAssignmentList() {
      const selected = this.state.selectedAssignments || {};
      return this._groupedAssignments()
        .map((assignment) => selected[String(assignment.id)])
        .filter(Boolean);
    }

    _setSelectableAssignments(checked, groupIndex) {
      if (this.state.pushing) return;
      const selector = groupIndex == null
        ? ".canvas-select-checkbox[data-selectable='1']"
        : `.canvas-select-checkbox[data-selectable='1'][data-group='${groupIndex}']`;
      document.querySelectorAll(selector).forEach((box) => {
        box.checked = !!checked;
        this._syncAssignmentCheckbox(box);
      });
      this._updateAssignmentSummary();
    }

    _syncAssignmentCheckbox(box) {
      const codebuddyId = String(box.getAttribute("data-codebuddy-assignment-id") || "");
      if (!codebuddyId) return;
      if (box.checked) {
        const pointsRaw = box.getAttribute("data-points-possible");
        const pointsPossible = pointsRaw === "" || pointsRaw == null ? null : Number(pointsRaw);
        this.state.selectedAssignments[codebuddyId] = {
          codebuddyId: codebuddyId,
          canvasId: String(box.getAttribute("data-canvas-assignment-id") || ""),
          pointsPossible: Number.isNaN(pointsPossible) ? null : pointsPossible,
        };
      } else {
        delete this.state.selectedAssignments[codebuddyId];
      }
    }

    _studentScoreRows(codebuddyAssignmentId, canvasAssignmentId, pointsPossible) {
      const cbScores = ((this.state.gradebook && this.state.gradebook.scores) || {})[String(codebuddyAssignmentId)] || {};
      const canvasScores = (this.state.canvasScores || {})[String(canvasAssignmentId)] || {};
      const rows = [];
      this.state.alignment.forEach((codebuddyStudent, canvasUserId) => {
        rows.push({
          name: (codebuddyStudent && codebuddyStudent.name) || (codebuddyStudent && codebuddyStudent.user_id) || "",
          codebuddy: cbScores[String(codebuddyStudent.user_id)],
          canvas: canvasScoreAsPercent(canvasScores[String(canvasUserId)], pointsPossible),
        });
      });
      rows.sort((a, b) => String(a.name).localeCompare(String(b.name), navigator.languages[0] || navigator.language, {
        numeric: true,
        ignorePunctuation: true,
        sensitivity: "base",
      }));
      return rows;
    }

    _renderPushScoresTable() {
      const root = document.getElementById("canvas_scores_sections");
      const summary = document.getElementById("canvas_scores_summary");
      if (!root) return;

      const selected = this._selectedAssignmentList();
      if (!selected.length) {
        root.innerHTML = `<p><em>Select at least one assignment first.</em></p>`;
        if (summary) summary.textContent = "";
        return;
      }

      root.innerHTML = selected.map((item) => {
        const title = this._assignmentTitle(item.codebuddyId);
        const note = this.state.pushNotes[String(item.codebuddyId)] || "";
        const rows = this._studentScoreRows(item.codebuddyId, item.canvasId, item.pointsPossible);
        const body = rows.length
          ? rows.map((row) => `
              <tr>
                <td>${esc(row.name)}</td>
                <td>${esc(formatScoreValue(row.codebuddy))}</td>
                <td>${esc(formatScoreValue(row.canvas))}</td>
              </tr>
            `).join("")
          : `<tr><td colspan="3"><em>No aligned students.</em></td></tr>`;
        const noteClass = note.ok === false ? "is-error" : (note.ok ? "is-success" : "");
        return `
          <section class="canvas-score-section" data-assignment-id="${esc(item.codebuddyId)}">
            <p class="mb-1 has-text-weight-semibold">${esc(title)}</p>
            <div class="canvas-push-status ${noteClass} mb-2">${esc(note.message || "")}</div>
            <div class="table-container canvas-table-wrap">
              <table class="table is-striped is-fullwidth">
                <thead>
                  <tr>
                    <th>Student</th>
                    <th>CodeBuddy</th>
                    <th>Canvas</th>
                  </tr>
                </thead>
                <tbody>${body}</tbody>
              </table>
            </div>
          </section>
        `;
      }).join("");

      if (summary) {
        summary.textContent = `${selected.length} assignment${selected.length === 1 ? "" : "s"} selected`;
      }
    }

    _groupedAssignments() {
      const assignments = ((this.state.gradebook && this.state.gradebook.assignments) || []).slice();
      assignments.sort((a, b) => {
        const ga = (a.assignment_group_title || "").toLowerCase();
        const gb = (b.assignment_group_title || "").toLowerCase();
        if (ga && !gb) return -1;
        if (!ga && gb) return 1;
        if (ga < gb) return -1;
        if (ga > gb) return 1;
        const ta = (a.title || "").toLowerCase();
        const tb = (b.title || "").toLowerCase();
        if (ta < tb) return -1;
        if (ta > tb) return 1;
        return 0;
      });
      return assignments;
    }

    _renderAssignmentsTable() {
      const tbody = document.getElementById("canvas_assignments_tbody");
      if (!tbody) return;

      const byName = this._canvasAssignmentByName();
      const assignments = this._groupedAssignments();
      let matched = 0;
      const html = [];
      const groups = [];
      assignments.forEach((assignment) => {
        const groupTitle = assignment.assignment_group_title || "Ungrouped";
        const last = groups[groups.length - 1];
        if (!last || last.title !== groupTitle) {
          groups.push({ title: groupTitle, items: [] });
        }
        groups[groups.length - 1].items.push(assignment);
      });

      groups.forEach((group, groupIndex) => {
        const prepared = group.items.map((assignment) => {
          const key = normalizeAssignmentName(assignment.title);
          const matches = byName.get(key) || [];
          let matchLabel = "No matching Canvas assignment";
          let canPush = false;
          let canvasAssignmentId = null;
          const hasSubmissions = !!assignment.has_submissions;
          let pointsPossible = null;
          if (matches.length === 1) {
            matched += 1;
            canvasAssignmentId = matches[0].id;
            matchLabel = matches[0].name || "Matched";
            canPush = hasSubmissions;
            pointsPossible = matches[0].points_possible;
          } else if (matches.length > 1) {
            matchLabel = `Ambiguous (${matches.length} Canvas matches)`;
          }
          return { assignment, matchLabel, canPush, canvasAssignmentId, hasSubmissions, pointsPossible };
        });
        const hasSelectable = prepared.some((item) => item.canPush);
        const groupButtons = hasSelectable
          ? `<div class="buttons mb-0">
                <button type="button" class="button canvas-group-select" data-group="${groupIndex}" data-checked="1" ${this.state.pushing ? "disabled" : ""}>Select all</button>
                <button type="button" class="button canvas-group-select" data-group="${groupIndex}" data-checked="0" ${this.state.pushing ? "disabled" : ""}>Deselect all</button>
              </div>`
          : "";

        html.push(`
          <tr class="canvas-group-row">
            <td colspan="4">
              <div class="canvas-group-heading">
                <strong>${esc(group.title)}</strong>
                ${groupButtons}
              </div>
            </td>
          </tr>
        `);

        prepared.forEach((item) => {
          const lastSubmission = item.hasSubmissions
            ? formatCanvasSubmissionTimestamp(item.assignment.last_submission_timestamp)
            : "No submissions yet";
          const note = this.state.pushNotes[String(item.assignment.id)] || "";
          const isSelected = !!this.state.selectedAssignments[String(item.assignment.id)];
          const checkbox = item.canPush
            ? `<label class="checkbox">
                  <input type="checkbox"
                    class="canvas-select-checkbox"
                    data-selectable="1"
                    data-group="${groupIndex}"
                    data-codebuddy-assignment-id="${esc(item.assignment.id)}"
                    data-canvas-assignment-id="${esc(item.canvasAssignmentId)}"
                    data-points-possible="${esc(item.pointsPossible == null ? "" : item.pointsPossible)}"
                    ${isSelected ? "checked" : ""}
                    ${this.state.pushing ? "disabled" : ""} />
                </label>`
            : "";

          html.push(`
            <tr data-assignment-id="${esc(item.assignment.id)}">
              <td>${esc(item.assignment.title || "")}</td>
              <td>${esc(lastSubmission)}</td>
              <td>${esc(item.matchLabel)}</td>
              <td>
                ${checkbox}
                <div class="canvas-push-status ${note.ok === false ? "is-error" : (note.ok ? "is-success" : "")}" data-note-for="${esc(item.assignment.id)}">
                  ${esc(note.message || "")}
                </div>
              </td>
            </tr>
          `);
        });
      });

      tbody.innerHTML = html.join("") || `<tr><td colspan="4"><em>No CodeBuddy assignments found.</em></td></tr>`;
      this._updateAssignmentSummary(matched, assignments.length);

      tbody.querySelectorAll(".canvas-select-checkbox").forEach((box) => {
        box.addEventListener("change", () => {
          this._syncAssignmentCheckbox(box);
          this._updateAssignmentSummary();
        });
      });
      tbody.querySelectorAll(".canvas-group-select").forEach((button) => {
        button.addEventListener("click", () => {
          const groupIndex = button.getAttribute("data-group");
          const checked = button.getAttribute("data-checked") === "1";
          this._setSelectableAssignments(checked, groupIndex);
        });
      });
    }

    _updateAssignmentSummary(matchedCount, assignmentCount) {
      const summary = document.getElementById("canvas_push_summary");
      if (!summary) return;
      const assignments = this._groupedAssignments();
      const byName = this._canvasAssignmentByName();
      const matched = matchedCount != null
        ? matchedCount
        : assignments.filter((assignment) => {
            const matches = byName.get(normalizeAssignmentName(assignment.title)) || [];
            return matches.length === 1;
          }).length;
      const total = assignmentCount != null ? assignmentCount : assignments.length;
      const selected = this._selectedAssignmentList().length;
      summary.textContent = `${matched} of ${total} assignment${total === 1 ? "" : "s"} matched to Canvas by name. ${selected} selected.`;
    }

    _gradesForAssignment(codebuddyAssignmentId) {
      const includeZeros = document.getElementById("canvas_include_zero_scores")?.checked !== false;
      const scores = ((this.state.gradebook && this.state.gradebook.scores) || {})[String(codebuddyAssignmentId)] || {};
      const grades = [];
      this.state.alignment.forEach((codebuddyStudent, canvasUserId) => {
        const score = scores[String(codebuddyStudent.user_id)];
        if (score == null || score === "" || Number.isNaN(Number(score))) return;
        const numericScore = Number(score);
        if (!includeZeros && numericScore <= 0) return;
        grades.push({
          canvas_user_id: canvasUserId,
          score: numericScore,
        });
      });
      return { grades, includeZeros };
    }

    async _uploadAssignmentGrades(codebuddyAssignmentId, canvasAssignmentId, grades) {
      const credentials = this._activeCredentials();
      const res = await fetch("/api/canvas/grades", {
        method: "POST",
        credentials: "same-origin",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          ...credentials,
          assignment_id: String(canvasAssignmentId),
          grades: grades,
        }),
      });
      const data = await res.json().catch(() => ({}));
      return { res, data };
    }

    async _pushSelectedAssignments() {
      if (this.state.pushing) return;
      const selected = this._selectedAssignmentList();
      if (!selected.length) {
        this._setError("Select at least one assignment.");
        return;
      }

      this.state.pushing = true;
      this._setError("");
      const pushBtn = document.getElementById("canvas_push_scores_btn");
      const previousLabel = pushBtn ? pushBtn.textContent : "";
      if (pushBtn) pushBtn.textContent = "Pushing…";
      this._setLoading(true);

      let succeeded = 0;
      let failed = 0;
      const failures = [];
      let aborted = false;

      try {
        for (let i = 0; i < selected.length; i++) {
          const item = selected[i];
          const title = this._assignmentTitle(item.codebuddyId);
          this._setStatus(`Pushing ${i + 1} of ${selected.length}: ${title}…`, "pending");
          this.state.pushNotes[String(item.codebuddyId)] = { ok: null, message: `Pushing (${i + 1} of ${selected.length})…` };
          this._renderPushScoresTable();

          const { grades, includeZeros } = this._gradesForAssignment(item.codebuddyId);
          if (!grades.length) {
            const message = includeZeros
              ? "No aligned students with scores were found."
              : "No aligned students with a score greater than zero were found.";
            this.state.pushNotes[String(item.codebuddyId)] = { ok: false, message: message };
            failed += 1;
            failures.push(`${title}: ${message}`);
            this._renderPushScoresTable();
            continue;
          }

          try {
            const { res, data } = await this._uploadAssignmentGrades(item.codebuddyId, item.canvasId, grades);
            if (!res.ok) {
              const message = data.error || "Could not upload grades to Canvas.";
              this.state.pushNotes[String(item.codebuddyId)] = { ok: false, message: message };
              failed += 1;
              failures.push(`${title}: ${message}`);
              if (res.status === 401) {
                aborted = true;
                await this._clearSavedCredentials();
                this._setError("Canvas rejected the access token. Remaining assignments were not pushed.");
                break;
              }
              this._renderPushScoresTable();
              continue;
            }
            const uploaded = data.uploaded != null ? data.uploaded : grades.length;
            this.state.pushNotes[String(item.codebuddyId)] = {
              ok: true,
              message: `Uploaded ${uploaded} score${uploaded === 1 ? "" : "s"}.`,
            };
            succeeded += 1;
            await this._loadCanvasScores([String(item.canvasId)], { silent: true });
            this._renderPushScoresTable();
          } catch (e) {
            const message = "Network error while uploading grades.";
            this.state.pushNotes[String(item.codebuddyId)] = { ok: false, message: message };
            failed += 1;
            failures.push(`${title}: ${message}`);
            this._renderPushScoresTable();
          }
        }

        if (!aborted) {
          const parts = [];
          if (succeeded) parts.push(`uploaded ${succeeded} assignment${succeeded === 1 ? "" : "s"}`);
          if (failed) parts.push(`${failed} failed`);
          const summary = parts.length ? `Finished: ${parts.join(", ")}.` : "Finished.";
          if (failed && succeeded) {
            this._setStatus(summary, "success");
            this._setError(failures.join(" "));
          } else if (failed) {
            this._setStatus("");
            this._setError(failures.join(" "));
          } else {
            this._setError("");
            this._setStatus(summary, "success");
          }
        }
      } finally {
        this.state.pushing = false;
        this._setLoading(false);
        if (pushBtn) pushBtn.textContent = previousLabel || "Push to Canvas";
        this._renderPushScoresTable();
      }
    }
  }

  window.CanvasGradeWizard = CanvasGradeWizard;
})(window);
