# CLAUDE.md — Personal Reference (trimmed from BMW Lab SOP)

> [!NOTE]
> This is a **personal, trimmed copy** for Richard (徐銘亨), an undergraduate 專題 (capstone) student affiliated with BMW Lab, NTUST. The full lab SOP was pulled down for reference; this version keeps only what's relevant to working locally as an undergrad, not yet pushing to the lab's GitHub. Sections that don't apply were removed rather than kept "just in case" — if something new from the lab SOP comes up, ask before assuming it belongs here.

---

## 1. What This Is

The original repo is the **Standard Operating Procedure (SOP)** for **BMW Lab** (Broadband Multimedia Wireless Networks) at NTUST, supervised by **Prof. Ray**. It's a Markdown-only collection of rules/workflows/checklists for lab members — not a software project.

Richard is not a graduate lab member; he's an undergrad doing his own capstone project (專題), currently working **locally**, not pushing to any lab GitHub repo. He may clone/reference lab repos (e.g. the project template) later, but his own work isn't in an official lab repo yet.

---

## 2. Current Capstone Context

- **Topic:** Energy saving in heterogeneous small-cell networks — an O-RAN **ES rApp** (cell on/off switching to save power while maintaining UE throughput). Not NTN/satellite (that was an earlier, since-abandoned topic).
- Senior student **Tobby**'s prior work on this exact problem (handed over via **Winnie**) is kept locally under `Tobby實驗再現/` as **background/reference material only** — it is not Richard's own codebase, and his actual deliverable hasn't been started/uploaded yet.
- Because the topic stays within the **O-RAN / rApp / Non-RT RIC / O1 interface** architecture, the lab SOP's O-RAN-specific guidance below remains relevant even though the specific use case changed.

---

## 3. Terminology That Applies

| Term | Meaning |
|---|---|
| **BMW Lab** | Broadband Multimedia Wireless Networks Lab at NTUST |
| **Prof. Ray** | Lab supervisor |
| **rApp** | RAN application (O-RAN ecosystem) — the type of thing Richard's capstone is |
| **Non-RT RIC / SMO / O1 interface** | O-RAN architecture pieces the ES rApp domain runs on (O1-PM for metrics, O1-CM for control) |
| **MRR (Minimum Reproducible Result)** | The experimental results in a defense's final slides that an incoming student must be able to reproduce — the concept behind the `Tobby實驗再現/` handover docs |
| **Handover** | Process of transferring a project from an outgoing to incoming student (relevant as background — Tobby → Winnie) |
| **Daily Log** | Time-stamped work record — see §5, two systems apply to Richard in parallel |
| **Milestones** | Project roadmap tracking |

---

## 4. Writing and Formatting Conventions

Still worth following for anything written in SOP style (reports, handover-style notes, etc.):

- GitHub-flavored Markdown.
- Callout syntax: `> [!NOTE]`, `> [!WARNING]`, `> [!CAUTION]`, `> [!IMPORTANT]`, `> [!TIP]`.
- Numbered section headings matching a TOC (e.g. `## 1. ...`).
- File links as relative paths.
- Checklist items as `- [ ]` with **fully numeric IDs** (`5.1.1`, not `5.1.1.a`).
- Keep documents concise and purpose-driven; detailed how-to content belongs in its own dedicated file.

### 4a. Link Validity Requirement (added 2026-08-03)

> [!IMPORTANT]
> Any reference to a file that exists inside `專題` must be a real Markdown hyperlink `[text](relative/path)` — never a backtick-only code span (`` `filename.md` ``) or plain-quoted text. A backtick/code-span renders as inert monospace text, not a clickable link, both locally and on GitHub. Only leave something as plain backtick text if the target genuinely does not exist anywhere under `專題` (e.g. a file that only exists inside David's `internship` repo on the Ubuntu side, not mirrored locally).

Before treating a Daily Note, Meeting Note, or any other SOP-style document as "done" (this is now a standing step in the daily-log/meeting-note SOP, not a one-off cleanup):

- Extract every Markdown link and every backtick-quoted or quoted filename that looks like it refers to a real project file.
- Confirm each target actually resolves relative to the file's own location (Markdown links resolve relative to the file that contains them — not the repo root, not `專題` itself — same behavior locally and on GitHub).
- Convert any bare filename mention that should be clickable into a real link; leave commands, metric names, and files that don't exist under `專題` as plain backtick text.

**Known trap (discovered 2026-08-03):** a folder populated via `git clone` (e.g. `Open-Research-Playbook`, `ocloud-telemetry-agent`, or a Windows-side reference copy of David's `internship` repo) carries its own nested `.git` directory. When the parent `專題` repo is `git add`-ed, Git silently records that folder as a **submodule reference ("gitlink", mode `160000`)** instead of tracking its actual files. With no `.gitmodules` entry, GitHub shows a dead folder — the real file contents never actually get pushed. Every link pointing *into* that folder then resolves fine locally but 404s on GitHub after upload, even though the relative-path syntax was correct all along.
- **Fix:** delete the nested `.git` folder (this sacrifices that folder's own independent commit history / ability to `git pull` upstream updates for it — acceptable for read-only reference clones Richard doesn't develop in directly), then re-track it as regular files: `git rm -r --cached <path>` followed by `git add <path>`. Confirm no `160000`-mode entries remain via `git ls-files -s | grep '^160000'`.
- **When to check:** any time a new folder is added to `專題` via `git clone` (not `git init` from scratch) — don't assume links into it will work post-push without checking this first.

---

## 5. Daily Log — Multiple Systems in Play

Richard maintains **two separate logs simultaneously** (confirmed 2026-07-31):

1. **Course capstone log** (`待消化資料/01_專題規劃與日誌_學生姓名.md` + `02_單日日誌_複製區塊.md`) — G-xx/W-xx coded, tied to course grading (see `04_評分規則_建議定稿.md`), self-checked against the plan via the prompt in `03_每日日誌對正檢查_Prompt.md`. This is the graded, course-mandated record.
2. **BMW Lab Daily Log** (work-duration format, GitHub Projects card, bullet-style per the lab's own `daily-log.md`) — this is what Richard treats as **primary** for actually keeping his day-to-day record up to date.

**Richard's own framing:** lab log gets updated first/most; the course log just needs *some* record present — it doesn't need to be as immediate or detailed as the lab log. Don't block on updating the course log if only the lab log has been touched.

> [!IMPORTANT]
> A **third** template set exists — Prof. Ray's **Open Research Playbook** (`待消化資料/Open-Research-Playbook/templates/`, files A–G, see §5a below). This uses a **table format**, distinct from the lab SOP's bullet-style GitHub-card format mentioned above.
>
> **Resolved 2026-07-31** (supersedes Richard's earlier "教授只認這個模板下所紀錄的內容" statement): for advisor/teacher evaluation purposes, the course log system (`待消化資料/01...md` + `02...md`, §5 above) and the Open Research Playbook templates (A–G) are **both recognized**. Richard only needs to actively maintain **one** of the two for evaluation credit, not both in parallel. Whichever one he keeps, the *content* must be recorded in the same detail/fields the template specifies — but the *layout/formatting* is his to design (自己另創排版); it doesn't need to visually mimic the template's own markdown/table styling. This does not change the separate BMW Lab Daily Log (GitHub Projects card, bullet-style) — that remains his own primary day-to-day habit per §5, independent of which system he picks for advisor evaluation.
>
> **Decided 2026-07-31:** Richard has chosen the **Open Research Playbook template (`G-daily-note.md`, paired with `E` for self-review)** as his primary evaluation record — this is now what he checks his daily log against. The course's `01`/`02`/`03`/`04` files are kept but are no longer the primary check; treat them as secondary/backup, not the active evaluation record.

### 5a. Open Research Playbook Templates (`Open-Research-Playbook/templates/`)

| File | Purpose | When used |
|---|---|---|
| `A-research-assignment.md` | Initial assignment: title, student, advisor, scope, expected deliverables, initial milestone plan, risks, signed responsibilities | Start of a research project |
| `B-knowledge-transfer-checklist.md` | Completed by the **graduating** researcher: research package, repo, MRR list, assets, remaining work | Before a researcher leaves (background only for Richard — this is Tobby's stage, not his) |
| `C-verification-report.md` | Completed by the **incoming** researcher: confirms understanding, reproduces the MRR, proposes future work | When taking over research — **directly relevant to Richard reproducing Tobby's ES rApp results** |
| `D-acceptance-form.md` | Advisor reviews B+C and approves the graduating researcher's departure | Departure approval (not Richard's stage) |
| `E-ai-daily-self-review-prompt.md` | A prompt (for AI) to check a completed `G-daily-note.md` for missing evidence, vague deliverables, unclear blockers — must not invent facts/evidence | Run after filling in each day's Daily Note |
| `F-meeting-notes.md` | Meeting record: review pending tasks first, end with new action items that have an owner, measurable deliverable, due date, evidence | Every advisor/research meeting |
| `G-daily-note.md` | The core daily record: short-term goal/weekly milestones → today's P1/P2/P3 task plan → review (status + evidence) → pending/blocker reasons → "today's biggest lesson" → AI self-review (via E) → next working day plan | **Every working day** |

### 5b. Relevance Check Against Richard's Actual Status (confirmed 2026-07-31)

Richard is an undergrad 專題生 mid background-study/reproduction stage, not a graduate student with a formal advisor-assigned thesis, and not graduating/transferring out. Checked each template against that:

| File | Relevant to Richard? |
|---|---|
| `A-research-assignment.md` | **No — redundant.** His course's `01_專題規劃與日誌_學生姓名.md` Part A already covers the same ground (background, goals, deliverables, milestones, risks) in the form his course actually requires. |
| `B-knowledge-transfer-checklist.md` | **Not applicable.** This is filled by a *graduating* researcher (Tobby/Winnie's side); Richard is only the receiving side, not producing this document. |
| `C-verification-report.md` | **Optional reference, genuinely useful.** Even though it's nominally for a formal incoming thesis student, its structure (confirm understanding → reproduce the MRR → propose future work) matches exactly what Richard is doing with Tobby's ES rApp material — worth using informally as his own verification worksheet, not mandatory. |
| `D-acceptance-form.md` | **Not applicable at all.** Purely an advisor-side departure sign-off form; Richard is never the subject of this document. |
| `E-ai-daily-self-review-prompt.md` | **Conditional** — only in play if Richard chooses the Playbook (not the course log) as his one evaluation-recognized system (see §5 resolution above); relevant only alongside an adopted `G`. |

**Conclusion (superseded 2026-07-31 — see below):** Since both systems now count for evaluation (§5), Richard's mandatory tool is **whichever one he picks to maintain** — either the course's 01/02/03/04 files, or the Playbook's A–G. A/B/D still don't apply to his current stage regardless of which system he picks (wrong lifecycle stage).

**Decided 2026-07-31:** Richard has picked the **Playbook** as his primary/mandatory system. `G-daily-note.md` is now his main daily record, checked/reviewed via `E-ai-daily-self-review-prompt.md`. The course's `01`/`02`/`03`/`04` files are kept but demoted to secondary — they don't need to be as immediate or detailed as `G`, and updating them can lag behind `G` without being a problem. `C-verification-report.md` remains available as an optional/informal reference for the Tobby-reproduction work regardless. A/B/D remain not applicable (wrong lifecycle stage).

**How to apply:** Don't push Richard toward filling out A, B, or D — they describe a lifecycle stage he isn't in. Treat `G-daily-note.md` (+ `E`) as the record to check first and hold to the fullest standard; treat the course log files as a secondary record that just needs *some* entry present, not full detail. Don't re-raise the "which system" question — it's settled.

---

## 6. Git Commit Convention (dormant for now)

Kept as reference for when Richard's work eventually merges into an official lab repo under the lab's template — **not active** while he's working locally with no push target.

When it does become active:

- **Author:** Ray-Guang Cheng `crg@mail.ntust.edu.tw`
- **Co-author trailer:** `Co-authored-by: Ian Joseph Chandra <ianjoseph2204@gmail.com>`
- Commit message structure: short imperative title, `work duration` lines (reconstructed from actual dates, never invented), a `Summary` paragraph, numbered `Details`, ending with the co-author trailer.
- **Guard rule:** no `git push` to a lab repo without review/approval from a GitHub admin (Ian Joseph Chandra or Bimo) — this repo's SOP treats unreviewed pushes as high-risk regardless of who issues the push command.

---

## 7. Lab SOP Reference Files Still Relevant

These live in the lab's SOP repo (not copied locally) but matter because Richard's capstone is an O-RAN rApp:

- **`oran-verification.md`** — O1/E2/R1 conformance checks; relevant since the ES rApp domain uses O1-PM/O1-CM heavily.
- **`programming.md`** — source-code standards and O-RAN/3GPP-oriented design pattern guidance (Adapter/Factory/Strategy); relevant for any rApp-style Python code Richard writes.
- **`implementation.md`** — guideline for a project's own `implementation.md` (installation, end-to-end integration, ending in the O-RAN verification checks above); useful template once Richard documents his own setup.

---

## 8. External Links Still Relevant

- **Open Research Playbook** (Prof. Ray): https://github.com/raycg/Open-Research-Playbook — research lifecycle (Think/Verify/Document/Transfer); also cloned locally under `待消化資料/Open-Research-Playbook/`.
- **BMW Lab GitHub Org**: https://github.com/orgs/bmw-ece-ntust
- **Project template repo**: https://github.com/bmw-ece-ntust/template
- **Daily-Log Automation repo**: https://github.com/bmw-ece-ntust/progress-plan

---

## 9. Explicitly Out of Scope (dropped from the full lab SOP)

Not relevant to an undergrad working locally, per confirmation with Richard — removed rather than kept as dead weight:

- `leaving-procedure.md`, `licensing.md`, `NDA/*` — graduation/IP-ownership/departure-NDA process; he isn't a departing graduate lab member.
- `lab-internal/stipend.md` — no lab stipend as an undergrad.
- `logistics/teep-preparation.md` — TEEP program, not applicable.
- PostgreSQL long-term-memory system (`lab-automation/llm-memory.md`) — requires lab-granted DB/SSH-tunnel access he doesn't have while working locally/unofficially.
- `research.md`, `paper-writing.md` — full thesis/paper-writing structure; deferred until he's actually writing a capstone report, not needed at the current reproduction/background-study stage.
- `待消化資料/README.md` (confirmed 2026-07-31) — this file is actually the **BMW-Lab NTUST Internship SOP** (Probation Period → On-site Internship program: attendance, LINE/Trello reporting, Industrial Internship Policy, TEEP forms, IEEE report/testimonial/video deliverables). It sat in the lab's shared readme folder, which made it look mandatory, but Richard confirmed he is a pure local 專題生 under Prof. Ray, **not** enrolled in this Internship program (no probation, no on-site attendance, no LINE/Trello tracking). Entire file is out of scope, not just the TEEP-specific parts already excluded above. `待消化資料/readme-guide.md` (the guide for writing a project's own README.md — Prerequisites/Setup/User Guide template) is a **different, unrelated file** and remains relevant per §7 once Richard has his own repo to document.

If any of these become relevant later (e.g. he gets lab repo access, or starts writing a formal report), revisit rather than assume — ask first.
