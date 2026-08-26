---
title: Antigravity Runtime Adapter Setup
document_id: AGENT-RUNTIME-ANTIGRAVITY-README-001
version: 1.1
status: approved-template
language: en-US
last_updated: 2026-08-10
runtime: Antigravity
scope:
  - Antigravity adapter installation
  - Workspace Rule materialization and activation
  - existing Global and Workspace Rule reconciliation
  - optional runtime tooling recommendations
authority_note: This README is operator guidance for installing the Antigravity runtime adapter. It is not canonical repository authority and does not replace the delivery contract under .agents/.
---

# Antigravity Runtime Adapter

This directory contains the Antigravity-specific bootstrap for the runtime-neutral `.agents/` software-delivery framework.

The adapter connects Antigravity Workspace Rules to the canonical repository-local delivery contract.

The canonical delivery framework remains under:

```text
.agents/
├── AGENTS.md
├── software-workflow.md
├── context/
├── prompts/
└── tasks/
```

The Antigravity adapter does not redefine that framework.

## Files

```text
runtime-adapters/antigravity/
├── README.md
└── rules/
    └── code-agent-workflow.md
```

### `rules/code-agent-workflow.md`

The adapter rule is intended to be materialized as:

```text
.agents/rules/code-agent-workflow.md
```

and configured in Antigravity as a Workspace Rule with activation mode:

```text
Always On
```

It provides:

- bootstrap routing into `.agents/AGENTS.md`;
- Planner / Reviewer / Executor role boundaries;
- Antigravity Rules and Workflow boundaries;
- skill, plugin, MCP, and Superpowers methodology boundaries;
- delegated-agent boundaries;
- Antigravity artifact and evidence boundaries;
- runtime-permission versus repository-authorization rules.

It intentionally does not duplicate the canonical software-delivery protocol.

### `README.md`

This file is for the human or automation installing the adapter.

It explains how to materialize and activate the Workspace Rule safely without destroying or silently overriding legitimate existing Antigravity customizations.

---

# Installation model

The template repository permanently stores the adapter under:

```text
.agents/runtime-adapters/antigravity/
```

A target repository using Antigravity SHOULD retain that adapter source and materialize its runtime rule into Antigravity's native Workspace Rules location.

Typical resulting repository:

```text
target-repository/
└── .agents/
    ├── AGENTS.md
    ├── software-workflow.md
    ├── context/
    │   └── project.md
    ├── prompts/
    │   └── plan-create-task.md
    ├── tasks/
    │   └── _template.md
    ├── runtime-adapters/
    │   └── antigravity/
    │       ├── README.md
    │       └── rules/
    │           └── code-agent-workflow.md
    └── rules/
        └── code-agent-workflow.md
```

The copy under `.agents/runtime-adapters/antigravity/` is the adapter source/reference.

The copy under `.agents/rules/` is the Antigravity-native materialized Workspace Rule.

Keeping both makes runtime materialization auditable and allows future adapter updates to be compared explicitly.

## Antigravity Projects and multi-repository scope

Current Antigravity Projects may contain more than one folder or repository.

This adapter remains **repository-local**.

When one Antigravity Project contains multiple repositories, install and verify the adapter independently for every repository that is intended to use this delivery framework.

Do not assume that a Rule discovered from one repository is legitimate authority for another repository in the same Antigravity Project.

Cross-repository work MUST preserve each repository's own authority, accepted baseline, governing task, and side-effect boundaries unless an approved higher-level authority explicitly coordinates them.

---

# Antigravity Rules model

Antigravity supports both Global Rules and Workspace Rules.

## Global Rules

Global Rules apply across workspaces and currently live at:

```text
~/.gemini/GEMINI.md
```

They are user/runtime-level instructions.

A Global Rule does not automatically become repository authority merely because Antigravity loads it.

## Workspace Rules

Workspace Rules for the current workspace or Git root currently live under:

```text
.agents/rules/
```

Antigravity also maintains backward compatibility with:

```text
.agent/rules/
```

This adapter uses the current `.agents/rules/` location.

Workspace Rules may use activation modes including:

- Manual;
- Always On;
- Model Decision;
- Glob.

The materialized `code-agent-workflow.md` adapter MUST be configured as:

```text
Always On
```

because it establishes the repository-wide delivery bootstrap rather than a conditional technical convention.

## File references

Antigravity Rules support `@` file references.

Relative references are resolved relative to the Rule file.

The adapter uses:

```text
@../AGENTS.md
```

from:

```text
.agents/rules/code-agent-workflow.md
```

to route into:

```text
.agents/AGENTS.md
```

Do not rewrite the adapter to duplicate the full canonical contract when the reference is sufficient.

## Rule-size limit

Antigravity currently limits each Rule file to 12,000 characters.

The adapter MUST remain below the runtime's current per-rule limit after any repository-specific reconciliation.

Do not grow the bootstrap into a second copy of the canonical delivery framework.

Check current official Antigravity documentation before depending on a specific numeric limit.

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

Repository-specific authority, tasks, scoped context, and planning artifacts MAY extend this structure.

Do not replace valid repository-specific artifacts merely to make an existing repository resemble the template.

## 2. Inspect existing Antigravity customizations

Before materializing the adapter, inspect:

```text
~/.gemini/GEMINI.md
.agents/rules/
.agent/rules/
.agents/hooks.json
~/.gemini/config/hooks.json
```

when those locations exist and are accessible.

Also inspect the Antigravity Customizations panel and effective Project settings for the active Rules, plugins, permissions, and execution controls that apply to the repository.

Identify:

- existing Global Rules that materially affect software-delivery behavior;
- an existing `.agents/rules/code-agent-workflow.md`;
- other active Workspace Rules that could conflict with the canonical `.agents/` contract;
- legacy `.agent/rules/` rules that remain active;
- Model Decision or Glob rules that may become active for repository areas governed by this framework;
- workspace or global JSON Hooks that can execute commands before, during, or after agent/tool activity;
- plugin-provided Rules or Hooks with material repository side effects;
- Project-level permissions or execution settings that materially affect the repository.

Do not assume that a repository is free of runtime automation merely because `.agents/rules/` is empty.

Hooks are especially important because they can execute independently of the prose in this bootstrap Rule. A repository installation is not safe merely because the Rule text itself is correct.

## 3. Classify the installation state

Use one of these installation cases:

```text
A. no existing target rule at .agents/rules/code-agent-workflow.md
B. the target rule already exists and is this adapter
C. the target rule exists with repository-specific or unrelated content
D. another active Workspace Rule materially conflicts with the adapter
E. a Global Rule materially conflicts with or ambiguously changes delivery authority
```

Several cases may apply simultaneously.

Hooks and Project-level permission conflicts are assessed separately because they are runtime behavior/configuration rather than Rule-file merge cases.

## 4. Materialize the Workspace Rule

### Case A — no existing target rule

Copy:

```text
.agents/runtime-adapters/antigravity/rules/code-agent-workflow.md
```

to:

```text
.agents/rules/code-agent-workflow.md
```

Then configure the materialized rule as **Always On**.

### Case B — the existing target rule is already this adapter

Compare it with the adapter source under:

```text
.agents/runtime-adapters/antigravity/rules/code-agent-workflow.md
```

If the materialized rule is current and unmodified, no content merge is required.

Verify that it remains configured as **Always On**.

If it has intentional repository-specific additions, treat it as Case C.

### Case C — the target filename already contains other content

Do NOT overwrite it blindly.

Prefer one of these explicit resolutions:

1. preserve the existing rule under a distinct meaningful Workspace Rule filename and materialize this adapter at `code-agent-workflow.md`;
2. merge only genuinely repository-wide compatible semantics into the adapter while keeping the result below Antigravity's rule-size limit; or
3. retain the existing target rule as a repository-specific rule and choose another clearly documented filename for the materialized bootstrap, provided it is configured **Always On** and its `@` routing remains correct.

Avoid merging unrelated technical instructions into the bootstrap merely to reduce file count.

Antigravity can load multiple Workspace Rules, so separate rules are normally preferable when their responsibilities are distinct.

### Case D — another Workspace Rule conflicts

Do not rely on the adapter to neutralize a contradictory active rule.

Review the conflicting rule and resolve the repository configuration explicitly.

A Workspace Rule is incompatible when it materially attempts to:

- redefine approved business or product intent;
- change approved requirements;
- weaken architecture or repository policy;
- bypass a canonical delivery gate;
- authorize implementation without a validated task;
- broaden a governing task;
- replace the exact governing task revision;
- self-approve implementation acceptance;
- treat acceptance as release;
- weaken security, privacy, safety, compliance, permission, or side-effect boundaries.

Scoped technical rules MAY remain active when they are compatible with those boundaries.

### Case E — a Global Rule conflicts or creates authority ambiguity

Global Rules are user/runtime-level instructions and are not stored in the repository.

Do not silently edit a user's Global Rule as part of repository installation.

Instead:

1. identify the conflicting or ambiguous Global Rule;
2. identify the affected repository delivery decision;
3. determine whether the Global Rule represents an explicit applicable user/designated-authority instruction or merely generic runtime preference;
4. reconcile the conflict explicitly before relying on the adapter for material delivery work.

Generic Global Rules MUST NOT silently become business, product, requirement, architecture, acceptance, or release authority.

Direct explicit user instructions may legitimately affect repository authority when applicable, as defined by the canonical `.agents/` contract.


## 5. Audit active JSON Hooks

Antigravity Hooks can run local commands at execution lifecycle events such as before or after tool use, before or after model invocation, and when the execution loop stops.

Inspect active repository, global, and plugin-provided Hooks that can affect this repository.

A Hook that mutates source, Git state, dependencies, external systems, infrastructure, generated artifacts, or other delivery state MUST have an authorization basis compatible with the canonical `.agents/` contract.

Do not treat automatic Hook execution as implicit repository authorization.

If an active Hook can perform a material side effect outside the governing task or applicable repository policy, disable, scope, or reconcile that Hook before relying on the adapter for execution.

Diagnostic or read-only Hooks MAY remain active when they do not weaken repository authority, evidence integrity, or runtime safety.

---

# 6. Activate the adapter

Materializing the Markdown file is not sufficient by itself.

Open Antigravity's Customizations panel and verify that the Workspace Rule containing the adapter bootstrap is configured as:

```text
Always On
```

Do not use:

```text
Manual
Model Decision
Glob
```

for the canonical bootstrap.

Those activation modes are appropriate for conditional or scoped technical rules, not for the repository-wide delivery contract entrypoint.

If the adapter was materialized under a different filename because of repository-specific reconciliation, verify that the actual replacement bootstrap rule is the one configured **Always On**.

---

# 7. Verify the `@` reference

The canonical materialized path is:

```text
.agents/rules/code-agent-workflow.md
```

and its canonical repository-contract reference is:

```text
@../AGENTS.md
```

That reference should resolve to:

```text
.agents/AGENTS.md
```

If the bootstrap rule is moved to another directory, recalculate the relative path rather than assuming `@../AGENTS.md` remains correct.

Do not silently move the canonical `.agents/AGENTS.md` contract merely to accommodate a runtime adapter.

---

# 8. Verify effective runtime behavior

After installing or changing Rules, start a fresh Antigravity agent session and verify the runtime behavior.

At minimum, confirm that:

1. the bootstrap Workspace Rule is active;
2. its activation mode is **Always On**;
3. `@../AGENTS.md` resolves to the intended canonical contract;
4. Planner / Reviewer work reaches `.agents/prompts/plan-create-task.md`;
5. Executor work requires a published validated task with an exact governing task revision;
6. existing Global and Workspace Rules do not materially contradict the canonical contract;
7. active JSON Hooks and plugin-provided Hooks do not perform unauthorized material side effects;
8. the bootstrap remains below Antigravity's current per-rule character limit;
9. no canonical `.agents/` artifact has been duplicated unnecessarily into Rules;
10. runtime permissions are not being treated as repository authorization;
11. in a multi-folder Antigravity Project, the repository-local adapter is not being treated as authority for a different repository.

When relevant, test from repository areas governed by conditional Glob or Model Decision rules to expose conflicts that may not appear from the repository root.

When the Antigravity Project contains multiple repositories, perform representative verification in each repository that uses the framework.

Use current official Antigravity documentation when verification behavior changes between runtime versions.

---

# Workspace Rule discipline

Keep the materialized bootstrap small and stable.

Use additional Workspace Rules for Antigravity-specific technical guidance that genuinely benefits from persistent runtime context.

Examples MAY include:

```text
.agents/rules/frontend-conventions.md
.agents/rules/python-testing.md
.agents/rules/api-contracts.md
```

Those examples are not required filenames.

Prefer scoped activation modes for scoped technical rules when appropriate.

Do not put the following into the bootstrap merely because Antigravity Rules are convenient:

- full PRDs;
- large requirement registries;
- architecture specifications;
- full task contracts;
- copies of `software-workflow.md`;
- copies of `plan-create-task.md`;
- entire external engineering methodologies;
- large runtime tutorials.

Use canonical repository authority, context, tasks, and progressive loading instead.

---

# Workflows

Antigravity Workflows are runtime convenience mechanisms for repeatable sequences of steps.

They are distinct from Rules:

```text
Rules
→ persistent reusable prompt context

Workflows
→ slash-invoked trajectory / step sequence
```

A repository MAY use Workflows for runtime convenience.

For example, a thin Workflow MAY help invoke a repository procedure consistently.

However, do not maintain a second or divergent copy of the canonical Planner/Reviewer procedure as an Antigravity Workflow.

The canonical procedure remains:

```text
.agents/prompts/plan-create-task.md
```

If a Workflow exists to start planning/review, it SHOULD route to that canonical procedure rather than restating its full contents.

Workflow invocation does not grant new repository authority or side-effect permission.

---

# Plugins, skills, and MCP

Antigravity plugins can bundle capabilities such as:

- skills;
- rules;
- MCP servers;
- hooks.

Those capabilities are runtime tooling.

They do not automatically become repository authority.

Use them within:

```text
direct applicable human / repository authority
→ .agents/software-workflow.md
→ .agents/AGENTS.md
→ exact governing validated task when executing
→ approval and side-effect boundaries
```

Workspace-specific plugins may be installed under Antigravity's supported workspace plugin locations.

Global plugins may apply across repositories.

Treat plugin-provided Rules with the same conflict discipline as other active Antigravity Rules.

Hooks or MCP capabilities that can perform side effects remain subject to the same repository authorization boundaries as direct agent actions.

Because Hooks may execute automatically at lifecycle events, their configuration MUST be audited as runtime policy rather than assumed to inherit authorization from the agent's current prompt.

---

# Superpowers

Superpowers is a recommended optional engineering methodology for Antigravity.

It is not a dependency of the canonical `.agents/` framework.

When desired, install or update Superpowers using the **current upstream Superpowers Antigravity instructions**.

Do not vendor or manually copy Superpowers skills into this repository merely to make the adapter work.

Do not duplicate Superpowers methodology into `code-agent-workflow.md`.

Current upstream Superpowers integration uses Antigravity's plugin system and session-start bootstrap behavior, but installation details may evolve independently of this template.

Use the upstream source of truth:

```text
https://github.com/obra/superpowers
```

After installation:

```text
Superpowers
→ engineering methodology

.agents/
→ repository delivery governance
```

Superpowers-generated technical plans, design documents, specifications, or other methodology artifacts do not automatically become approved repository authority.

During Executor work, methodology artifacts remain ephemeral unless repository authority or the governing task explicitly permits their persistence.

Repository mutation and Git commit remain separate authorization concerns.

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

A validated task MAY identify a repository-intelligence capability as required when execution genuinely depends on it.

Derived indexes, graphs, summaries, or retrieval results remain supporting intelligence rather than authority.

---

# Antigravity artifacts

Antigravity may create plans, task lists, diagrams, screenshots, browser recordings, diffs, or other runtime artifacts.

Those artifacts can be useful for communication or evidence.

They are not automatically:

- approved product authority;
- requirements;
- architecture authority;
- validated tasks;
- acceptance records;
- release approval.

Preserve or commit runtime artifacts only when repository policy, the governing task, or designated authority makes that appropriate.

Do not turn Antigravity's artifact system into a parallel repository authority model.

---

# Runtime permissions and safety

Antigravity runtime and Project settings determine what the agent is technically capable of doing.

Depending on the Antigravity version and surface, relevant controls may include:

- terminal execution policy;
- outside-folder or non-workspace file-access policy;
- Project-level permissions;
- security presets or Strict Mode where available;
- browser access controls;
- artifact review behavior;
- terminal sandboxing;
- sandbox network access.

These settings are runtime safety and capability controls.

Current Antigravity Projects can apply these controls at Project scope, so operators MUST verify the effective settings for the Project that contains the repository rather than relying only on global defaults.

They do not replace repository delivery authorization.

The operative rule is:

```text
runtime permission
AND
repository delivery authorization
```

Both must allow an action before it may proceed.

This applies to:

- material shell side effects;
- Git commits;
- pushes and pull requests;
- dependency installation or replacement;
- browser mutations of external systems;
- destructive data or infrastructure operations;
- production changes;
- deployment;
- publication;
- release.

A runtime configured for high autonomy MUST still obey the validated task and repository authorization boundaries.

A runtime configured more restrictively may require additional human review even when the repository task authorizes the action.

---

# Security recommendations

Runtime security configuration is repository- and environment-specific.

For repositories handling sensitive source, credentials, regulated data, production systems, or destructive operations, operators SHOULD review Antigravity's current Project security preset, terminal execution policy, outside-folder access policy, sandboxing, browser restrictions, permissions, and any Strict Mode control exposed by the active runtime version.

Do not encode a universal runtime-security profile in this template because legitimate environments differ.

Repository-specific policy MAY require stricter settings.

Runtime security settings MAY strengthen repository safety requirements but MUST NOT silently weaken them.

---

# Updating the adapter

Antigravity runtime behavior evolves independently of the canonical `.agents/` protocol.

When updating this adapter:

1. verify current Workspace Rule location and activation behavior from official Antigravity documentation;
2. verify current `@` reference semantics;
3. verify the current per-rule size limit;
4. review changes to Antigravity Project/multi-folder behavior;
5. review changes to Global Rules, Workspace Rules, JSON Hooks, plugins, Workflows, permissions, and sandbox behavior when relevant;
6. verify optional Superpowers integration from its current upstream source;
7. preserve compatibility with the canonical frozen `.agents/` artifacts;
8. change only runtime-specific behavior.

After updating:

1. update the source under `.agents/runtime-adapters/antigravity/`;
2. reconcile the materialized `.agents/rules/` copy intentionally;
3. verify its activation remains **Always On**;
4. start a fresh Antigravity session and verify effective behavior.

An Antigravity adapter update does not automatically require a canonical protocol version change.

A canonical protocol update does not automatically require an adapter update unless the runtime bootstrap or boundary semantics are affected.

---

# Removing or switching runtimes

Removing the Antigravity adapter SHOULD NOT require removing the canonical `.agents/` framework.

To stop using this adapter:

1. remove or retire the materialized Antigravity Workspace Rule according to repository policy;
2. remove Antigravity-specific optional tooling when desired;
3. preserve the canonical `.agents/` artifacts;
4. preserve runtime-adapter history when repository policy requires it;
5. install another runtime adapter when applicable.

If Global Rules were changed specifically for this repository, reconcile them separately; they are user-level state and are not removed by deleting repository files.

The repository-local delivery protocol remains runtime-neutral.

---

# Installation acceptance checklist

Before declaring the Antigravity adapter installed, verify:

- [ ] canonical `.agents/` files are present;
- [ ] `.agents/runtime-adapters/antigravity/` contains the adapter source;
- [ ] the runtime bootstrap is materialized under `.agents/rules/`;
- [ ] the materialized bootstrap is configured **Always On**;
- [ ] its `@` reference resolves to `.agents/AGENTS.md`;
- [ ] an existing target rule was reconciled rather than blindly overwritten;
- [ ] existing Global Rules were checked for material authority/protocol conflicts;
- [ ] existing Workspace and legacy `.agent/rules/` rules were checked for material conflicts;
- [ ] conditional Model Decision or Glob rules cannot silently weaken canonical boundaries;
- [ ] active workspace, global, and plugin-provided JSON Hooks were checked for unauthorized material side effects;
- [ ] effective Project-level permissions and execution controls were verified;
- [ ] multi-folder Projects were checked so one repository's adapter is not treated as another repository's authority;
- [ ] the materialized rule remains within Antigravity's current per-rule size limit;
- [ ] Planner / Reviewer routing reaches `.agents/prompts/plan-create-task.md`;
- [ ] Executor routing requires an exact governing validated task revision;
- [ ] Workflows do not duplicate or replace the canonical Planner/Reviewer procedure;
- [ ] optional skills, plugins, MCPs, and Superpowers remain methodology/evidence aids rather than authority;
- [ ] Antigravity runtime artifacts are not treated as repository authority by default;
- [ ] runtime permissions are not mistaken for repository authorization;
- [ ] effective behavior was verified in a fresh Antigravity session;
- [ ] no canonical `.agents/` artifact was duplicated unnecessarily into runtime Rules.
