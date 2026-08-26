<!-- runtime-adapter: claude | version: 1.1 | status: approved-template -->
<!-- source-location import: @../../AGENTS.md -->
<!-- when materialized as ./CLAUDE.md, replace that import with @.agents/AGENTS.md -->

@../../AGENTS.md

# Claude Code Runtime Adapter

This file connects Claude Code to the repository-local, runtime-neutral software-delivery contract under `.agents/`.

The imported `.agents/AGENTS.md` contract is canonical for repository AI delivery.

This adapter adds only Claude Code-specific runtime behavior. It MUST NOT redefine or weaken canonical repository authority, the delivery protocol, governing tasks, evidence requirements, approval boundaries, or release boundaries.

## Canonical routing

Use the imported `.agents/AGENTS.md` contract for role routing and progressive loading.

`.agents/software-workflow.md` remains the normative software-delivery protocol.

When acting as Planner or Reviewer:

- load the canonical files required by `.agents/AGENTS.md`;
- use `.agents/prompts/plan-create-task.md` as the canonical delivery-orchestration procedure;
- resolve pending execution, review, remediation, approval, and baseline state before dependent successor planning;
- publish executable work only when canonical Task Readiness is satisfied.

When acting as Executor:

- load the exact governing validated task revision;
- load its implementation baseline and referenced authority;
- inspect only implementation context materially relevant to the task;
- execute within the task's bounded authority;
- report observed verification evidence and the correct terminal state.

Do not redo delivery planning merely to substitute a preferred implementation objective.

If a task stop condition is reached, return the issue to Planner/Reviewer orchestration.

## Claude instruction layers

Claude Code may also load:

- managed organization instructions;
- user `~/.claude/CLAUDE.md`;
- user `~/.claude/rules/`;
- repository `CLAUDE.local.md`;
- nested `CLAUDE.md` and `CLAUDE.local.md`;
- repository `.claude/rules/`;
- path-scoped rules;
- instructions from explicitly added directories when configured.

These are runtime instruction sources. They do not silently become approved repository authority merely because Claude loads them.

Repository-specific or scoped instructions MAY define compatible technical conventions, commands, tests, ownership rules, or implementation constraints.

They MUST NOT silently:

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

A direct user or designated-authority instruction MAY legitimately change repository authority when it is explicit and applicable.

If active instruction sources materially conflict or leave delivery authority ambiguous, surface the conflicting sources and affected decision rather than silently choosing whichever instruction is more convenient.

## CLAUDE.local.md and auto memory

`CLAUDE.local.md`, Claude auto memory, and subagent memory are supporting runtime context.

They are not repository authority by default.

Do not use machine-local memory, remembered preferences, or previous-session conclusions to silently redefine:

- requirements;
- architecture;
- task scope;
- accepted baseline;
- acceptance criteria;
- approval state;
- release state.

Reverify material repository claims against current approved authority or observed repository evidence.

If memory conflicts with the repository, the repository must be reverified rather than rewritten to match memory.

Do not persist secrets, credentials, sensitive external data, or unauthorized repository authority into auto memory.

Claude subagents may use persistent memory with `user`, `project`, or `local` scope.

`project`-scoped subagent memory is stored under `.claude/agent-memory/` and is a repository mutation that may be shared through version control. It MUST NOT be written merely because a subagent supports persistent memory.

During task-governed execution, project-scoped memory writes require compatibility with the governing task's scope and repository side-effect authorization. Outside execution, they require an applicable repository or user authorization basis.

When persistence is useful but repository mutation is not authorized, prefer an appropriate non-repository memory scope or keep the delegated result ephemeral.

All subagent memory remains supporting context until material claims are verified against repository authority or observed evidence.

## Claude skills, plugins, and MCP

Claude Code skills, plugins, MCP servers, slash commands, and other runtime extensions are engineering, analysis, and evidence aids.

Use relevant installed capabilities when they materially improve the current responsibility and their use is permitted.

Runtime methodology remains subordinate to:

1. applicable direct human and approved repository authority;
2. `.agents/software-workflow.md`;
3. `.agents/AGENTS.md`;
4. the exact governing validated task when executing;
5. applicable approval, permission, security, privacy, and side-effect boundaries.

Installed capability does not become repository authority.

A skill, plugin, MCP server, or command MUST NOT justify changing a delivery objective, requirement, architecture decision, acceptance criterion, approval state, or release state without legitimate authority.

## Superpowers

When Superpowers is installed and applicable, use it according to its current Claude Code skill-routing and bootstrap behavior.

Superpowers MAY guide technical practices such as design exploration, implementation planning, testing discipline, systematic debugging, work isolation, subagent coordination, technical review, and verification.

Superpowers governs **how technical work is performed**.

The canonical `.agents/` framework governs **what delivery work is legitimate, bounded, reviewable, and acceptable**.

Superpowers-generated specifications, plans, design documents, or other methodology artifacts do not automatically become approved repository authority.

During Executor work, keep methodology planning ephemeral unless the governing task or applicable repository authority explicitly permits the artifact to be persisted.

Do not commit methodology artifacts unless both artifact creation and Git commit are authorized.

If a Superpowers workflow conflicts with applicable direct user instructions, approved repository authority, the governing task, approval boundaries, or required stop conditions, treat it as a methodology conflict.

Adapt the methodology when its own rules allow that adaptation. If it cannot be followed without violating those boundaries, stop and surface the conflict.

## Subagents, agent teams, and delegation

Claude Code MAY use subagents, background delegated work, or agent teams when appropriate.

Delegation does not create new delivery authority.

### Planner / Reviewer delegation

Planner or Reviewer delegation MAY occur before a governing task exists and MUST remain bounded by:

- current verified repository state and accepted baseline when known;
- applicable intended authority;
- the specific planning, discovery, evidence, or review question;
- applicable approval and side-effect boundaries.

Planning or review delegation MUST NOT silently become implementation mutation.

Claude's built-in `Explore` and `Plan` subagents intentionally do not load `CLAUDE.md` or the parent session's Git-status context.

When delegating material work to either built-in agent, include the repository boundaries that the delegated question actually requires in the delegation prompt. At minimum, do not assume that this adapter or the imported canonical contract reached that subagent automatically.

Treat `Explore` and `Plan` results as supporting discovery or planning evidence. The main Planner/Reviewer session with canonical `.agents/` context remains responsible for authority decisions, gate state, task publication, remediation, and acceptance.

### Executor delegation

Executor delegation MUST remain bounded by:

- implementation baseline;
- exact governing task revision;
- authority inputs;
- in-scope and preserved behavior;
- execution constraints;
- stop conditions;
- remaining approval requirements;
- side-effect authorization.

A delegated worker MUST NOT turn a task-local technical assignment into an independent delivery objective.

### Agent teams

When Claude agent teams are enabled, teammates load normal project context including `CLAUDE.md`, but each teammate is an independent Claude Code session with its own context and shared team task coordination.

The team lead's runtime **plan approval** for a teammate is a technical coordination mechanism only.

It MUST NOT be treated as:

- canonical T5 Task Readiness;
- publication of a validated governing task;
- designated business, product, requirement, or architecture approval;
- implementation acceptance;
- side-effect authorization;
- release approval.

Team tasks are runtime coordination records, not canonical `.agents/tasks/` delivery contracts.

If teammates perform task-governed implementation, each delegated unit MUST remain within the same governing task revision and implementation baseline unless canonical planning has explicitly established separate validated tasks.

Subagent, teammate, or agent-team summaries and task states are supporting context or evidence until verified against the repository.

Parallel work MUST respect explicit dependencies and overlapping write surfaces.

Do not hide an independent implementation objective inside delegated work when it requires a separate validated task.

## Hooks, permissions, and settings

Claude Code permissions, sandboxing, settings, and hooks can enforce or automate runtime behavior.

They determine technical capability or enforcement. They do not themselves create repository delivery authority.

Apply both boundaries:

```text
runtime permission
AND
repository delivery authorization
```

An allow rule, remembered permission, hook, plugin hook, or unrestricted runtime mode does not automatically authorize:

- Git commit or push;
- pull-request creation;
- dependency installation or replacement;
- destructive data or infrastructure operations;
- external-system mutation;
- production changes;
- deployment;
- publication;
- release;
- access or persistence of secrets.

Hooks that can mutate repository or external state MUST have an authorization basis compatible with repository policy and the governing task.

A `PreToolUse` hook MAY strengthen safety by denying or escalating actions. A permissive hook or permission rule MUST NOT weaken repository authorization boundaries.

Treat `.claude/settings.local.json`, user settings, project settings, managed settings, subagent definitions, agent-team settings, and plugin-provided hooks as runtime configuration that may require inspection when they materially affect delivery.

A runtime permission inherited by a subagent or teammate does not create repository authorization. The same two-boundary rule applies independently to every delegated worker.

## Repository intelligence and evidence

When Graphify, Codebase Memory MCP, or equivalent repository-intelligence capabilities are available, follow the intelligence boundaries in `.agents/AGENTS.md` and the active Planner/Reviewer procedure or governing task.

Derived indexes, graphs, summaries, memory, and retrieval output remain supporting intelligence.

Material conclusions MUST be verified against approved repository authority or current observed implementation evidence as applicable.

Do not represent inferred command results, unobserved tests, local checks as CI, subagent summaries, skill output, plugin output, or cached memory as stronger evidence than was actually observed.

Before reporting **Review Required**, satisfy the governing task's applicable verification requirements and accurately report remaining verification limitations.

If execution reaches a valid stop condition before a reviewable implementation exists, report **Planning Required** with supporting evidence rather than claiming successful completion.

Final implementation acceptance remains a Planner/Reviewer responsibility.

## Operating rule

For every material repository action:

```text
Claude project CLAUDE.md
→ imported .agents/AGENTS.md
→ role-specific canonical loading
→ applicable Claude skills/plugins/subagents/agent teams/MCP
→ bounded work
→ observed evidence
→ canonical Planner/Reviewer loop
```

When Claude runtime methodology and repository delivery governance differ, preserve legitimate repository authority and surface the conflict.
