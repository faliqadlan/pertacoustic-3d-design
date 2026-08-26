---
title: Codex Runtime Adapter Setup
document_id: AGENT-RUNTIME-CODEX-README-001
version: 1.1
status: approved-template
language: en-US
last_updated: 2026-08-10
runtime: Codex
scope:
  - Codex adapter installation
  - root instruction materialization
  - existing-instruction reconciliation
  - optional runtime tooling recommendations
authority_note: This README is operator guidance for installing the Codex runtime adapter. It is not canonical repository authority and does not replace the delivery contract under .agents/.
---

# Codex Runtime Adapter

This directory contains the Codex-specific bootstrap for the runtime-neutral `.agents/` software-delivery framework.

The adapter connects Codex's native repository-instruction discovery to the canonical repository-local delivery contract.

The canonical delivery framework remains under:

```text
.agents/
├── AGENTS.md
├── software-workflow.md
├── context/
├── prompts/
└── tasks/
```

The Codex adapter does not redefine that framework.

## Files

```text
runtime-adapters/codex/
├── README.md
└── AGENTS.md
```

### `AGENTS.md`

The adapter `AGENTS.md` is intended to be materialized as the target repository's root:

```text
./AGENTS.md
```

It provides:

- Codex bootstrap routing into `.agents/AGENTS.md`;
- Planner / Reviewer / Executor role routing;
- Codex skill and plugin boundaries;
- Superpowers methodology integration when installed;
- subagent and delegation boundaries;
- runtime-permission versus repository-authorization rules.

It intentionally does not duplicate the full canonical delivery protocol.

### `README.md`

This file is for the human or automation installing the adapter.

It explains how to materialize the Codex bootstrap safely without destroying existing repository instructions.

---

# Installation model

The template repository permanently stores the adapter under:

```text
.agents/runtime-adapters/codex/
```

A target repository using Codex SHOULD materialize the adapter into Codex's native repository-instruction location.

Typical resulting repository:

```text
target-repository/
├── AGENTS.md
│
└── .agents/
    ├── AGENTS.md
    ├── software-workflow.md
    ├── context/
    │   └── project.md
    ├── prompts/
    │   └── plan-create-task.md
    └── tasks/
        └── _template.md
```

The installed repository SHOULD retain `.agents/runtime-adapters/` as runtime integration source/reference material.

This keeps the installed repository consistent with `.agents/AGENTS.md`, which defines `runtime-adapters/` as the location of runtime-specific integration material, and makes future adapter updates auditable against their materialized root instruction.

If a repository intentionally adopts a different packaging model, that repository-specific policy MUST preserve an equivalent discoverable source of runtime-adapter semantics and MUST NOT leave canonical `.agents/` documentation materially inaccurate.

---

# Codex instruction discovery

Codex uses repository instruction files in this order within each directory:

```text
AGENTS.override.md
AGENTS.md
<configured project_doc_fallback_filenames, in configured order>
```

At project scope, Codex walks from the project root toward the current working directory and includes at most one recognized instruction file per directory.

Within the same directory, `AGENTS.override.md` is selected before `AGENTS.md`; configured fallback filenames are considered only when neither standard file is selected.

Instructions closer to the current working directory are later in the combined instruction chain and therefore have higher runtime precedence.

Because of this behavior, installation MUST inspect both existing instruction files and the effective Codex project-instruction configuration before materializing this adapter.

Do not blindly overwrite or add a root `AGENTS.md` without checking which root instruction is currently active and which existing instruction would become shadowed.

For current Codex discovery behavior, consult the official Codex `AGENTS.md` documentation.

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

Repository-specific context, tasks, authority artifacts, and scoped context MAY extend this structure.

Do not replace valid repository-specific artifacts merely to make the target repository resemble the template.

## 2. Inspect existing Codex instructions and configuration

Before creating or replacing anything, inspect:

```text
./AGENTS.override.md
./AGENTS.md
```

Also determine the effective Codex values for:

```text
project_doc_fallback_filenames
project_doc_max_bytes
CODEX_HOME
```

Inspect any configured fallback instruction file that exists at the repository root, plus relevant nested standard, override, or configured fallback instruction files that already govern repository scopes.

Classify the root installation state as one of:

```text
A. no active root Codex instruction exists
B. root AGENTS.md is active
C. root AGENTS.override.md is active
D. both standard root files exist; AGENTS.override.md is active
E. a configured fallback root instruction is active
```

A configured fallback is part of the active repository instruction model and MUST NOT be silently discarded by introducing a higher-priority standard filename.

## 3. Materialize safely

### Case A — no active root Codex instruction exists

Materialize:

```text
.agents/runtime-adapters/codex/AGENTS.md
```

as:

```text
./AGENTS.md
```

No merge is required.

Confirm that no configured fallback instruction at the repository root would be newly shadowed by this file.

### Case B — root `AGENTS.md` already exists

Do NOT overwrite it blindly.

Review the existing file and merge the Codex adapter semantics into it.

Preserve legitimate repository-specific instructions such as:

- build or test commands;
- repository conventions;
- local ownership rules;
- scoped technical constraints;
- code-review expectations.

Ensure the merged root file still:

- routes Codex to `.agents/AGENTS.md`;
- preserves the canonical authority and evidence model;
- preserves Planner / Reviewer / Executor routing;
- preserves validated-task execution boundaries;
- preserves runtime-methodology and side-effect boundaries.

If the existing root file materially conflicts with the canonical `.agents/` framework, resolve the conflict explicitly before treating installation as complete.

### Case C — root `AGENTS.override.md` already exists

A root `AGENTS.md` alone is not sufficient because Codex selects the override at that directory level.

Do NOT overwrite or remove the override automatically.

Review why the override exists.

Then choose an explicit repository-approved resolution such as:

1. integrate the adapter bootstrap and required boundaries into the existing `AGENTS.override.md`;
2. retire or rename the override when it is no longer required, then materialize the adapter as `AGENTS.md`; or
3. preserve the override with an equivalent compatible bootstrap when repository policy intentionally requires it.

The resulting instruction file actually selected by Codex MUST route to the canonical `.agents/AGENTS.md` contract.

### Case D — both root files exist

Codex will select the root `AGENTS.override.md` rather than the root `AGENTS.md`.

Treat this as Case C.

Do not assume that updating only `AGENTS.md` changes active Codex behavior.

### Case E — a configured fallback root instruction is active

Do NOT create `./AGENTS.md` without reconciling the active fallback first.

Creating a standard `AGENTS.md` would take precedence over the configured fallback at the same directory and could silently remove existing repository instructions from Codex's active chain.

Choose an explicit repository-approved resolution such as:

1. merge the fallback's legitimate repository-specific semantics into the materialized root `AGENTS.md`, then retain or retire the fallback according to repository policy;
2. keep the configured fallback as the active root instruction and integrate an equivalent canonical `.agents/` bootstrap into it; or
3. change the Codex fallback configuration intentionally and verify the resulting instruction chain.

Preserve legitimate existing repository instructions and verify which file Codex actually selects after the change.

## 4. Review nested instructions

Existing nested instruction files MAY remain.

This includes standard files, overrides, and configured fallback instruction filenames.

They are useful for scoped technical rules such as:

```text
services/payments/AGENTS.override.md
packages/sdk/AGENTS.md
apps/web/AGENTS.md
```

They MUST remain compatible with the canonical repository delivery contract.

Review nested instructions for rules that could materially:

- redefine approved behavior;
- change requirement authority;
- weaken architecture constraints;
- authorize implementation outside a validated task;
- broaden task scope;
- change acceptance semantics;
- authorize otherwise forbidden side effects;
- weaken security, privacy, safety, compliance, or release boundaries.

A conflict is a repository-configuration defect.

Do not rely on root instructions to neutralize a conflicting narrower instruction, because narrower Codex instructions have higher runtime precedence.

## 5. Verify instruction loading

Start a fresh Codex run from the repository root and verify that Codex reports the expected instruction sources.

At minimum, confirm that:

1. the selected root instruction is the intended `AGENTS.md`, `AGENTS.override.md`, or deliberately retained configured fallback;
2. the active root instruction routes to `.agents/AGENTS.md`;
3. no legitimate pre-existing root instruction was unintentionally shadowed;
4. the effective combined project-instruction chain fits within `project_doc_max_bytes` or the repository has intentionally raised/split the limit;
5. no critical instruction is truncated;
6. active instructions do not contain conflicting canonical-delivery semantics.

When the repository uses nested instructions, verify from representative scoped working directories as well.

Codex rebuilds its instruction chain for a new run/session. Restart Codex after changing instruction files before diagnosing stale behavior.

Use the current official Codex documentation for exact verification commands and configuration options.

---

# Instruction-size discipline

Keep the materialized root adapter concise.

The root adapter is a bootstrap and runtime boundary file, not the location for:

- the full software-delivery protocol;
- large PRDs;
- architecture specifications;
- requirement registries;
- complete task contracts;
- long runtime tutorials;
- copies of Superpowers skills.

Codex limits the combined project-instruction content it loads according to the effective `project_doc_max_bytes` runtime configuration.

Large root instructions can reduce the available budget for legitimate nested repository instructions, and Codex stops adding project instructions when the configured combined limit is reached.

After merging this adapter with pre-existing root instructions, verify the effective combined instruction size and loading behavior from representative working directories.

Prefer progressive loading through `.agents/AGENTS.md`, scoped context, tasks, and repository-native authority instead of duplicating content into Codex instruction files.

Check current Codex documentation before depending on a specific numeric size limit.

---

# Optional engineering methodology

The canonical `.agents/` framework intentionally does not mandate a particular generic software-engineering methodology.

Codex MAY use:

- native Codex skills;
- installed plugins;
- MCP servers;
- subagents;
- repository-specific tools;
- external engineering methodologies;

when relevant and permitted.

The materialized Codex adapter defines the boundary between those capabilities and repository delivery governance.

---

# Superpowers

Superpowers is a recommended optional engineering methodology for Codex.

It is not a dependency of the canonical `.agents/` framework.

When desired, install Superpowers through the current Codex plugin marketplace using the upstream Superpowers installation guidance.

Do not copy or vendor Superpowers skills into this repository merely to make this adapter work.

Do not hard-code marketplace installation commands into this template when upstream installation guidance can change independently.

After installation, Superpowers SHOULD remain runtime tooling:

```text
Superpowers
→ engineering methodology

.agents/
→ repository delivery governance
```

Superpowers-generated technical plans, design notes, or other methodology artifacts do not automatically become approved repository authority.

The Codex adapter defines the required boundary when Superpowers is used during Planner, Reviewer, or Executor work.

## Upstream reference

Superpowers:

```text
https://github.com/obra/superpowers
```

Use the current upstream README or official Codex plugin-marketplace experience for installation and update instructions.

---

# Other Codex plugins and skills

Other installed capabilities MAY be used when appropriate.

Examples include:

- Codex Security;
- GitHub workflows;
- CI debugging;
- repository-analysis skills;
- domain-specific implementation skills;
- documentation tooling;
- MCP integrations.

Installation of a capability does not give it repository authority.

Its use remains subject to:

```text
human / approved repository authority
→ canonical software-workflow.md
→ canonical .agents/AGENTS.md
→ governing task when executing
→ approval and side-effect boundaries
```

A plugin may provide technical methodology, discovery, evidence, or automation.

It MUST NOT silently redefine delivery authority.

---

# MCP and repository intelligence

Graphify, Codebase Memory MCP, and comparable repository-intelligence systems MAY be configured independently of this adapter.

The Codex adapter does not install or configure them automatically.

When available, their use is governed by:

```text
.agents/AGENTS.md
```

and, for Planner/Reviewer work:

```text
.agents/prompts/plan-create-task.md
```

A task MAY also declare a repository-intelligence capability as required when execution genuinely depends on it.

Derived indexes and summaries remain supporting intelligence rather than authority.

---

# Runtime permissions

Codex sandbox, approval, network, filesystem, and tool configuration determine what the runtime is technically capable of doing.

Repository authorization remains a separate concern.

Installation SHOULD NOT configure Codex to bypass the repository's approval model.

The operative rule is:

```text
runtime permission
AND
repository authorization
```

Both must allow an action before it may proceed.

Examples include:

- commits;
- pushes;
- pull-request creation;
- dependency changes;
- external-system mutation;
- destructive operations;
- deployment;
- release.

---

# Updating the adapter

Runtime behavior evolves independently of the canonical `.agents/` protocol.

When updating this Codex adapter:

1. verify current Codex instruction-discovery behavior from official OpenAI documentation;
2. verify any optional methodology integration from its current upstream source;
3. preserve compatibility with the canonical frozen `.agents/` artifacts;
4. change only runtime-specific behavior;
5. do not copy runtime details back into `software-workflow.md` unless they reveal a genuinely runtime-neutral protocol requirement.

An adapter update does not automatically require a canonical protocol version change.

Likewise, a canonical protocol update does not automatically require adapter changes unless the runtime bootstrap or boundary semantics are affected.

---

# Removing or switching runtimes

Removing the Codex adapter SHOULD NOT require removing the canonical `.agents/` framework.

To stop using this adapter:

1. remove or reconcile the materialized Codex root instruction according to repository policy;
2. remove Codex-specific optional tooling when desired;
3. preserve canonical `.agents/` artifacts;
4. install another runtime adapter when applicable.

The repository-local delivery protocol remains runtime-neutral.

---

# Installation acceptance checklist

Before declaring the Codex adapter installed, verify:

- [ ] canonical `.agents/` files are present;
- [ ] the effective `CODEX_HOME`, `project_doc_fallback_filenames`, and `project_doc_max_bytes` values are understood where they affect this repository;
- [ ] the active root Codex instruction file is known;
- [ ] an existing root `AGENTS.md` was merged rather than blindly overwritten;
- [ ] an existing root `AGENTS.override.md` was explicitly reconciled;
- [ ] any active configured fallback root instruction was explicitly reconciled;
- [ ] no legitimate root instruction was unintentionally shadowed;
- [ ] active root instructions route to `.agents/AGENTS.md`;
- [ ] nested Codex standard, override, and configured fallback instructions were checked for material protocol conflicts;
- [ ] the effective combined project-instruction chain is not truncating critical guidance;
- [ ] Planner / Reviewer routing reaches `.agents/prompts/plan-create-task.md`;
- [ ] Executor routing requires an exact governing validated task revision;
- [ ] optional skills and plugins remain methodology/evidence aids rather than authority;
- [ ] Superpowers, when installed, remains optional runtime methodology;
- [ ] runtime permissions are not mistaken for repository authorization;
- [ ] instruction loading was verified in a fresh Codex run;
- [ ] no canonical `.agents/` artifact was duplicated unnecessarily into the root runtime instruction.
