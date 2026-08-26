---
title: Claude Code Runtime Adapter Setup
document_id: AGENT-RUNTIME-CLAUDE-README-001
version: 1.1
status: approved-template
language: en-US
last_updated: 2026-08-10
runtime: Claude Code
scope:
  - Claude Code adapter installation
  - CLAUDE.md materialization
  - existing instruction reconciliation
  - settings, memory, hooks, subagent, and agent-team verification
  - optional runtime tooling recommendations
authority_note: This README is operator guidance for installing the Claude Code runtime adapter. It is not canonical repository authority and does not replace the delivery contract under .agents/.
---

# Claude Code Runtime Adapter

This directory contains the Claude Code-specific bootstrap for the runtime-neutral `.agents/` software-delivery framework.

The adapter connects Claude Code's native project instruction system to the canonical repository-local delivery contract.

The canonical framework remains under:

```text
.agents/
├── AGENTS.md
├── software-workflow.md
├── context/
├── prompts/
└── tasks/
```

The Claude adapter does not redefine that framework.

## Files

```text
runtime-adapters/claude/
├── README.md
└── CLAUDE.md
```

### `CLAUDE.md`

The adapter source is stored at:

```text
.agents/runtime-adapters/claude/CLAUDE.md
```

It is intended to be materialized as:

```text
./CLAUDE.md
```

at the target repository root.

It provides:

- Claude Code bootstrap routing into `.agents/AGENTS.md`;
- Planner / Reviewer / Executor role boundaries;
- instruction-layer and memory boundaries;
- Claude skill, plugin, MCP, and Superpowers methodology boundaries;
- subagent and agent-team delegation boundaries;
- hooks and runtime-permission boundaries;
- evidence and terminal-state rules.

It intentionally does not duplicate the full canonical delivery protocol.

### `README.md`

This file is for the human or automation installing the adapter.

It explains how to materialize the Claude bootstrap safely without destroying existing Claude Code instructions or mistaking runtime configuration, memory, permissions, subagent coordination, or plugin behavior for repository delivery authority.

---

# Installation model

The template repository permanently stores the adapter under:

```text
.agents/runtime-adapters/claude/
```

A target repository using Claude Code SHOULD retain that adapter source and materialize the runtime bootstrap to the repository root.

Typical resulting repository:

```text
target-repository/
├── CLAUDE.md
│
└── .agents/
    ├── AGENTS.md
    ├── software-workflow.md
    ├── context/
    │   └── project.md
    ├── prompts/
    │   └── plan-create-task.md
    ├── tasks/
    │   └── _template.md
    └── runtime-adapters/
        └── claude/
            ├── README.md
            └── CLAUDE.md
```

The copy under `.agents/runtime-adapters/claude/` is the adapter source/reference.

The root `./CLAUDE.md` is the Claude-native materialized bootstrap.

Keeping both makes materialization auditable and lets future runtime-adapter updates be reconciled explicitly.

---

# Source import versus materialized import

Claude Code resolves relative `@` imports relative to the `CLAUDE.md` file containing the import.

The retained adapter source therefore uses:

```text
@../../AGENTS.md
```

because from:

```text
.agents/runtime-adapters/claude/CLAUDE.md
```

that resolves to:

```text
.agents/AGENTS.md
```

When materialized at repository root as:

```text
./CLAUDE.md
```

the import MUST be rewritten to:

```text
@.agents/AGENTS.md
```

Do not copy the source adapter byte-for-byte to repository root without adjusting this import.

Do not change the canonical `.agents/AGENTS.md` location merely to avoid rewriting the materialized import.

---

# Claude Code instruction model

Claude Code may load project and non-project instruction sources including:

```text
managed CLAUDE.md / managed claudeMd policy
~/.claude/CLAUDE.md
~/.claude/rules/
./CLAUDE.md
./.claude/CLAUDE.md
./CLAUDE.local.md
nested CLAUDE.md / CLAUDE.local.md
.claude/rules/
path-scoped rules
instructions from directories added with `--add-dir` when explicitly enabled
```

User configuration may live below a different base directory when `CLAUDE_CONFIG_DIR` is configured.

By default, `--add-dir` does not load `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, or `CLAUDE.local.md` from the added directory. Those instruction sources become eligible only when `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1` is enabled.

When that environment variable is active, treat instruction-bearing added directories as additional runtime instruction sources. They MUST NOT silently become authority for the primary repository merely because Claude can read them.

Claude Code treats CLAUDE.md files as behavioral context, not as a hard technical enforcement mechanism.

Repository installation MUST therefore verify both:

```text
instruction context
AND
enforced runtime configuration
```

where enforced runtime configuration may include permissions, sandbox settings, hooks, managed policy, and other client controls.

## Project instruction loading

Claude Code loads project instructions by walking the relevant directory hierarchy.

Project instructions closer to the active working directory are added later in the instruction context.

`CLAUDE.local.md` is local/personal project context and is loaded alongside project instructions.

Nested instructions may load lazily when Claude reads files in their directories.

Project rules under `.claude/rules/` may load unconditionally or only when matching paths are used.

Conflicting instructions are not a safe override mechanism: Claude may resolve conflicting prose inconsistently.

A material conflict MUST therefore be reconciled rather than intentionally depending on instruction ordering.

## Canonical repository boundary

Regardless of which Claude instruction source is active, repository delivery behavior MUST remain compatible with the canonical `.agents/` framework.

Runtime instructions MUST NOT silently:

- redefine approved business or product intent;
- change approved requirements;
- weaken approved architecture or repository policy;
- bypass a required delivery gate;
- authorize implementation without a validated task;
- broaden a governing task;
- replace the exact governing task revision;
- self-approve implementation acceptance;
- convert acceptance into release authorization;
- weaken security, privacy, safety, compliance, permission, or side-effect boundaries.

A direct explicit user or designated-authority instruction MAY legitimately change repository authority when applicable.

If authority remains materially ambiguous, stop and reconcile it through the canonical delivery process.

---

# Installation procedure

## 1. Install the canonical `.agents/` framework

Ensure the target repository contains the canonical framework required by this adapter.

At minimum:

```text
.agents/
├── AGENTS.md
├── software-workflow.md
├── context/
│   └── project.md
├── prompts/
│   └── plan-create-task.md
└── tasks/
    └── _template.md
```

Repository-specific authority, planning artifacts, tasks, and scoped context MAY extend this structure.

Do not replace valid repository-specific artifacts merely to make an existing repository resemble this template.

## 2. Inspect existing Claude Code instructions

Before creating or replacing a root `CLAUDE.md`, inspect, when applicable:

```text
./CLAUDE.md
./.claude/CLAUDE.md
./CLAUDE.local.md
./.claude/rules/
~/.claude/CLAUDE.md
~/.claude/rules/
managed organization instructions
nested CLAUDE.md / CLAUDE.local.md
```

Also inspect project settings and invocation environment that can change instruction loading, including:

- `claudeMdExcludes`;
- invocation-time setting-source selection;
- `--add-dir` directories;
- `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD`;
- `CLAUDE_CONFIG_DIR`.

When added-directory instruction loading is enabled, inspect the relevant `CLAUDE.md`, `.claude/CLAUDE.md`, `.claude/rules/`, and `CLAUDE.local.md` sources in those directories for material conflicts.

Do not assume that an empty repository root means Claude has no instructions.

## 3. Inspect relevant Claude runtime configuration

Inspect, when they exist or materially affect the repository:

```text
.claude/settings.json
.claude/settings.local.json
~/.claude/settings.json
managed settings
.mcp.json
.claude/agents/
.claude/skills/
plugin configuration
hooks
```

Use the effective `CLAUDE_CONFIG_DIR` instead of `~/.claude` when Claude is configured to use another user configuration directory.

Identify:

- permission allow/deny rules;
- remembered local permission approvals;
- sandbox settings;
- hooks capable of mutating repository or external state;
- project-enabled plugins;
- MCP servers;
- project and local subagent definitions;
- settings that select a main-session custom agent;
- experimental agent-team enablement when applicable;
- instruction exclusions;
- auto-memory configuration.

Runtime configuration may materially affect delivery even when the root `CLAUDE.md` is correct.

## Working-directory-sensitive configuration

Do not assume Claude Code resolves all project configuration with the same ancestor walk used for `CLAUDE.md`.

Current Claude Code behavior distinguishes several cases:

- project `CLAUDE.md` and `CLAUDE.local.md` instructions are discovered through the applicable directory hierarchy;
- hooks and most other project `.claude/settings.json` behavior are discovered from the session's current/original working-directory project configuration rather than inherited automatically from every ancestor directory;
- `.claude/settings.local.json` permission state is resolved at the Git repository root for normal interactive CLI sessions;
- configuration from `--add-dir` is only partially loaded, with instruction files requiring explicit opt-in.

For predictable repository behavior, perform installation verification from the repository root **and** from any subdirectory that developers commonly use as their Claude Code launch directory.

If effective settings, hooks, or instructions differ materially by launch directory, record and reconcile that behavior rather than assuming the root verification applies everywhere.

## 4. Classify the project instruction state

Use one or more of these cases:

```text
A. no project CLAUDE.md bootstrap exists
B. root ./CLAUDE.md already exists
C. ./.claude/CLAUDE.md already exists
D. both project CLAUDE.md locations are populated
E. CLAUDE.local.md or project rules materially conflict
F. managed/user instructions materially conflict
G. project settings exclude or suppress required project instructions
H. an explicitly added directory contributes conflicting instructions
I. common launch directories produce materially different active settings or hooks
```

Several cases may apply simultaneously.

## 5. Materialize safely

### Case A — no project CLAUDE.md bootstrap exists

Materialize:

```text
.agents/runtime-adapters/claude/CLAUDE.md
```

as:

```text
./CLAUDE.md
```

and rewrite:

```text
@../../AGENTS.md
```

to:

```text
@.agents/AGENTS.md
```

Preserve the rest of the adapter semantics.

### Case B — root `./CLAUDE.md` already exists

Do NOT overwrite it blindly.

Review the existing file and merge the adapter bootstrap and Claude-specific boundaries into it.

Preserve legitimate repository instructions such as:

- build and test commands;
- repository conventions;
- architectural navigation hints;
- scoped development expectations;
- team-shared Claude workflows that do not redefine canonical delivery authority.

Ensure the resulting root file imports:

```text
@.agents/AGENTS.md
```

exactly once unless a different repository-approved import structure intentionally provides the same canonical contract.

Avoid copying the full `.agents/AGENTS.md` contents into `CLAUDE.md`.

### Case C — `./.claude/CLAUDE.md` already exists

Do not silently ignore it.

Preferred resolutions are:

1. preserve compatible `.claude/CLAUDE.md` content and materialize the canonical bootstrap at root;
2. move or merge repository-wide Claude-specific content into the root `CLAUDE.md` when that reduces ambiguity without losing legitimate instructions; or
3. retain both when responsibilities are intentionally distinct and `/context` verifies that the effective instruction set is correct.

Do not depend on contradictory instructions in the two project locations.

### Case D — both project CLAUDE.md locations are populated

Treat both files as active repository instruction sources until runtime verification proves otherwise.

Review them together.

Ensure:

- the canonical `.agents/AGENTS.md` contract is imported once in a deliberate bootstrap;
- duplicate runtime instructions do not create contradictory semantics;
- repository-specific Claude guidance remains compatible with canonical delivery boundaries.

Use `/context` to verify the actual loaded project memory files rather than assuming which file Claude selected.

### Case E — `CLAUDE.local.md` or project rules conflict

Do not overwrite personal local instructions automatically.

Do not rely on the root adapter to cancel contradictory prose.

Identify the conflict and reconcile it explicitly.

For path-scoped `.claude/rules/`, verify representative affected paths because those rules may load only when Claude works with matching files.

A local preference MUST NOT silently become approved business, product, requirement, architecture, acceptance, release, or side-effect authority.

### Case F — managed or user instructions conflict

Managed and user instructions may apply outside the repository.

Do not silently mutate organization or user configuration as part of repository installation.

Identify:

- the conflicting instruction;
- its scope and ownership;
- the affected repository decision;
- whether it represents legitimate applicable human/organization authority or a generic runtime preference.

Managed policy may legitimately impose stronger security or compliance constraints.

Repository instructions MUST NOT attempt to weaken such applicable higher-level restrictions.

Generic personal preferences MUST NOT silently redefine repository delivery authority.

### Case G — required project instructions are excluded

Claude Code supports excluding specific project instruction files through configuration such as `claudeMdExcludes`.

Invocation settings may also omit project setting sources.

If the materialized adapter or its imported canonical contract is excluded from the effective session context, installation is not complete.

Resolve the exclusion intentionally or document an approved alternate bootstrap.

Do not claim Claude is using the canonical framework merely because the files exist on disk.

### Case H — an added directory contributes instructions

When Claude is launched with `--add-dir` and `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1`, the added directory can contribute Claude instruction files.

Do not treat those instructions as repository authority merely because the runtime loads them.

Inspect them for the same material conflicts as user, managed, local, nested, and project rules.

If the added directory belongs to another repository, preserve repository-local authority and baseline boundaries. Cross-repository authority requires explicit approved coordination rather than implicit instruction sharing.

### Case I — launch-directory-sensitive settings or hooks

If developers commonly start Claude Code below the repository root, verify the effective runtime configuration from those launch directories.

A root-level `CLAUDE.md` may still load while project hooks or other `.claude/settings.json` behavior differs because those configuration surfaces do not necessarily inherit using the same ancestor walk.

Do not declare installation complete until the expected launch patterns have compatible:

- instruction context;
- permission behavior;
- hooks;
- enabled plugins and marketplaces where relevant;
- MCP/runtime configuration needed by delivery.

If the repository requires Claude to be launched from a specific directory for correct runtime policy, state that requirement explicitly in repository guidance.

---

# Verify instruction loading

After materialization or reconciliation, start a fresh Claude Code session from the repository.

Use:

```text
/context
```

and confirm that the expected project instruction file appears under Memory files.

Use:

```text
/memory
```

to inspect loaded CLAUDE.md, CLAUDE.local.md, project rules, and auto memory.

At minimum, confirm that:

1. the intended root `CLAUDE.md` is loaded;
2. its `@.agents/AGENTS.md` import resolves successfully;
3. the canonical contract is present in effective context;
4. no required project instruction is excluded;
5. conflicting nested/local/rule instructions are absent or explicitly reconciled;
6. Planner / Reviewer routing reaches `.agents/prompts/plan-create-task.md`;
7. Executor work requires an exact published validated task revision.

When the repository contains path-scoped rules or nested CLAUDE.md files, verify from representative affected files/directories.

When developers commonly launch Claude from subdirectories, repeat `/context`, `/memory`, and `/status` from representative launch directories and inspect material hooks/permissions there as well.

When `--add-dir` is used with additional-directory instruction loading enabled, verify the added instruction sources explicitly and confirm that they do not silently cross repository authority boundaries.

Project-root `CLAUDE.md` is re-read after compaction, while nested instructions may reload only when Claude accesses their scope again.

Do not diagnose post-compaction behavior without considering that distinction.

---

# Keep the root adapter concise

Claude Code recommends concise project instructions; overly large CLAUDE.md files consume context and can reduce adherence.

The root adapter is a runtime bootstrap, not the location for:

- full PRDs;
- requirement registries;
- architecture specifications;
- complete executable tasks;
- copies of `software-workflow.md`;
- copies of `plan-create-task.md`;
- entire external engineering methodologies;
- long runtime tutorials.

Use imports, repository-native authority, path-scoped rules, skills, tasks, and progressive loading according to their intended roles.

Splitting content into `@` imports can improve organization, but imported content still consumes launch context.

Do not duplicate canonical `.agents/` content merely to make Claude-specific instructions appear self-contained.

---

# Auto memory

Claude Code auto memory is separate from repository authority.

Auto memory is machine-local repository context and is shared across worktrees of the same Git repository by default.

It may contain useful learned facts such as:

- build commands;
- debugging observations;
- recurring implementation patterns;
- developer preferences.

It MUST NOT silently establish or modify:

- approved requirements;
- architecture authority;
- task scope;
- accepted baseline;
- acceptance criteria;
- designated approval;
- release state.

Material claims from auto memory must be reverified against repository authority or observed evidence.

Operators MAY disable or relocate auto memory according to local security or privacy needs.

Do not store secrets, credentials, regulated data, or unauthorized external information in auto memory.

When auto memory materially affects delivery, inspect it through `/memory`.

---

# Subagent memory

Claude subagents may use persistent memory scopes.

Project-scoped subagent memory can create repository content under:

```text
.claude/agent-memory/
```

and may be shared through version control.

That is a repository mutation.

During Executor work, project-scoped memory writes require compatibility with:

```text
governing task scope
AND
repository side-effect authorization
```

Outside task-governed execution, project memory persistence requires an applicable repository or direct user authorization basis.

If persistent learning is useful but repository mutation is not authorized, prefer a non-repository memory scope or keep the result ephemeral.

Subagent memory remains supporting context until material claims are verified.

---

# Subagents

Claude Code supports built-in and custom subagents.

Subagents are runtime delegation mechanisms, not independent delivery authorities.

## Explore and Plan exceptions

Claude's built-in `Explore` and `Plan` agents intentionally skip project `CLAUDE.md` files and parent-session Git-status context.

When delegating a material question to either agent:

- pass the specific canonical boundaries it needs in the delegation prompt;
- do not assume `.agents/AGENTS.md` was inherited;
- keep the delegation read-only/discovery-oriented;
- treat results as supporting evidence.

The main Planner/Reviewer session remains responsible for:

- authority decisions;
- gate state;
- task publication;
- remediation routing;
- baseline acceptance.

## Custom subagents

Custom subagents may inherit normal project context and can define their own tools, hooks, skills, MCP servers, memory, and model settings.

Those capabilities do not create new delivery authority.

Review project subagent definitions under:

```text
.claude/agents/
```

when they can materially affect delivery.

A custom subagent with broad tools or permissive hooks remains bounded by the canonical task and side-effect model.

---

# Agent teams

Claude Code agent teams are an optional/experimental multi-session execution mechanism.

They introduce runtime coordination concepts such as:

- team lead;
- teammates;
- shared task list;
- runtime task dependencies;
- teammate plan approval.

These concepts MUST NOT be confused with canonical delivery state.

Specifically:

```text
Claude team task
≠ .agents executable task

teammate plan approval
≠ T5 Task Readiness

team lead approval
≠ designated repository authority

team task complete
≠ implementation accepted

team permissions
≠ repository side-effect authorization

team completion
≠ release approval
```

Teammates load normal project context, but each has an independent context window.

When teammates perform task-governed implementation, keep all work within the same governing task revision and implementation baseline unless canonical planning has explicitly created separate validated tasks.

Parallel work must respect dependencies and overlapping write surfaces.

Do not use a runtime team task list as a replacement for `.agents/tasks/`.

---

# Settings and permissions

Claude Code settings can come from user, project, local, command-line, and managed-policy layers.

Relevant repository files include:

```text
.claude/settings.json
.claude/settings.local.json
```

Local settings may contain remembered permission approvals and are normally machine-local.

Project settings may be committed and shared.

Managed settings may enforce organization-wide restrictions.

Use:

```text
/status
```

to verify which setting sources are active.

Do not infer effective runtime behavior from one JSON file in isolation.

## Permission boundary

Permissions determine what Claude is technically allowed to invoke.

They do not independently authorize repository delivery side effects.

Apply:

```text
runtime permission
AND
repository delivery authorization
```

to each material action.

This includes:

- Git commits;
- pushes;
- pull-request creation;
- dependency installation or replacement;
- external-system mutation;
- destructive data or infrastructure operations;
- production changes;
- deployment;
- publication;
- release;
- secret access or persistence.

A remembered `"allow"` in local settings does not mean the current validated task authorizes the operation.

Likewise, a task may authorize an action that the runtime still blocks; both boundaries must permit it.

Project `permissions.allow` rules and `permissions.additionalDirectories` are subject to Claude Code's workspace-trust gate. An untrusted workspace may therefore ignore capability-granting project configuration even though the JSON file is present.

Treat workspace trust as runtime capability state, not repository authority. Verify the effective trusted/untrusted behavior when it materially affects execution or access boundaries.

---

# Hooks

Claude Code hooks can be defined by:

- user settings;
- project settings;
- local settings;
- managed policy;
- plugins;
- skills;
- subagents;
- session configuration.

Hooks can run commands or other decision logic at lifecycle events.

Some hooks can mutate repository or external state automatically.

Audit active hooks that materially affect the repository.

A hook that performs material mutation MUST have an authorization basis compatible with the canonical `.agents/` contract.

Automatic execution is not implicit authorization.

Examples requiring explicit scrutiny include hooks that:

- run formatters that rewrite files;
- modify generated artifacts;
- execute Git operations;
- install dependencies;
- mutate infrastructure or external systems;
- send repository content to external endpoints;
- change settings or permissions.

`PreToolUse` hooks MAY strengthen safety by denying or escalating an operation.

Permissive hooks, prompt hooks, agent hooks, or inherited plugin hooks MUST NOT weaken repository authorization.

Use Claude's hooks inspection/debugging surfaces when hook origin is unclear.

---

# Plugins, skills, MCP, and commands

Claude Code plugins and project extensions may provide:

- skills;
- slash commands;
- hooks;
- MCP servers;
- subagents;
- other runtime integrations.

They are runtime capabilities.

They do not automatically become repository authority.

Use them within:

```text
applicable direct human / approved repository authority
→ .agents/software-workflow.md
→ .agents/AGENTS.md
→ exact governing validated task when executing
→ approval and side-effect boundaries
```

Project-enabled external plugins still require user installation/trust according to current Claude Code behavior.

Plugin trust does not imply delivery authorization.

MCP servers capable of external mutation remain subject to the same task and approval boundaries as direct tool use.

---

# Superpowers

Superpowers is a recommended optional engineering methodology for Claude Code.

It is not a dependency of the canonical `.agents/` framework.

When desired, install or update Superpowers through the current official Claude Code plugin marketplace or the current upstream Superpowers guidance.

Do not vendor or manually duplicate Superpowers skills into this repository merely to make the adapter work.

Do not hard-code marketplace installation commands into this template when upstream distribution may evolve independently.

Use the upstream source of truth:

```text
https://github.com/obra/superpowers
```

After installation:

```text
Superpowers
→ engineering methodology

Claude skills / plugins / subagents / agent teams
→ runtime capability

.agents/
→ repository delivery governance
```

Superpowers-generated specifications, plans, design documents, or similar methodology artifacts do not automatically become approved repository authority.

During Executor work, methodology artifacts remain ephemeral unless repository authority or the governing task explicitly permits persistence.

Artifact persistence and Git commit are separate authorization questions.

If a Superpowers workflow conflicts with applicable direct user instructions, approved repository authority, the governing task, approval boundaries, or stop conditions, preserve repository authority and surface the methodology conflict.

---

# Repository intelligence

Graphify, Codebase Memory MCP, and comparable repository-intelligence systems MAY be configured independently of this adapter.

The adapter does not install them automatically.

When available, their use is governed by:

```text
.agents/AGENTS.md
```

and, for Planner/Reviewer work:

```text
.agents/prompts/plan-create-task.md
```

A validated task MAY declare an intelligence capability as required when execution genuinely depends on it.

Derived indexes, graphs, summaries, memory, and retrieval output remain supporting intelligence rather than authority.

---

# Security recommendations

Runtime security configuration is environment-specific.

For repositories containing sensitive source, credentials, regulated data, production integrations, destructive operations, or external mutation capability, operators SHOULD review:

- managed policy;
- project and local permissions;
- sandbox configuration;
- filesystem/network restrictions;
- MCP server trust;
- plugin trust;
- active hooks;
- auto-memory location;
- subagent definitions;
- agent-team permissions.

Do not encode one universal Claude Code security profile into this template.

Repository or organization policy MAY require stricter runtime settings.

Runtime security controls MAY strengthen repository safety requirements but MUST NOT silently weaken them.

---

# Updating the adapter

Claude Code evolves independently of the canonical `.agents/` protocol.

When updating this adapter:

1. verify current `CLAUDE.md` loading and import semantics from official Anthropic documentation;
2. verify current project/user/local/rules behavior;
3. review changes to auto memory and subagent memory;
4. review changes to subagents and agent teams;
5. review permissions, workspace trust, settings hierarchy, launch-directory behavior, hooks, sandboxing, plugins, and MCP behavior when relevant;
6. review `--add-dir` and additional-directory instruction-loading behavior when relevant;
7. verify optional Superpowers integration from its current upstream source;
8. preserve compatibility with the frozen canonical `.agents/` artifacts;
9. change only runtime-specific behavior.

After updating:

1. update `.agents/runtime-adapters/claude/CLAUDE.md`;
2. reconcile the materialized root `./CLAUDE.md` intentionally;
3. preserve or reapply the root-specific `@.agents/AGENTS.md` import;
4. start a fresh Claude session;
5. verify effective instructions with `/context` and `/memory`;
6. verify active configuration with `/status`;
7. inspect material hooks and permissions where applicable.

An adapter update does not automatically require a canonical protocol version change.

A canonical protocol update does not automatically require an adapter update unless runtime bootstrap or boundary semantics are affected.

---

# Removing or switching runtimes

Removing the Claude adapter SHOULD NOT require removing the canonical `.agents/` framework.

To stop using this adapter:

1. remove or reconcile the materialized root `CLAUDE.md` according to repository policy;
2. remove Claude-specific optional project configuration only when intentionally decommissioned;
3. preserve canonical `.agents/` artifacts;
4. preserve runtime-adapter source/history when repository policy requires it;
5. install another runtime adapter when applicable.

Do not delete personal or managed Claude configuration merely because one repository stops using this adapter.

The repository-local delivery protocol remains runtime-neutral.

---

# Installation acceptance checklist

Before declaring the Claude adapter installed, verify:

- [ ] canonical `.agents/` files are present;
- [ ] `.agents/runtime-adapters/claude/` contains the adapter source;
- [ ] the bootstrap is materialized as the intended project `CLAUDE.md`;
- [ ] the source import `@../../AGENTS.md` was rewritten to `@.agents/AGENTS.md` in the root materialized copy;
- [ ] existing root and `.claude/CLAUDE.md` instructions were reconciled rather than blindly overwritten;
- [ ] `CLAUDE.local.md`, user rules, managed instructions, nested instructions, and `.claude/rules/` were checked for material conflicts when applicable;
- [ ] `claudeMdExcludes` and setting-source configuration do not suppress the canonical bootstrap;
- [ ] `--add-dir` and `CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD` were checked when applicable;
- [ ] added-directory instructions do not silently cross repository authority boundaries;
- [ ] common Claude launch directories were checked for materially different project settings or hooks;
- [ ] workspace-trust state was considered where project allow rules or additional-directory permissions matter;
- [ ] `/context` confirms the expected project instruction is loaded;
- [ ] `/memory` confirms the relevant project instructions/rules/memory state;
- [ ] `/status` confirms the expected settings sources;
- [ ] Planner / Reviewer routing reaches `.agents/prompts/plan-create-task.md`;
- [ ] Executor routing requires an exact governing validated task revision;
- [ ] auto memory is not treated as repository authority;
- [ ] project-scoped subagent memory cannot mutate the repository without authorization;
- [ ] built-in Explore/Plan delegation does not assume CLAUDE.md inheritance;
- [ ] agent-team runtime tasks and plan approvals are not confused with canonical task or approval state;
- [ ] project/user/local/managed permissions are not mistaken for delivery authorization;
- [ ] active material hooks were inspected for unauthorized side effects;
- [ ] optional plugins, skills, MCP, Superpowers, subagents, and agent teams remain methodology/evidence/runtime aids rather than authority;
- [ ] no canonical `.agents/` artifact was duplicated unnecessarily into Claude-specific instruction files.
