# AI asset conventions across coding harnesses

## Question

What filesystem conventions, asset families, metadata, default locations, precedence rules, and interoperability constraints exist across Pi, Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, and other material coding harnesses, sufficient to recommend an evidence-based v1 compatibility set?

## Executive finding

There is a useful common core, but no universal “AI asset” filesystem model.

- **Agent Skills is the strongest shared format.** Pi, Claude Code, Codex, Cursor, GitHub Copilot, and Gemini CLI all document `SKILL.md`-based skills, and most recognize the shared `.agents/skills/` location in at least one scope. The portable core is a skill directory with a required `SKILL.md` whose YAML frontmatter includes `name` and `description`; hosts add fields and discovery behavior beyond that core. [Agent Skills specification](https://agentskills.io/specification)
- **`AGENTS.md` is the strongest shared instruction format**, but hosts differ on which directories they scan, whether they accept alternate names, and whether closer files override or merely follow broader files. [AGENTS.md specification](https://agents.md/)
- **Agents, rules, and prompt/command files are host dialects.** Their paths, frontmatter, activation rules, and precedence are not portable enough for one generic parser.
- **Discovery and effective activation are different facts.** The catalog should preserve every discovered placement and record host-specific resolution separately instead of silently deciding that one file is universally “active.”

## Primary-source findings

### Shared formats

#### Agent Skills

The open Agent Skills format defines a skill as a directory containing `SKILL.md`, with optional bundled scripts, references, and assets. The portable frontmatter core is `name` and `description`; optional standard fields include `license`, `compatibility`, `metadata`, and `allowed-tools`. Hosts extend this vocabulary, so unknown fields must be retained rather than discarded. [Agent Skills specification](https://agentskills.io/specification)

The standard defines the package format, not one mandatory installation root for every host. `.agents/skills/` is therefore an interoperability convention used by several hosts, not the only path the dashboard should scan.

#### AGENTS.md

`AGENTS.md` is plain Markdown with directory-scoped instructions. Nested files apply to the subtree beneath them, and more-specific instructions take precedence under the shared convention. Harnesses may add fallback names, override filenames, imports, or different load timing. [AGENTS.md specification](https://agents.md/)

### Harness matrix

| Harness | Skills | Instructions / rules | Agents | Prompts / commands | Resolution details relevant to the catalog |
|---|---|---|---|---|---|
| **Pi** | Global `~/.pi/agent/skills/`, `~/.agents/skills/`; project `.pi/skills/`, `.agents/skills/`; package/settings/CLI roots. Recursively finds `SKILL.md`; Pi-specific roots also accept direct Markdown skills. | Loads `AGENTS.md` or `CLAUDE.md`; `AGENTS.override.md` replaces the ordinary context file in the same directory. | No built-in subagent asset convention; Pi explicitly delegates this to extensions/packages. | Global `~/.pi/agent/prompts/*.md`; project `.pi/prompts/*.md`; package/settings/CLI roots. Markdown frontmatter may include `description` and `argument-hint`. | Project resources require project trust. Duplicate skill names warn and keep the first discovered skill. Prompt-template discovery is non-recursive unless another root is configured explicitly. |
| **Claude Code** | Personal `~/.claude/skills/<name>/SKILL.md`; project `.claude/skills/<name>/SKILL.md`; managed and plugin skills; nested project skill directories are supported. | Managed, user `~/.claude/CLAUDE.md`, project `CLAUDE.md` or `.claude/CLAUDE.md`, `CLAUDE.local.md`, and recursive `.claude/rules/*.md`. Claude does not directly read `AGENTS.md`, but a `CLAUDE.md` can import it. | Project `.claude/agents/` and user `~/.claude/agents/`, recursively; Markdown plus YAML frontmatter. | `.claude/commands/*.md` remains supported, but custom commands have been merged into skills. | Managed instructions load before user and project instructions; closer project instructions are later in context. For skills, enterprise overrides personal, personal overrides project; plugin skills are namespaced. Symlinked skills resolving to the same target are loaded once. |
| **Codex** | Repository `.agents/skills/` from the current directory upward to repository root; user `~/.agents/skills/`; admin `/etc/codex/skills`; bundled system skills. Symlinked skill folders are supported. | Global `~/.codex/AGENTS.override.md` or `~/.codex/AGENTS.md`; then one instruction file per directory from repository root to current directory, checking `AGENTS.override.md`, `AGENTS.md`, then configured fallback names. | No stable standalone custom-agent file convention was identified in the reviewed first-party Codex docs. | `~/.codex/prompts/*.md` exists but is deprecated in favor of skills; only top-level Markdown files are scanned. | Instruction files are concatenated root-to-leaf, so closer guidance comes later. Skills with the same `name` are not merged and can both appear. Repository skill discovery follows the launch directory’s ancestor chain, not every nested directory in the repository. |
| **Cursor** | Project `.agents/skills/`, `.cursor/skills/`; user `~/.agents/skills/`, `~/.cursor/skills/`; also Claude and Codex skill roots. Recursively finds `SKILL.md`, including nested project roots. | `.cursor/rules/**/*.mdc` with `description`, `globs`, and `alwaysApply`; root and nested `AGENTS.md`. | Project `.cursor/agents/`, plus Claude/Codex compatibility roots; corresponding user roots. Markdown plus YAML frontmatter. | Cursor documents migration of dynamic rules and slash commands into skills, but the reviewed Skills page does not provide enough stable filesystem detail to promise legacy command discovery in v1. | Nested skills are directory-scoped. Project agents beat user agents, and `.cursor/` beats Claude/Codex compatibility roots on name conflict. Team rules, project rules, and user rules are merged with that documented precedence. Local user skills are not copied automatically to cloud/remote workers. |
| **GitHub Copilot** | Project `.github/skills/`, `.claude/skills/`, `.agents/skills/`; personal `~/.copilot/skills/`, `~/.agents/skills/`. | `.github/copilot-instructions.md`; `.github/instructions/**/*.instructions.md`; Copilot CLI also discovers `AGENTS.md`, `CLAUDE.md`, `.claude/CLAUDE.md`, and `GEMINI.md`, plus user-level instruction roots. | Project `.github/agents/`; user `~/.copilot/agents/`; Markdown agent profiles with YAML frontmatter. | `.github/prompts/*.prompt.md`. | Copilot CLI combines applicable instruction files and explicitly does **not** define one general precedence across them; conflicting instructions should be avoided. User agents override repository agents in Copilot CLI, while repository agent profiles override organization and enterprise profiles on GitHub. Support varies by Copilot surface/IDE. |
| **Gemini CLI** | Built-in, extension, user `~/.gemini/skills/` or `~/.agents/skills/`, then workspace `.gemini/skills/` or `.agents/skills/`. | Global `~/.gemini/GEMINI.md`; workspace/ancestor context; just-in-time nested context. The context filename is configurable and can include `AGENTS.md`. | Project `.gemini/agents/*.md`; user `~/.gemini/agents/*.md`; Markdown plus YAML frontmatter. | User `~/.gemini/commands/**/*.toml`; project `.gemini/commands/**/*.toml`; nested paths become colon-separated command names. | Skill precedence is built-in < extension < user < workspace; within user/workspace tiers, `.agents/skills/` beats `.gemini/skills/`. Project commands override same-named user commands. Context files are concatenated rather than reduced to one winner. |

### Evidence by harness

#### Pi

Pi’s first-party Skills documentation lists global, project, package, settings, and CLI sources; recursive `SKILL.md` discovery; project trust; validation; and duplicate-name behavior. It also documents the shared `.agents/skills/` alias and shows how users can explicitly include Claude or Codex skill directories. [Pi Skills](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/skills.md)

Pi’s Prompt Templates documentation defines the global/project paths, Markdown format, optional metadata, and non-recursive default scan. [Pi Prompt Templates](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/docs/prompt-templates.md)

The Pi README documents its context-file behavior and explicitly states that subagents are not built in. [Pi coding agent README](https://github.com/earendil-works/pi/blob/main/packages/coding-agent/README.md)

#### Claude Code

Claude Code documents skill paths, nested discovery, source precedence, symlink behavior, standard versus Claude-specific frontmatter, and the compatibility relationship between legacy commands and skills. [Claude Code Skills](https://code.claude.com/docs/en/skills)

Its memory documentation defines `CLAUDE.md`, `.claude/rules/`, hierarchy/load order, imports, symlinks, and the explicit `AGENTS.md` interoperability workaround. [Claude Code Memory](https://code.claude.com/docs/en/memory)

Its subagent documentation defines project/user agent roots, recursive discovery, frontmatter, and conflict handling. [Claude Code Subagents](https://code.claude.com/docs/en/sub-agents)

#### Codex

Codex’s Skills documentation defines the `.agents/skills/` repository and user roots, ancestor-chain discovery, required metadata, symlink behavior, and optional OpenAI-specific metadata. [Codex Skills](https://learn.chatgpt.com/docs/build-skills)

Codex’s instruction documentation defines global and project `AGENTS.md` lookup, overrides, configurable fallback names, and root-to-current-directory merge order. [Codex AGENTS.md](https://learn.chatgpt.com/docs/agent-configuration/agents-md)

Codex labels `~/.codex/prompts/*.md` custom prompts as deprecated and recommends skills for reusable/shared workflows. [Codex Custom Prompts](https://learn.chatgpt.com/docs/custom-prompts)

#### Cursor

Cursor’s Skills documentation defines its native and compatibility roots, recursive/nested project discovery, directory scoping, standard fields, Cursor extensions, and the local-versus-cloud distinction. [Cursor Skills](https://cursor.com/docs/skills)

Cursor’s Rules documentation defines `.mdc` files, activation metadata, `AGENTS.md`, nested precedence, and Team/Project/User rule handling. [Cursor Rules](https://cursor.com/docs/rules)

Cursor’s Subagents documentation defines project/user roots, Claude/Codex compatibility roots, frontmatter, and name-conflict precedence. [Cursor Subagents](https://cursor.com/docs/subagents)

#### GitHub Copilot

GitHub’s first-party documentation lists Copilot’s project and personal skill roots and identifies Agent Skills as an open standard. [About agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)

The customization reference lists repository instructions, path-specific instructions, prompt files, custom agents, skills, and hooks with their conventional paths. [Copilot customization cheat sheet](https://docs.github.com/en/copilot/reference/customization-cheat-sheet)

Copilot CLI’s instruction documentation lists user and repository roots, supported cross-harness instruction filenames, path-specific behavior, and the absence of a general precedence rule. [Copilot CLI custom instructions](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-custom-instructions)

#### Gemini CLI

Gemini CLI’s first-party Skills documentation defines discovery tiers, aliases, precedence, activation consent, and local management. [Gemini CLI Skills](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/skills.md)

Its context, custom-command, and subagent documentation define `GEMINI.md` hierarchy, configurable instruction filenames, TOML command roots/precedence, and Markdown agent roots/frontmatter. [GEMINI.md context](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/gemini-md.md), [Custom commands](https://github.com/google-gemini/gemini-cli/blob/main/docs/cli/custom-commands.md), [Subagents](https://github.com/google-gemini/gemini-cli/blob/main/docs/core/subagents.md)

### Other material candidates

Windsurf’s first-party documentation exposes Skills, `AGENTS.md`, rules/memories, and Markdown workflows as distinct customization families. It is a strong next adapter candidate, but its exact resolution semantics should be verified in a dedicated adapter ticket before claiming compatibility. [Windsurf Skills](https://docs.windsurf.com/windsurf/cascade/skills), [Windsurf AGENTS.md](https://docs.windsurf.com/windsurf/cascade/agents-md), [Windsurf Memories & Rules](https://docs.windsurf.com/windsurf/cascade/memories), [Windsurf Workflows](https://docs.windsurf.com/windsurf/cascade/workflows)

Cline maintains first-party repositories for the harness and a library explicitly covering rules, skills, workflows, and `AGENTS.md`. It is also a material follow-on candidate, but should not be marked supported until its current product documentation and precedence rules receive the same path-by-path verification. [Cline](https://github.com/cline/cline), [Cline rule and skill library](https://github.com/cline/clinerules)

## Interoperability constraints

1. **A matching filename is not proof of equivalent behavior.** Shared `SKILL.md` packages can contain host-only frontmatter or scripts requiring tools unavailable in another harness. Store the parsed portable fields, raw frontmatter, and a declared/observed dialect separately.
2. **Asset identity and placement must remain separate.** A symlinked skill can be one asset visible through several roots; copied skills without a stable identifier remain separate assets. Hosts also differ in whether they deduplicate symlink targets.
3. **Precedence is per harness and asset family.** Some hosts choose one winner, some retain duplicates, and instruction systems often concatenate content. Record `resolution = active | shadowed | merged | duplicate | unknown` only when an adapter has evidence for that host.
4. **Launch directory matters.** Codex, Claude Code, Pi, and Gemini all use some form of current-directory/ancestor discovery. A catalog scan from the repository root cannot assume it reproduces a harness launched from a nested package.
5. **Local and remote surfaces differ.** Cursor remote/cloud workers and Claude cloud sessions do not automatically inherit every user-level local skill. Copilot feature support varies among CLI, GitHub, and IDE surfaces. Compatibility claims therefore need a `surface` dimension.
6. **Trust is part of discoverability.** Pi, Codex, Claude Code, and other hosts gate at least some project resources behind trust or security behavior. “Present on disk” must not be displayed as “will load” without considering trust state.
7. **Reload behavior differs.** Some hosts watch skill files; others require a session restart or explicit reload. The catalog should report files, not promise immediate host uptake.
8. **Assets can execute or induce execution.** Skills can bundle scripts and agent/command files can invoke tools. V1’s read-only scanner should never execute, import, render active HTML from, or evaluate discovered content.

## Recommendation for v1

### Compatibility set

Implement **six first-party adapters**—Pi, Claude Code, Codex, Cursor, GitHub Copilot, and Gemini CLI—behind a shared standards layer:

1. **Agent Skills scanner** for standard `SKILL.md` packages and `.agents/skills/`, with adapter-added roots and host-specific validation.
2. **AGENTS.md scanner** for plain instructions, with adapter-owned traversal and precedence rules.
3. **Harness dialect scanners** for the documented v1 families:
   - Pi: skills, instructions, prompt templates.
   - Claude Code: skills, instructions/rules, agents, and legacy command files (marked legacy).
   - Codex: skills and instructions; deprecated custom prompts may be shown only with a deprecation badge.
   - Cursor: skills, rules/AGENTS.md, and agents; defer legacy command discovery until its filesystem contract is separately verified.
   - GitHub Copilot: skills, instructions, agents, and prompt files, tagged by Copilot surface where support differs.
   - Gemini CLI: skills, context instructions, agents, and TOML commands.

This set is justified by first-party documentation for every claimed path and covers every v1 asset family without pretending every harness supports every family.

Treat **Windsurf and Cline as named follow-on adapters**, not generic filesystem guesses. Their inclusion should graduate after a dedicated verification of current roots, metadata, precedence, and local/cloud behavior.

### Adapter boundary implied by the evidence

Each adapter should return facts, not mutate or execute assets:

- candidate roots and path patterns by OS, scope, and surface;
- traversal direction, recursion, nested scope, and symlink policy;
- parsed portable metadata plus untouched raw metadata;
- asset family and dialect;
- placement scope (`system`, `managed`, `user`, `workspace`, `directory`, `plugin/package`);
- harness/surface compatibility evidence;
- host-specific resolution status and reason;
- validation/deprecation/security warnings.

The shared catalog should own canonical-path identity, read limits, content hashing if later approved, normalized search fields, and the many-to-one Asset-to-Placement relationship. It should not own harness precedence rules.

## Decision questions surfaced

1. Should v1 display host-specific `active`, `shadowed`, and `merged` states, or list placements neutrally until the adapter contract proves effective resolution?
2. Should deprecated Claude command files and Codex custom prompts appear by default, behind a “legacy assets” filter, or not at all?
3. Is compatibility tracked only by harness, or by **harness surface** (for example Copilot CLI versus GitHub versus IDE; Cursor local versus cloud)?
4. Which host-specific skill frontmatter fields become normalized searchable fields, and which remain raw dialect metadata?
5. Should Windsurf and Cline be the next two adapters after the six-adapter v1 set, or should v1 trade one of the six for one of them?
