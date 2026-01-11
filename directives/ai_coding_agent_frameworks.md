# AI Coding Agent Frameworks: Comprehensive Analysis

> Deep research compilation on Claude Code (CLAUDE.md), Google Antigravity, and agentic coding best practices.

---

## Table of Contents

1. [Claude Code & CLAUDE.md Framework](#claude-code--claudemd-framework)
2. [Google Antigravity IDE Framework](#google-antigravity-ide-framework)
3. [Comparison & Integration Patterns](#comparison--integration-patterns)
4. [GitHub Resources & Solutions](#github-resources--solutions)
5. [Implementation Recommendations](#implementation-recommendations)

---

## Claude Code & CLAUDE.md Framework

### What is CLAUDE.md?

CLAUDE.md is a special configuration file that serves as your project's persistent memory for Claude. It is automatically loaded at the start of every conversation, becoming part of Claude's system prompt.

#### Key Characteristics

| Feature | Description |
|---------|-------------|
| **Persistent Context** | Automatically loaded, eliminating need to re-explain project basics |
| **Hierarchical Loading** | Merges from enterprise → user (`~/.claude/CLAUDE.md`) → project (`./CLAUDE.md`) → subdirectories |
| **Nested Support** | Subdirectory files (e.g., `tests/CLAUDE.md`) loaded when working in those areas |
| **Living Document** | Built organically using `#` key to add frequently-repeated instructions |

### Best Practices for CLAUDE.md

#### Optimal Structure

```markdown
# Project Name

## Overview/Purpose
Brief description of what the project does

## Tech Stack
- Languages: Python 3.10, TypeScript 5.3
- Frameworks: FastAPI, React 18
- Tools: Docker, PostgreSQL

## Project Structure
- `/src` - Source code
- `/tests` - Test files
- `/execution` - Deterministic scripts
- `/directives` - SOPs and instructions

## Code Style & Conventions
- Formatting standards
- Naming conventions
- Error handling patterns

## Important Commands
- Build: `npm run build`
- Test: `npm test`
- Lint: `eslint .`

## Key Patterns & Decisions
- Architectural choices and rationale
- Common patterns to follow

## Important Warnings
- Project-specific gotchas
- Common mistakes to avoid
```

#### Sizing Guidelines

| Metric | Recommendation |
|--------|----------------|
| **Optimal Length** | 60-300 lines maximum |
| **Instruction Complexity** | LLMs follow ~150-200 instructions reliably |
| **Token Efficiency** | Shorter files = lower cost per conversation |

#### What NOT to Include

- Don't use Claude as a linter (use actual linters)
- Avoid auto-generation; craft manually for best results
- Don't include all information—use progressive disclosure
- Point to relevant files/docs instead of duplicating content

### The 3-Layer Architecture Pattern

This pattern separates probabilistic LLM work from deterministic execution:

```
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 1: DIRECTIVE                       │
│  (What to do)                                               │
│  • SOPs in Markdown at /directives/                         │
│  • Define goals, inputs, tools, outputs, edge cases         │
│  • Natural language instructions                            │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                  LAYER 2: ORCHESTRATION                     │
│  (Decision making - The LLM)                                │
│  • Read directives, call tools in order                     │
│  • Handle errors, ask for clarification                     │
│  • Update directives with learnings                         │
│  • Glue between intent and execution                        │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    LAYER 3: EXECUTION                       │
│  (Doing the work)                                           │
│  • Deterministic Python scripts at /execution/              │
│  • API calls, data processing, file operations              │
│  • Environment variables in .env                            │
│  • Reliable, testable, fast                                 │
└─────────────────────────────────────────────────────────────┘
```

**Why this works**: 90% accuracy per step = 59% success over 5 steps. Pushing complexity into deterministic code keeps LLM focused on decision-making.

### Claude Code File Organization

```
project/
├── CLAUDE.md                    # Root project instructions
├── .claude/
│   ├── commands/                # Slash commands (.md files)
│   │   ├── fix-issue.md        # → /fix-issue
│   │   └── security-review.md  # → /security-review
│   ├── agents/                  # Subagent definitions
│   │   ├── code-reviewer.md
│   │   └── test-writer.md
│   └── skills/                  # Skill definitions
├── directives/                  # SOPs and workflows
├── execution/                   # Deterministic scripts
├── .tmp/                        # Intermediate files
└── tests/
    └── CLAUDE.md               # Test-specific instructions
```

### Subagent Configuration

Subagents are specialized AI assistants placed in `.claude/agents/`:

```yaml
---
name: code-reviewer
description: Reviews code for quality, security, and best practices
tools: Read, Grep, Glob
---

You are an expert code reviewer specializing in:
- Security vulnerability detection
- Performance optimization
- Code maintainability

## Review Checklist
1. Check for security vulnerabilities (OWASP Top 10)
2. Verify error handling patterns
3. Assess code complexity and readability
4. Validate naming conventions
5. Review test coverage

## Communication Protocol
- Be specific with line numbers
- Suggest concrete improvements
- Prioritize issues by severity
```

#### Tool Assignments by Agent Type

| Agent Type | Tools |
|------------|-------|
| Read-only (reviewers) | `Read, Grep, Glob` |
| Research agents | `Read, Grep, Glob, WebFetch, WebSearch` |
| Code writers | `Read, Write, Edit, Bash, Glob, Grep` |
| Documentation | `Read, Write, Edit, Glob, Grep, WebFetch` |

### Slash Commands

Create `.md` files in `.claude/commands/`:

```yaml
---
description: "Fix a GitHub issue"
allowed-tools: ["bash", "grep", "read", "edit"]
argument-hint: "issue number"
model: "claude-sonnet-4-20250514"
---

# Fix GitHub Issue $ARGUMENTS

1. Fetch issue details from GitHub
2. Analyze the problem
3. Implement the fix
4. Write tests
5. Create commit with descriptive message
```

### Self-Annealing Loop

When errors occur:

```
Error Detected
     ↓
1. Read error message and stack trace
     ↓
2. Fix the script/code
     ↓
3. Test the fix
     ↓
4. Update directive with learnings
     ↓
System is now stronger
```

---

## Google Antigravity IDE Framework

### Overview

Google Antigravity is an AI-powered IDE announced November 18, 2025 alongside Gemini 3. It enables developers to delegate complex coding tasks to autonomous AI agents.

| Aspect | Detail |
|--------|--------|
| **Release** | November 18, 2025 (public preview) |
| **Base** | Fork of VS Code (via Windsurf) |
| **Cost** | Free with rate limits |
| **Primary Model** | Gemini 3 Pro, Deep Think, Flash |
| **Additional Models** | Claude Sonnet 4.5, Claude Opus 4.5, GPT-OSS-120B |

### Three-Surface Architecture

Antigravity gives agents three command surfaces:

```
┌─────────────────────────────────────────────────────────────┐
│                       EDITOR SURFACE                        │
│  • Familiar IDE interface (VS Code-like)                    │
│  • AI-powered tab completions                               │
│  • Inline commands and suggestions                          │
│  • Agent sidebar for interaction                            │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      TERMINAL SURFACE                       │
│  • Shell command execution                                  │
│  • Dev server management                                    │
│  • Build and test automation                                │
│  • Environment interaction                                  │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│                      BROWSER SURFACE                        │
│  • Chrome integration                                       │
│  • UI verification and testing                              │
│  • Screenshot capture                                       │
│  • E2E test execution                                       │
└─────────────────────────────────────────────────────────────┘
```

### Two Primary Views

#### 1. Editor View
Standard IDE interface with agent sidebar—similar to Cursor or GitHub Copilot but with deeper agent integration.

#### 2. Manager View
Mission Control dashboard for orchestrating multiple agents:
- Spawn, monitor, and interact with multiple agents
- Asynchronous task execution
- Parallel agent workflows
- High-level project orchestration

**Example**: Dispatch 5 agents to work on 5 bugs simultaneously, multiplying throughput.

### Configuration System

#### Global Rules (`~/.gemini/GEMINI.md`)
```markdown
# Global Development Rules

## Code Style
- Use TypeScript strict mode
- Prefer functional programming patterns
- Maximum function length: 50 lines

## Security
- Never commit secrets
- Validate all external inputs
- Use parameterized queries
```

#### Workspace Rules (`.antigravity/rules.md`)
Project-specific rules that override/supplement global:
```markdown
# Project-Specific Rules

## Architecture
- Use Repository pattern for database access
- All API endpoints must be versioned
- Use Tailwind CSS for styling

## Testing
- Minimum 80% code coverage
- E2E tests for all user flows
```

### Workspace Template Structure

```
project/
├── src/
│   ├── agent.py           # Primary agent execution loop
│   ├── memory.py          # JSON-based memory management
│   ├── mcp_client.py      # Model Context Protocol integration
│   ├── swarm.py           # Multi-agent coordination
│   ├── agents/            # Specialist implementations
│   └── tools/             # Custom Python function tools
├── .context/              # Knowledge base auto-injection
├── .antigravity/          # IDE context rules
├── .cursorrules           # IDE directives
├── artifacts/             # Task outputs and evidence
└── mcp_servers.json       # External tool connections
```

### Artifacts System

Antigravity creates Artifacts to communicate work and enable feedback:

- Rich markdown files
- Architecture diagrams
- Images and screenshots
- Browser recordings
- Code diffs

**Purpose**: Solve the "Trust Gap" between agent actions and human understanding.

### Performance Benchmarks

| Metric | Antigravity | Cursor 2.0 |
|--------|-------------|------------|
| Next.js + Supabase feature | 42s | 68s |
| 100k+ line codebase navigation | 40% faster | baseline |
| Refactoring accuracy | 94% | 78% |
| SWE-bench Verified | 76.2% | — |

### Multi-Agent Orchestration Patterns

```python
# Router-Worker Pattern
from src.swarm import SwarmOrchestrator

swarm = SwarmOrchestrator()
result = swarm.execute("Build and review a calculator")
# Routes to: Coder → Reviewer → Researcher → Synthesis
```

| Pattern | Description |
|---------|-------------|
| **Sequential** | Agent A → Agent B → Agent C → Result |
| **Parallel** | Multiple agents simultaneously, merge results |
| **Conditional** | Dynamic routing based on analysis |
| **Review & Validation** | Primary → Review → Final |

### MCP Server Configuration

```json
{
  "servers": [{
    "name": "github",
    "transport": "stdio",
    "command": "npx",
    "args": ["-y", "@modelcontextprotocol/server-github"],
    "enabled": true
  }]
}
```

---

## Comparison & Integration Patterns

### Framework Comparison

| Aspect | Claude Code | Google Antigravity |
|--------|-------------|-------------------|
| **Philosophy** | Terminal-native, minimal | Visual IDE, agent-first |
| **Configuration** | CLAUDE.md (Markdown) | GEMINI.md + rules.md |
| **Subagents** | `.claude/agents/` | Built-in agent manager |
| **Multi-model** | Claude-focused | Multi-provider |
| **Browser Control** | Limited (WebFetch) | Native Chrome integration |
| **Async Workflows** | Manual orchestration | Native Manager view |
| **Cost** | Per-token usage | Free (rate-limited) |

### Unified Configuration Pattern

For projects supporting both:

```
project/
├── CLAUDE.md               # Claude Code instructions
├── AGENTS.md               # Mirrored for other systems
├── GEMINI.md               # Mirrored for Antigravity
├── .claude/
│   ├── agents/             # Claude subagents
│   └── commands/           # Claude slash commands
├── .antigravity/
│   └── rules.md            # Antigravity-specific rules
├── .context/               # Shared knowledge base
├── directives/             # Shared SOPs
└── execution/              # Shared deterministic scripts
```

---

## GitHub Resources & Solutions

### Essential Repositories

#### Claude Code Ecosystem

| Repository | Description | Link |
|------------|-------------|------|
| **awesome-claude-code** | Curated commands, files, workflows | [GitHub](https://github.com/hesreallyhim/awesome-claude-code) |
| **awesome-claude-code-subagents** | 100+ specialized subagents | [GitHub](https://github.com/VoltAgent/awesome-claude-code-subagents) |
| **agents** | 99 agents + 15 orchestrators | [GitHub](https://github.com/wshobson/agents) |
| **awesome-claude-agents** | Orchestrated dev team | [GitHub](https://github.com/vijaythecoder/awesome-claude-agents) |
| **claude-code-best-practices** | Best practices & examples | [GitHub](https://github.com/awattar/claude-code-best-practices) |

#### Google Antigravity Ecosystem

| Repository | Description | Link |
|------------|-------------|------|
| **antigravity-workspace-template** | Starter kit for Antigravity | [GitHub](https://github.com/study8677/antigravity-workspace-template) |

### Subagent Categories (100+ Available)

1. **Core Development** (11): API designer, backend, frontend, fullstack, mobile
2. **Language Specialists** (26): TypeScript, Python, Java, Rust, Go, C++, etc.
3. **Infrastructure** (14): DevOps, Kubernetes, Terraform, cloud architecture
4. **Quality & Security** (12): Code review, testing, penetration testing
5. **Data & AI** (12): ML, MLOps, NLP, data engineering
6. **Developer Experience** (13): Build systems, CLI tools, documentation
7. **Specialized Domains** (12): Blockchain, game dev, IoT, fintech
8. **Business & Product** (10): PM, project coordination, technical writing
9. **Meta & Orchestration** (9): Multi-agent coordination, workflows
10. **Research & Analysis** (6): Competitive analysis, trend forecasting

---

## Implementation Recommendations

### For New Projects

1. **Start with `/init`** command to generate baseline CLAUDE.md
2. **Refine manually**—don't rely solely on auto-generation
3. **Build organically** using `#` key during sessions
4. **Keep under 300 lines**—prefer progressive disclosure

### For Existing Projects

1. **Audit current workflows** and identify repetitive instructions
2. **Create directives** for complex, multi-step processes
3. **Extract execution scripts** for deterministic operations
4. **Set up subagents** for specialized tasks

### Self-Annealing Checklist

When something breaks:
- [ ] Read error message and stack trace
- [ ] Fix the script
- [ ] Test the fix (check if paid API before auto-retry)
- [ ] Update directive with learnings
- [ ] Document edge cases discovered

### Recommended Directory Structure

```
project/
├── CLAUDE.md                    # 60-300 lines, human-readable
├── .claude/
│   ├── agents/                  # Specialized subagents
│   ├── commands/                # Slash commands
│   └── skills/                  # Deep behavioral guidance
├── directives/                  # SOPs and workflows
│   ├── api-integration.md
│   ├── testing.md
│   └── deployment.md
├── execution/                   # Deterministic Python scripts
│   ├── scrape_website.py
│   ├── process_data.py
│   └── deploy.py
├── .tmp/                        # Intermediate files (gitignored)
├── .env                         # Environment variables
└── tests/
    └── CLAUDE.md               # Test-specific instructions
```

---

## Sources

### Official Documentation
- [Claude Code: Best practices for agentic coding](https://www.anthropic.com/engineering/claude-code-best-practices)
- [Building agents with the Claude Agent SDK](https://www.anthropic.com/engineering/building-agents-with-the-claude-agent-sdk)
- [Google Developers Blog: Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)
- [Google Codelabs: Getting Started with Antigravity](https://codelabs.developers.google.com/getting-started-google-antigravity)

### Community Resources
- [Writing a good CLAUDE.md - HumanLayer](https://www.humanlayer.dev/blog/writing-a-good-claude-md)
- [Claude Agent Skills Deep Dive](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)
- [Google Antigravity: Agentic IDE - Index.dev](https://www.index.dev/blog/google-antigravity-agentic-ide)
- [Antigravity First Impressions - PromptLayer](https://blog.promptlayer.com/google-antigravity-first-impressions-of-the-agent-first-ide/)

### GitHub Repositories
- [awesome-claude-code](https://github.com/hesreallyhim/awesome-claude-code)
- [awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)
- [agents](https://github.com/wshobson/agents)
- [antigravity-workspace-template](https://github.com/study8677/antigravity-workspace-template)

---

*Last updated: January 2026*
