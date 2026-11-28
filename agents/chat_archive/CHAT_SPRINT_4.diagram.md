# CHAT_SPRINT_4 — Sprint Archive

## Summary

Sprint 4 replaced bobp chat-merge with bobp merge: conflict-safe merging for timestamped Markdown documents (CHAT.md, LESSONS.md, DECISIONS.md/ADRs), both post-conflict cleanup and optional Git custom merge driver (--git-driver %O %A %B), SEC-005..009 hardened, real git merge/rebase verified, docs/skills synced, 353 tests green.

---

## Planning

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Mouse
    participant All
    participant Cypher
    participant Smith
    participant Morpheus
    participant Switch
    participant Neo
    Note over Mouse,Neo: 📅 2026-11-01
    Mouse->>All: "handoff"
    Note right of Mouse: "Mouse state saved for<br/>Sprint 2 close, cold-<br/>start plan in<br/>agents/mouse/state.md.<br/>Waiting on owner:<br/>commit/release, and<br/>whether to run bobp u…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 3 stories<br/>SKL-1..6 drafted (docs/s<br/>prints/USER_STORIES_SPRI<br/>NT3.md): .claude/skills<br/>real dirs, no links +<br/>migration, root<br/>AGENTS.md cr…"
    Smith->>Morpheus: "user approve"
    Note right of Smith: "rubric STORIES: OUT=A<br/>TEST=A FAIL=A SCOPE=A<br/>SIZE=A DESIGN=A. Note:<br/>SIZE is the sprint, not<br/>a story, six stories,<br/>ordered plan needed.<br/>SKL-6…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Architecture complete<br/>(ADR-S3-1..7, ownership<br/>manifest, symlink-safe<br/>moves). @Smith *user<br/>feedback sprint-3 arch"
    Smith->>Switch: "user approve"
    Note right of Smith: "rubric ARCH: BOUND=A<br/>FLOW=A FAIL=A USER=A<br/>DECS=A FEAS=A. User<br/>impact flagged:<br/>Codex/Gemini lose skills<br/>(documented), clean now<br/>needs --yes.…"
    Switch->>Mouse: "sec handoff"
    Note right of Switch: "security gate (design):<br/>No blocking findings.<br/>Threats reviewed:<br/>symlinked<br/>.claude/.claude/skills,<br/>hostile legacy links,<br/>manifest/evals path…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 3 planned in<br/>task.md: 7 phases<br/>(layout+spec, no-<br/>links+migration, evals,<br/>path rewrite, size,<br/>descriptions/gotchas,<br/>agent-safe CLI) +…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "PLAN review: Weak on<br/>ALIGN/VERIF for Task 4.2<br/>(verified with --dry-<br/>run, which lands in<br/>Phase 7). Mouse<br/>corrected the task to<br/>use a scratch-…"
```

---

## Phase 0

Sprint 3 plan logged in agents/mouse/sprint_log.md; implementation not started. Phase 1 is next.

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Switch
    participant Morpheus
    Note over Neo,Morpheus: 📅 2026-11-01
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 impl done:<br/>_skill_layout<br/>(place_skills, ownership<br/>manifest, symlink-safe),<br/>real skills in<br/>.claude/skills, persona<br/>memory in agents/…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 1 PASSED on<br/>the real CLI (scratch<br/>HOME/CODEX_HOME): 35<br/>skills real dirs, 0<br/>symlinks under .claude,<br/>all pass spec name rule,<br/>manif…"
    Switch->>Neo: "sec reject"
    Note right of Switch: "security gate phase 1:<br/>Blocked SEC-006.<br/>write_stamp (Sprint 2)<br/>and write_manifest<br/>follow planted symlinks:<br/>reproduced victim file<br/>overwritt…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "SEC-006 fixed:<br/>write_text_safely()<br/>(random temp file +<br/>os.replace) now used for<br/>the version stamp and<br/>the skill manifest,<br/>planted-symlink t…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 1 re-run<br/>PASSED on real CLI: with<br/>symlinks planted at<br/>.bobp-version, .bobp-<br/>skills and ..bobp-<br/>skills.tmp, bobp update<br/>exits 0, all…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 1):<br/>No blocking findings.<br/>SEC-006 verified fixed.<br/>Rechecked: symlinked<br/>.claude/.claude/skills<br/>refused, manifest read<br/>n…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 review PASSED.<br/>ADR-S3-1/2/3 respected.<br/>Notes: STAMP/manifest<br/>share one safe writer in<br/>_common,<br/>find_persona_dirs now<br/>keys on state.…"
```

---

## Phase 2

Phase 2: no-links setup, legacy migration and link removal, root AGENTS.md

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Switch
    participant Morpheus
    participant Mouse
    Note over Neo,Mouse: 📅 2026-11-01
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 2 impl done:<br/>remove_legacy_links<br/>(readlink target inside<br/>agents/ only),<br/>migrate_legacy,<br/>ensure_root_agents_md<br/>(create-only), setup sc…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 2 PASSED on<br/>real CLI with an old-<br/>layout fixture (10<br/>links, own skill, real<br/>GEMINI.md, .cursorrules-<br/>>/etc/hosts, Codex-home<br/>link):…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 2):<br/>No blocking findings.<br/>Reviewed: link removal<br/>by literal readlink<br/>target (dotdot escape,<br/>self-loop, outside link<br/>al…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 2 review PASSED.<br/>ADR-S3-2/5 respected,<br/>ordering links->migrate-<br/>>place->AGENTS.md is<br/>correct and idempotent,<br/>no new dependency.<br/>Note:…"
    Mouse->>Neo: "sm handoff"
    Note right of Mouse: "Owner queued: the<br/>testing tool must follow<br/>agentskills.io<br/>evaluating-skills. Added<br/>STORY-SKL-4 AC7-12<br/>(iteration workspaces,<br/>with_skill + b…"
```

---

## Phase 3

Phase 3: evals in evals/evals.json (loader, 11 cases moved per skill, catalog.json removed); then Phase 3b workspace/baseline

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Switch
    participant Morpheus
    participant Bob
    participant User
    participant All
    participant Cypher
    participant Mouse
    participant Oracle
    participant Smith
    participant Tank
    Note over Neo,Tank: 📅 2026-11-01
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 3 impl done: 11<br/>cases moved to bobp/temp<br/>lates/agents/<skill>/eva<br/>ls/evals.json (standard<br/>fields + one bobp<br/>object), load_evals()<br/>with…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 3 PASSED on<br/>real CLI: 10 evals files<br/>install with their<br/>skills<br/>(skill_name==dir),<br/>--list shows the same 11<br/>names, --list --json =…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 3):<br/>No blocking findings.<br/>Loader refuses symlinked<br/>and >1MB files, rejects<br/>absolute/.. in files,<br/>artifact and rubric,…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 3 review PASSED.<br/>ADR-S3-4 respected:<br/>standard fields<br/>untouched, evaluator<br/>extras in one bobp<br/>object, loader returns<br/>the old suite sha…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 3b impl done: pers<br/>ona_eval_workspace.py<br/>(naming, iterations, tim<br/>ing/grading/benchmark/fe<br/>edback/snapshot,<br/>baseline_request),<br/>run_suite…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 3b PASSED<br/>against REAL Promptfoo<br/>reports (offline echo<br/>provider, no Codex/Jev<br/>calls): tree matches the<br/>evaluating-skills<br/>layout,…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase<br/>3b): No blocking<br/>findings. Workspace and<br/>eval folder names<br/>validated (lowercase-<br/>hyphen) before becoming<br/>path parts, al…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 3b review PASSED.<br/>ADR-S3-8 respected: Jev<br/>grading kept and feeding<br/>grading.json, results<br/>under build/ (generated<br/>data), standard file…"
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 4 impl done:<br/>_path_rewrite.py<br/>(tested, idempotent,<br/>skill-link rules, narrow<br/>allow-list scope), 30+4<br/>packaged template files<br/>migrated,…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 4 PASSED:<br/>scratch-copy rehearsal<br/>then real 'bobp update<br/>.' on this repo: 35 real<br/>skills, 0 bobp symlinks<br/>left, root AGENTS.md<br/>rea…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 4):<br/>No blocking findings.<br/>Rewrite scope is an<br/>explicit allow-list<br/>(root AGENTS.md,<br/>agents/templates,<br/>PROJECT/INDEX/HEL…"
    Morpheus->>Bob: "lead handoff"
    Note right of Morpheus: "Phase 4 review PASSED.<br/>ADR-S3-5 respected: one<br/>tested function for<br/>templates and projects.<br/>Caught by review: skill-<br/>relative links<br/>(../skill…"
    Note over Neo,Tank: 📅 2026-11-06
    User->>All: "request"
    Note right of User: "User invoked -protocol<br/>init, initializing Bob<br/>session. Working tree<br/>has extensive Sprint 3<br/>migration changes, user<br/>asked for their context."
    User->>All: "request"
    Note right of User: "User asked to resume and<br/>complete Sprint 3. Newer<br/>owner decision in sprint<br/>log: move skills to<br/>.agents/skills,<br/>reconcile plan and<br/>execute r…"
    Note over Neo,Tank: 📅 2026-11-23
    User->>All: "request"
    Note right of User: "/bob-protocol init load<br/>bob — initialize Bob<br/>Protocol session and<br/>load Bob persona."
    Bob->>All: "ready"
    Note right of Bob: "Bob Protocol<br/>initialized. Team ready.<br/>Loaded Bob (*prompt),<br/>Sprint 3 Phases 1-4 and<br/>.agents/skills migration<br/>are in the working tree,<br/>with…"
    Bob->>All: "greeting"
    Note right of Bob: "Good morning, team! What<br/>is your favorite part of<br/>your job? Why: a quick<br/>check-in starts the day<br/>together."
    Bob->>All: "greeting"
    Note right of Bob: "Turning vague intent<br/>into crisp persona<br/>prompts and rubrics that<br/>hold up under real<br/>evals—a strong prompt<br/>makes good judgment<br/>repeatable. W…"
    Cypher->>All: "greeting"
    Note right of Cypher: "Turning messy user needs<br/>into crisp, testable<br/>acceptance criteria so<br/>everyone knows what done<br/>looks like. Why: sharing<br/>my favorite part for…"
    Morpheus->>All: "greeting"
    Note right of Morpheus: "Naming the right<br/>boundaries and<br/>invariants before a line<br/>of code is written,<br/>choosing the simplest<br/>design that survives the<br/>real lifecycle.…"
    Mouse->>All: "greeting"
    Note right of Mouse: "Breaking big goals into<br/>small, dependency-<br/>ordered batches so<br/>blockers surface early<br/>and progress stays<br/>visible. Why: sharing my<br/>favorite pa…"
    Neo->>All: "greeting"
    Note right of Neo: "Reproducing a stubborn<br/>failure and landing the<br/>smallest, cleanly tested<br/>change that proves the<br/>fix. Why: sharing my<br/>favorite part for the m…"
    Oracle->>All: "greeting"
    Note right of Oracle: "Tracing decisions back<br/>to their source and<br/>placing durable<br/>knowledge right where<br/>the next person will<br/>find it. Why: sharing my<br/>favorite par…"
    Smith->>All: "greeting"
    Note right of Smith: "Running the real<br/>interface myself to spot<br/>rough edges and make<br/>recovery paths just as<br/>clear as the happy path.<br/>Why: sharing my favorite<br/>par…"
    Switch->>All: "greeting"
    Note right of Switch: "Catching trust-boundary<br/>and dependency risks<br/>early and pairing every<br/>evidence-backed finding<br/>with a fix the team can<br/>adopt cleanly. Why: sh…"
    Tank->>All: "greeting"
    Note right of Tank: "Making the safe path the<br/>easy path with<br/>declarative, repeatable<br/>automation that works<br/>the same everywhere.<br/>Why: sharing my favorite<br/>part fo…"
    Trin->>All: "greeting"
    Note right of Trin: "Testing against real<br/>behavior and artifacts<br/>so risk-based evidence<br/>decides every gate with<br/>zero guesswork. Why:<br/>sharing my favorite part<br/>fo…"
    User->>All: "request"
    Note right of User: "User requested: update<br/>Tank to use mise and<br/>Task for build<br/>instructions with make<br/>as a thin wrapper<br/>(example: t3-gcp<br/>project). Why: log use…"
    Bob->>All: "reprompt"
    Note right of Bob: "Updated Tank persona (.a<br/>gents/skills/tank/SKILL.<br/>md + packaged template)<br/>and Tank's build-env<br/>skill (+<br/>references/language-<br/>conventions.md) t…"
    User->>All: "request"
    Note right of User: "User requested: wire age<br/>nts/templates/_template_<br/>DOMAIN.md and the DOMAIN<br/>rubric into Morpheus's<br/>skill (canonical +<br/>packaged). Why: log<br/>user…"
    Bob->>All: "reprompt"
    Note right of Bob: "Wired agents/templates/_<br/>template_DOMAIN.md and<br/>DOMAIN rubric into<br/>Morpheus (.agents/skills<br/>/morpheus/SKILL.md +<br/>packaged copy), parity<br/>and s…"
    User->>All: "request"
    Note right of User: "User requested: add new<br/>artifact templates for<br/>Makefile, Taskfile.yml,<br/>and mise.toml including<br/>rubrics. Why: log user<br/>template-creation req…"
    User->>All: "request"
    Note right of User: "User requested: wire up<br/>all missing template and<br/>rubric references across<br/>persona and shared<br/>skills (plus the new<br/>Makefile/Taskfile/mise<br/>te…"
    Bob->>All: "reprompt"
    Note right of Bob: "Added<br/>_template_MAKEFILE.md,<br/>_template_TASKFILE.md,<br/>and _template_MISE.md<br/>(with rubrics) to<br/>agents/templates/ +<br/>packaged templates,<br/>registe…"
    User->>All: "request"
    Note right of User: "$oracle groom — user<br/>invoked Oracle to groom<br/>project documentation.<br/>Why: log external<br/>persona invocation."
    Bob->>Oracle: "handoff"
    Note right of Bob: "Bob state saved after<br/>adding build templates<br/>and wiring<br/>template/rubric refs<br/>across skills. Handing<br/>off for documentation<br/>groom. @Oracle *o…"
    Oracle->>All: "init"
    Note right of Oracle: "Activating Oracle (*ora)<br/>for *ora groom. Why:<br/>audit documentation<br/>index, templates, links,<br/>rubric blocks, and<br/>consistency."
    Oracle->>All: "ora groom"
    Note right of Oracle: "Grooming complete. Fixed<br/>38 broken links<br/>(DOCUMENTATION_INDEX.md<br/>+<br/>PERSONA_EVALUATION.md),<br/>synced STARTUP/SHORTHAND<br/>/WALKTHROUGH/index<br/>mirro…"
    User->>All: "request"
    Note right of User: "User requested: bump<br/>version and commit. Why:<br/>log version bump and<br/>commit authorization."
    Note over Neo,Tank: 📅 2026-11-24
    User->>All: "request"
    Note right of User: "User requested: release<br/>bobp 0.3.1 with merged<br/>Dependabot dependency<br/>updates. Why: log<br/>release authorization."
    Note over Neo,Tank: 📅 2026-11-27
    User->>All: "request"
    Note right of User: "$bob-protocol init read<br/>docs — initialize Bob<br/>Protocol session and<br/>read project docs. Why:<br/>log external session<br/>startup request."
    Bob->>All: "ready"
    Note right of Bob: "Bob Protocol<br/>initialized. Team ready.<br/>Verified 10 personas,<br/>via MCP, and read<br/>project docs, awaiting<br/>user direction. Why:<br/>complete init rap…"
    Bob->>All: "greeting"
    Note right of Bob: "Good morning, team! What<br/>is your favorite part of<br/>your job? Why: a quick<br/>check-in starts the day<br/>together."
    Bob->>All: "greeting"
    Note right of Bob: "Keeping every persona's<br/>role distinct so the<br/>workflow carries the<br/>detail and rubrics<br/>actually see what<br/>matters. Why: morning<br/>check-in."
    Cypher->>All: "greeting"
    Note right of Cypher: "Naming assumptions<br/>upfront so we can<br/>reverse them cleanly and<br/>keep every story tied to<br/>a real user outcome.<br/>Why: morning check-in."
    Morpheus->>All: "greeting"
    Note right of Morpheus: "Making architectural<br/>tradeoffs explicit early<br/>so the codebase stays<br/>simple and resilient<br/>over time. Why: morning<br/>check-in."
    Mouse->>All: "greeting"
    Note right of Mouse: "Watching small, well-<br/>ordered tasks move<br/>smoothly across the<br/>board while keeping team<br/>pace sustainable. Why:<br/>morning check-in."
    Neo->>All: "greeting"
    Note right of Neo: "Turning a failing test<br/>into green, verifiable<br/>behavior with clean,<br/>maintainable code. Why:<br/>morning check-in."
    Oracle->>All: "greeting"
    Note right of Oracle: "Spotting contradictions<br/>in the record and<br/>preserving honest<br/>provenance so nobody<br/>repeats past mistakes.<br/>Why: morning check-in."
    Smith->>All: "greeting"
    Note right of Smith: "Spotting confusing<br/>defaults and sharp edges<br/>so the interface always<br/>makes the next step<br/>obvious without blaming<br/>the user. Why: morning<br/>chec…"
    Switch->>All: "greeting"
    Note right of Switch: "Pinning trust boundaries<br/>and trimming privileges<br/>before trouble<br/>happens—least privilege<br/>beats incident response<br/>every time. Why: morning<br/>ch…"
    Tank->>All: "greeting"
    Note right of Tank: "Verifying that a clean<br/>rebuild and deploy work<br/>identically<br/>everywhere—repeatable<br/>always beats heroic.<br/>Why: morning check-in."
    Trin->>All: "greeting"
    Note right of Trin: "Writing crisp failure<br/>reports that point<br/>straight to the next<br/>step so regressions<br/>never slip past the<br/>gate. Why: morning<br/>check-in."
    User->>All: "request"
    Note right of User: "$cypher nreq enhance<br/>chat merge tool to merge<br/>#quot;time stamped<br/>documents#quot;. Why: log<br/>external persona<br/>invocation and new<br/>requirement."
    Bob->>Cypher: "handoff"
    Note right of Bob: "Bob state saved. Handing<br/>off new requirement on<br/>chat merge tool to<br/>Cypher. @Cypher *pm<br/>story enhance chat merge<br/>tool to merge time<br/>stamped…"
    Cypher->>All: "init"
    Note right of Cypher: "Activating Cypher (*pm)<br/>to capture and refine<br/>new requirement for<br/>enhancing the chat merge<br/>tool to merge time-<br/>stamped documents. Why:<br/>log p…"
    Cypher->>User: "pm story"
    Note right of Cypher: "Reviewed chat_merge.py<br/>and project artifacts.<br/>Asking user 4 scope<br/>questions (doc formats,<br/>single vs multi-file<br/>merge, CLI surface,<br/>sprint p…"
    Cypher->>All: "pm story"
    Note right of Cypher: "Drafted Sprint 4 stories<br/>in docs/sprints/USER_STO<br/>RIES_SPRINT4.md (STORY-<br/>MRG-1..4: bobp merge<br/>replacing chat-merge,<br/>multi-format<br/>timestamped…"
    Cypher->>All: "pm story"
    Note right of Cypher: "Trimmed docs/sprints/USE<br/>R_STORIES_SPRINT4.md per<br/>owner KISS directive<br/>down to 3 tight stories<br/>(STORY-MRG-1..3).<br/>STORIES rubric self-<br/>check P…"
    Note over Neo,Tank: 📅 2026-11-28
    User->>All: "request"
    Note right of User: "/sprint on till done —<br/>run full Sprint 4 (bobp<br/>merge) planning,<br/>implementation, QA,<br/>security, review, and<br/>closeout. Why: log user<br/>sprint ex…"
    Cypher->>Smith: "pm handoff"
    Note right of Cypher: "Sprint 4 stories ready<br/>for Gate 1 review in doc<br/>s/sprints/USER_STORIES_S<br/>PRINT4.md. @Smith *user<br/>review docs/sprints/USER<br/>_STORIES_SPRINT4.md.…"
    Smith->>Morpheus: "user approve"
    Note right of Smith: "*user approve. rubric<br/>STORIES: OUT=PASS<br/>TEST=PASS FAIL=PASS<br/>SCOPE=PASS SIZE=PASS<br/>DESIGN=PASS. Stories<br/>approved with 6 HCI<br/>notes for arch (A…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Sprint 4 Architecture<br/>appended to docs/sprints<br/>/USER_STORIES_SPRINT4.md<br/>(ADR-S4-1..5, single<br/>stdlib<br/>bobp/tools/merge.py, all<br/>6 Gate 1 HCI no…"
    Smith->>Morpheus: "user reject"
    Note right of Smith: "*user reject REASON:<br/>Flow A preamble-conflict<br/>check falsely rejects<br/>top-of-file desc<br/>conflicts, metadata<br/>regex misses space after<br/>**Date:**…"
    Morpheus->>Smith: "lead handoff"
    Note right of Morpheus: "Revised Sprint 4<br/>Architecture in docs/spr<br/>ints/USER_STORIES_SPRINT<br/>4.md: fixed top-of-file<br/>hunk preamble detection,<br/>fixed metadata Date<br/>regex…"
    Smith->>Switch: "user approve"
    Note right of Smith: "*user approve. rubric<br/>ARCH: BOUND=PASS<br/>FLOW=PASS FAIL=PASS<br/>USER=PASS DECS=PASS<br/>FEAS=PASS. Revised<br/>Sprint 4 arch fixes top-<br/>of-file hunk dete…"
    Switch->>Mouse: "sec handoff"
    Note right of Switch: "security gate (design):<br/>No blocking findings.<br/>Threat model complete<br/>(gitleaks + accepted-<br/>risks OK), Neo hardening<br/>items (O_NONBLOCK<br/>write,…"
    Mouse->>Morpheus: "sm handoff"
    Note right of Mouse: "Sprint 4 task board<br/>created in task.md (3<br/>phases + Closeout,<br/>Sprint 3 archived to doc<br/>s/sprints/TASK_SPRINT3.m<br/>d). PLAN self-check<br/>PASS. @Mor…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Sprint 4 plan approved.<br/>rubric PLAN: SIZE=PASS<br/>GATE=PASS VERIF=PASS<br/>ALIGN=PASS OWNER=PASS<br/>LEVEL=PASS. Phase 1<br/>ready. @Neo *swe impl<br/>phase-1…"
```

---

## Phase 1

Phase 1: Core bobp merge (multi-format timestamped Markdown parser, post-conflict cleanup, SEC-005/006/007 file/output safety). Why: phase start marker for Sprint 4.

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant All
    participant Trin
    participant Switch
    participant Morpheus
    Note over Neo,Morpheus: 📅 2026-11-28
    Neo->>All: "init"
    Note right of Neo: "Activating Neo (*swe)<br/>for Phase 1 TDD (writing<br/>failing<br/>tests/test_merge.py<br/>first). Why: follow<br/>Test-First invariant."
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 1 impl complete<br/>(bobp/tools/merge.py,<br/>cli.py, chat_report.py,<br/>setup_agent_links.py,<br/>tests/test_merge.py).<br/>Full suite green: 344<br/>passe…"
    Switch->>Neo: "sec reject"
    Note right of Switch: "security gate (phase 1):<br/>Blocked SEC-008 (Medium<br/>ReDoS in META_DATE_RE,<br/>2-char fix + ReDoS/dry-<br/>run-escape tests).<br/>Severity: Medium |<br/>Verdic…"
    Morpheus->>Neo: "lead reject"
    Note right of Morpheus: "Phase 1 review REJECT:<br/>Git-factored --- above<br/><<<<<<< HEAD in CHAT.md<br/>causes parse_blocks to<br/>swallow or miss entries,<br/>also simplify sort_en…"
    Switch->>Neo: "sec reject"
    Note right of Switch: "security gate (phase 1):<br/>Blocked SEC-009 (Medium<br/>ReDoS in parse_blocks<br/>re.split on blank-line<br/>runs, 7-char (?<!\n)<br/>fix). SEC-008 verified<br/>f…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 1 passed (45<br/>focused tests green +<br/>live CLI dry-run & exit-<br/>code checks). @Switch<br/>*sec review phase-1.<br/>Why: complete Phase 1<br/>UAT."
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 1):<br/>No blocking findings.<br/>SEC-008 & SEC-009<br/>verified fixed (linear-<br/>time regexes),<br/>SEC-005/006/007 I/O &<br/>sanitize verif…"
    Morpheus->>Neo: "lead handoff"
    Note right of Morpheus: "Phase 1 review APPROVED.<br/>rubric LOOP_IMPL:<br/>TFIRST=A VERIF=S MODUL=S<br/>REGRESS=S BUDGET=A.<br/>Ready for Phase 2. @Neo<br/>*swe impl phase-2. Why:<br/>cle…"
```

---

## Phase 2

Phase 2: Optional Git custom merge driver (--git-driver BASE OURS THEIRS) with 3-way entry/preamble merge and real-git E2E tests. Why: phase start marker for Sprint 4.

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Neo
    participant Trin
    participant Switch
    participant Morpheus
    participant Bob
    Note over Neo,Bob: 📅 2026-11-28
    Neo->>Trin: "swe handoff"
    Note right of Neo: "Phase 2 impl complete<br/>(--git-driver BASE OURS<br/>THEIRS 3-way merge +<br/>real-git E2E tests<br/>across<br/>CHAT/LESSONS/DECISIONS).<br/>Full suite green: 353…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "UAT phase 2 passed (353<br/>passed, 2 skipped, 218<br/>subtests + real git<br/>merge & git rebase UAT<br/>green). @Switch *sec<br/>review phase-2. Why:<br/>complet…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 2):<br/>No blocking findings.<br/>Zero shell exec, SEC-005<br/>on BASE/OURS/THEIRS,<br/>writes strictly to OURS<br/>with no .bak, isolated…"
    Morpheus->>Bob: "lead handoff"
    Note right of Morpheus: "Phase 2 review APPROVED.<br/>rubric LOOP_IMPL:<br/>TFIRST=S VERIF=S MODUL=S<br/>REGRESS=S BUDGET=A.<br/>Ready for Phase 3 (help<br/>& docs). @Bob *reprompt<br/>pha…"
```

---

## Phase 3

Phase 3: Help snippet verification and active skill/template/doc updates from chat-merge to bobp merge. Why: phase start marker for Sprint 4.

```mermaid
%%{init: {"sequence": {"messageFontSize": 14, "noteFontSize": 18, "actorFontSize": 14}}}%%
sequenceDiagram
    autonumber
    participant Bob
    participant Trin
    participant Switch
    participant Morpheus
    participant Tank
    participant Oracle
    participant Smith
    participant All
    participant Neo
    participant Cypher
    participant Mouse
    Note over Bob,Mouse: 📅 2026-11-28
    Bob->>Trin: "reprompt handoff"
    Note right of Bob: "Phase 3 complete: synced<br/>bob-tools,<br/>DOCUMENTATION_INDEX,<br/>SHORTHAND_GUIDE, README,<br/>and packaged mirrors for<br/>bobp merge, verified<br/>--help opt-…"
    Trin->>Switch: "qa handoff"
    Note right of Trin: "Phase 3 verification<br/>passed: 51 focused tests<br/>(merge, skill_spec,<br/>bob_manage) + 175<br/>subtests green,<br/>canonical/packaged diffs<br/>clean, zero st…"
    Switch->>Morpheus: "sec handoff"
    Note right of Switch: "security gate (phase 3):<br/>No blocking findings.<br/>Quick pass on<br/>doc/skill/help text:<br/>opt-in Git snippet uses<br/>only %O %A %B, no auto-<br/>config mut…"
    Morpheus->>Tank: "lead handoff"
    Note right of Morpheus: "Phase 3 review APPROVED.<br/>All Sprint 4 phases<br/>complete. @Tank *devops<br/>sdlc-check. Why: start<br/>Stage 3 Sprint Closeout."
    Tank->>Oracle: "devops handoff"
    Note right of Tank: "SDLC conformance check<br/>PASSED: pure stdlib (no<br/>manifest/dep drift),<br/>make test (353 passed, 2<br/>skipped, 218 subtests),<br/>make lint (Mermaid PAS…"
    Oracle->>Smith: "ora handoff"
    Note right of Oracle: "Sprint 4 docs groomed:<br/>updated<br/>DOCUMENTATION_INDEX (+<br/>packaged copy), added<br/>SEC-008/009 regex lesson<br/>to docs/LESSONS.md<br/>(dogfooded with bob…"
    Smith->>All: "user approve"
    Note right of Smith: "*user approve. rubric<br/>UAT: COVER=PASS<br/>STEPS=PASS FAIL=PASS<br/>DATA=PASS EVID=PASS.<br/>rubric LESSON: WHEN=PASS<br/>WHAT=PASS RULE=PASS<br/>CAUSE=PASS PLA…"
    Neo->>Cypher: "retro"
    Note right of Neo: "Neo retro: TDD +<br/>independent<br/>Switch/Morpheus reviews<br/>caught Git-factored ---<br/>and SEC-008/009 ReDoS<br/>before release, Phase 2<br/>driver went gree…"
    Trin->>Cypher: "retro"
    Note right of Trin: "Trin retro: 353 passed<br/>(218 subtests), real git<br/>merge & rebase verified<br/>end to end, alarm-<br/>guarded FIFO/ReDoS tests<br/>kept suite fast (<16s).…"
    Morpheus->>Cypher: "retro"
    Note right of Morpheus: "Morpheus retro: single<br/>stdlib<br/>bobp/tools/merge.py<br/>honored KISS, Smith Gate<br/>2 saved us from top-of-<br/>file desc conflict bug<br/>pre-coding. Backlo…"
    Oracle->>Cypher: "retro"
    Note right of Oracle: "Oracle retro:<br/>canonical/packaged<br/>parity held cleanly and<br/>SEC-008/009 regex lesson<br/>is now in<br/>docs/LESSONS.md.<br/>Backlog: resume Sprint 3<br/>SDLC…"
    Mouse->>Cypher: "retro"
    Note right of Mouse: "Mouse retro: 3 compact<br/>phases with clear gates<br/>flowed smoothly with<br/>zero context loss,<br/>Sprint 3 board safely<br/>preserved at<br/>docs/sprints/TASK…"
    Smith->>Cypher: "retro"
    Note right of Smith: "Smith retro: Gate 1/2<br/>HCI notes landed in code<br/>and --help is self-<br/>service. Backlog:<br/>singular/plural polish<br/>(1 entry vs N entries)<br/>and --git…"
    Switch->>Cypher: "retro"
    Note right of Switch: "Switch retro:<br/>benchmarking regexes on<br/>20k-100k inputs caught<br/>SEC-008/009 early,<br/>SEC-005/006/007 I/O<br/>controls held clean<br/>across Phases 1-3.…"
    Tank->>Cypher: "retro"
    Note right of Tank: "Tank retro: pure stdlib<br/>kept SDLC and manifests<br/>drift-free, test, lint,<br/>security-scan, and build<br/>all passed green.<br/>Backlog: distclean<br/>wrapp…"
    Bob->>Cypher: "retro"
    Note right of Bob: "Bob retro: bob-tools<br/>canonical/packaged<br/>mirrors stayed synced<br/>and passed skill_spec.<br/>Backlog: Sprint 3 Phases<br/>5-6 (size limits,<br/>references/…"
    Cypher->>Cypher: "retro"
    Note right of Cypher: "Cypher retro:<br/>1-question-at-a-time<br/>scoping + KISS directive<br/>yielded 3 sharp stories<br/>with zero mid-sprint<br/>scope creep. Backlog<br/>logged in age…"
    Cypher->>All: "pm launch"
    Note right of Cypher: "*pm launch SPRINT_4.<br/>bobp merge shipped<br/>(replaces chat-merge,<br/>multi-format<br/>CHAT/LESSONS/DECISIONS,<br/>post-conflict cleanup +<br/>opt-in Git 3-way…"
```

## Sprint close-out

- **Cypher**: \*pm launch SPRINT\_4. bobp merge shipped (replaces chat-merge, multi-format CHAT/LESSONS/DECISIONS, post-conflict cleanup + opt-in Git 3-way…
