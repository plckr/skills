# Agent skills

A personal-first collection of reusable agent skills, shared publicly. Original skills and modified upstream skills live side by side in `skills/`.

This repository is being set up; no skills are published yet. The installation commands below become useful once skills have been added and pushed.

## Install

Use the existing [skills CLI](https://github.com/vercel-labs/skills) with Node.js and Git installed. No custom installer is needed.

```bash
# Discover available skills without installing
npx skills add plckr/skills --list

# Select skills and agents interactively (project-local by default)
npx skills add plckr/skills

# Or install for your user, across projects
npx skills add plckr/skills --global
```

Choose a subset on each machine; machines do not have to share the same selection. The CLI handles supported agents' installation locations, including Pi. Installation compatibility does not make tool-specific instructions portable.

## Update and recover

Normal installations follow this repository's default branch, `main`. Updates are explicit; there are no releases or per-skill versions for now.

```bash
# Check for available updates (exit code 1 means updates exist)
npx skills check

# Update user-wide skills
npx skills update --global

# Or update project-local skills
npx skills update --project
```

These update commands affect all installed skills in that scope, including other collections. To update only a particular skill, add its name: `npx skills update <skill-name> --global`.

Installed skills are disposable deployments, not working copies. **Updates can overwrite local edits.** Make changes in a Git checkout of this repository, commit and push them, then update installations. Never store credentials or machine-specific configuration in a shared skill.

For a frozen snapshot or recovery to a known revision, reinstall selected skills from a full 40-character commit SHA:

```bash
npx skills add plckr/skills#<full-commit-sha> --global
```

A commit-pinned installation remains pinned during updates. To follow `main` again, reinstall from `plckr/skills` without the SHA. Keep scope and agent choices consistent when reinstalling; do not assume updates preserve every agent or copy-mode preference. This is manual recovery, not an automatic rollback system.

## Add a skill

Every skill has its own directory directly inside `skills/`. Do not create separate categories for original and forked skills.

```text
skills/
├── code-review/
│   └── SKILL.md
└── debugging/
    ├── SKILL.md
    ├── UPSTREAM.md    # Only for a fork
    └── LICENSE        # Preserved upstream license
```

Start with `skills/<skill-name>/SKILL.md`:

```markdown
---
name: skill-name
description: Describe what this skill does and when an agent should use it.
---

# Skill name

Write actionable instructions for the agent here.
```

- Use a unique lowercase name with single hyphens, matching its directory (maximum 64 characters).
- Keep `description` a nonempty string, at most 1,024 characters.
- Add `scripts/`, `references/`, or `assets/` inside a skill only when needed. Use relative Markdown links for local resources.
- Prefer portable instructions. Explicitly document any agent-specific tools, dependencies, permissions, or platform assumptions.
- Do not include secrets, absolute machine paths, or generated installations.
- Before merging, manually review instruction quality, safety, and behavior in the relevant agent. Structural checks cannot prove that a skill works.

### Modified upstream skills

Keep forks beside original skills. Preserve upstream license files and copyright notices, and check that redistribution and modification are permitted before adding a fork.

Include an `UPSTREAM.md` in each fork with:

- Original repository URL and skill path.
- Full upstream commit SHA used as the starting point.
- Applicable license and attribution.
- Why it was forked and what changed.

Review and merge upstream improvements deliberately. Collection updates install our maintained versions; they do not automatically merge changes from original authors.

## Validate locally

Python 3.11+ is required for repository checks, not for installing the collection.

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r scripts/requirements.txt
.venv/bin/python -m unittest discover -s tests
.venv/bin/python scripts/validate_skills.py
```

Validation checks YAML metadata, unique names, the flat directory layout, and local Markdown link/image targets in the README and skill documentation. Link checks verify files and directories, not heading fragments, external URLs, or raw HTML. GitHub Actions runs the same checks on pushes and pull requests.

## License

Original work is [MIT licensed](LICENSE). Third-party material remains subject to its own license and attribution; the root license does not override those terms.
