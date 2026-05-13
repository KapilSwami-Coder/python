let qCount = 0;
let selectedCourseId = null;

function getCourses() {
    return Array.isArray(window.__PROFESSOR_COURSES__) ? window.__PROFESSOR_COURSES__ : [];
}

function showPanel(name) {
    document.querySelectorAll(".prof-panel").forEach((el) => el.classList.add("hidden"));
    const map = {
        home: "panel-home",
        exam: "panel-exam",
        result: "panel-result",
        create: "panel-create",
    };
    const id = map[name];
    if (id) document.getElementById(id).classList.remove("hidden");

    document.querySelectorAll(".nav-tab").forEach((btn) => {
        btn.classList.toggle("active", btn.dataset.panel === name);
    });
}

function courseCardHtml(c, showCreateBtn) {
    const safe = (s) =>
        String(s)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/"/g, "&quot;");
    const btn = showCreateBtn
        ? `<button type="button" class="btn-primary btn-create-exam" data-course-id="${c.id}">Create exam</button>`
        : "";
    return `
        <article class="course-card">
            <h3>${safe(c.course)}</h3>
            <p><strong>Batch year:</strong> ${safe(c.batch_year)}</p>
            <p><strong>Batch no:</strong> ${safe(c.batch_no)}</p>
            ${btn}
        </article>`;
}

function renderCourseGrids() {
    const courses = getCourses();
    const homeEl = document.getElementById("course-list-home");
    const examEl = document.getElementById("course-list-exam");
    if (!homeEl || !examEl) return;

    if (courses.length === 0) {
        const empty =
            '<p class="prof-empty">No subjects yet. Ask an admin to add rows in the <code>professor</code> table (<code>said</code>, <code>user_id</code>, course, batch_year, batch_no).</p>';
        homeEl.innerHTML = empty;
        examEl.innerHTML = empty;
        return;
    }

    homeEl.innerHTML = courses.map((c) => courseCardHtml(c, false)).join("");
    examEl.innerHTML = courses.map((c) => courseCardHtml(c, true)).join("");

    examEl.querySelectorAll(".btn-create-exam").forEach((btn) => {
        btn.addEventListener("click", () => openCreateExam(Number(btn.dataset.courseId)));
    });
}

function openCreateExam(courseId) {
    const c = getCourses().find((x) => Number(x.id) === Number(courseId));
    if (!c) return;
    selectedCourseId = courseId;
    qCount = 0;
    const qc = document.getElementById("question-container");
    if (qc) qc.innerHTML = "";

    const meta = document.getElementById("create-course-meta");
    if (meta) {
        meta.innerHTML = `
            <p><strong>Course:</strong> ${escapeHtml(c.course)}</p>
            <p><strong>Batch year:</strong> ${escapeHtml(c.batch_year)} &nbsp;|&nbsp; <strong>Batch no:</strong> ${escapeHtml(c.batch_no)}</p>
            <p class="prof-note">Year and batch are taken from the database for this course — you cannot edit them here.</p>`;
    }
    const title = document.getElementById("exam_title");
    const instr = document.getElementById("exam_instructions");
    if (title) title.value = "";
    if (instr) instr.value = "";

    showPanel("create");
    document.querySelectorAll(".nav-tab").forEach((b) => b.classList.remove("active"));
}

function escapeHtml(s) {
    return String(s)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function initProfessorNav() {
    document.querySelectorAll(".nav-tab").forEach((btn) => {
        btn.addEventListener("click", () => {
            const panel = btn.dataset.panel;
            if (panel === "home" || panel === "exam" || panel === "result") {
                showPanel(panel);
            }
        });
    });
    const back = document.getElementById("btn-back-create");
    if (back) {
        back.addEventListener("click", () => {
            selectedCourseId = null;
            showPanel("exam");
        });
    }
}

function getQuestionContainer() {
    const el = document.getElementById("question-container");
    if (!el) {
        console.error("question-container missing — open Exam → Create exam first.");
    }
    return el;
}

function addMcqField() {
    qCount++;

    const container = getQuestionContainer();
    if (!container) {
        alert("Question area not found. Use Exam → Create exam for a course first.");
        return;
    }
    const html = `
        <div class="q-block">
            <p>Question ${qCount} (MCQ)</p>

            <input type="hidden" value="mcq">

            <input type="text" class="q-text" placeholder="Enter question" required><br>

            <input type="text" class="optA" placeholder="Option A" required>
            <input type="text" class="optB" placeholder="Option B" required>
            <input type="text" class="optC" placeholder="Option C" required>
            <input type="text" class="optD" placeholder="Option D" required>

            <select class="correct">
                <option value="A">A is correct</option>
                <option value="B">B is correct</option>
                <option value="C">C is correct</option>
                <option value="D">D is correct</option>
            </select>

            <input type="number" class="mark" placeholder="Marks" required>

            <button type="button" class="btn-secondary" onclick="this.parentElement.remove()">Remove</button>
        </div>`;

    container.insertAdjacentHTML("beforeend", html);
}

function addWrittenField() {
    qCount++;

    const container = getQuestionContainer();
    if (!container) {
        alert("Question area not found. Use Exam → Create exam for a course first.");
        return;
    }
    const html = `
        <div class="q-block">
            <p>Question ${qCount} (written)</p>

            <input type="hidden" value="written">

            <input type="text" class="q-text" placeholder="Enter question" required><br>
            <textarea class="correct" placeholder="Model answer / rubric"></textarea>

            <input type="number" class="mark" placeholder="Marks" required>

            <button type="button" class="btn-secondary" onclick="this.parentElement.remove()">Remove</button>
        </div>`;

    container.insertAdjacentHTML("beforeend", html);
}

function submitCompleteQuiz() {
    const uploadBtn = document.getElementById("btn-finish-upload");

    try {
        const blocks = document.querySelectorAll("#panel-create .q-block");

        if (!selectedCourseId) {
            alert("Pehle Exam tab kholo, course chuno, phir Create exam.");
            return;
        }

        if (blocks.length === 0) {
            alert("Kam se kam ek question add karo (MCQ / written).");
            return;
        }

        const titleEl = document.getElementById("exam_title");
        const instrEl = document.getElementById("exam_instructions");
        if (!titleEl) {
            alert("Exam title field missing — page reload karke try karo.");
            return;
        }

        const title = titleEl.value.trim();
        const instructions = instrEl ? instrEl.value.trim() : "";

        if (!title) {
            alert("Exam title likho.");
            return;
        }

        const allQuestions = [];
        blocks.forEach((block, index) => {
            const hidden = block.querySelector('input[type="hidden"]');
            if (!hidden) throw new Error("Invalid question block");
            const qType = hidden.value;

            const qText = block.querySelector(".q-text");
            const correctEl = block.querySelector(".correct");
            const markEl = block.querySelector(".mark");
            if (!qText || !correctEl || !markEl) throw new Error("Incomplete question fields");

            const qData = {
                type: qType,
                text: qText.value,
                correct: correctEl.value,
                mark: parseInt(markEl.value || "1", 10) || 1,
                question_no: index + 1,
            };

            if (qType === "mcq") {
                const a = block.querySelector(".optA");
                const b = block.querySelector(".optB");
                const c = block.querySelector(".optC");
                const d = block.querySelector(".optD");
                if (!a || !b || !c || !d) throw new Error("MCQ options incomplete");
                qData.optionA = a.value;
                qData.optionB = b.value;
                qData.optionC = c.value;
                qData.optionD = d.value;
            }

            allQuestions.push(qData);
        });

        const finalData = {
            teaching_id: Number(selectedCourseId),
            title,
            instructions,
            questions: allQuestions,
        };

        if (uploadBtn) {
            uploadBtn.disabled = true;
            uploadBtn.dataset.oldText = uploadBtn.textContent;
            uploadBtn.textContent = "Uploading…";
        }

        fetch("/upload_exam", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            credentials: "same-origin",
            body: JSON.stringify(finalData),
        })
            .then(async (res) => {
                const text = await res.text();
                let data;
                try {
                    data = JSON.parse(text);
                } catch {
                    const snippet = (text || "").replace(/\s+/g, " ").slice(0, 240);
                    throw new Error(
                        snippet || res.statusText || "Server ne JSON nahi bheja — console dekho."
                    );
                }
                if (!res.ok) {
                    throw new Error(data.message || data.error || res.statusText);
                }
                return data;
            })
            .then((data) => {
                alert(data.message || "Quiz save ho gaya.");
                selectedCourseId = null;
                location.reload();
            })
            .catch((err) => {
                console.error("upload_exam", err);
                alert(err.message || "Upload fail — browser console (F12) me error dekho.");
            })
            .finally(() => {
                if (uploadBtn) {
                    uploadBtn.disabled = false;
                    if (uploadBtn.dataset.oldText) uploadBtn.textContent = uploadBtn.dataset.oldText;
                }
            });
    } catch (e) {
        console.error(e);
        alert(e.message || "JavaScript error");
        if (uploadBtn) {
            uploadBtn.disabled = false;
            if (uploadBtn.dataset.oldText) uploadBtn.textContent = uploadBtn.dataset.oldText;
        }
    }
}

document.addEventListener("DOMContentLoaded", () => {
    if (!document.body.classList.contains("professor-page")) return;
    initProfessorNav();
    renderCourseGrids();
    showPanel("home");
});
