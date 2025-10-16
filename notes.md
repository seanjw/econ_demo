# Claude Code Primer: Essential Commands & Best Practices

## Installation Guide

### Prerequisites
- **Node.js**: Version 20 or later required
- **npm**: Comes with Node.js (or use yarn/pnpm)
- **Operating System**: Works on macOS, Linux, and Windows (WSL recommended)
- **Anthropic Account**: You'll need to authenticate on first use

### Installation Methods

```bash
# Install Claude Code globally
npm install -g @anthropic-ai/claude-code
 --version
```

---

## 1. Referencing Files and Agents

### File References
Claude Code can access and modify files in your project directory and subdirectories.

```bash
# Reference specific files in your prompts
claude "Review the authentication logic in src/auth/login.js"

# Reference multiple files
claude "Compare the implementations in server.js and client.js"

# Use relative paths from your working directory
claude "Update all TypeScript files in ./components"
```

---

## 3. Clearing Context

The `/clear` command resets Claude's context window, essential for managing long sessions and improving performance.

### When to Clear Context
- Between different tasks to reset the context window
- After completing a major feature or section
- When Claude seems to be losing track of the conversation
- Before starting unrelated work

### How to Use
```bash
# Within a Claude session
/clear

# Or press Escape to interrupt and clear
```

### Strategic Context Management
For large tasks with multiple steps, improve performance by having Claude use a Markdown file as a checklist and working scratchpad:

```bash
claude "Create a file called progress.md to track our work, then let's refactor the authentication system step by step"
```

---

## 4. Compacting Context

Context compacting helps Claude maintain focus on relevant information while working on long tasks.

### Automatic Compacting
Claude automatically compacts context when approaching limits, but you can optimize this process.

### Manual Strategies
1. **Use checkpoint files**: Save state to markdown files
2. **Summarize progress**: Ask Claude to summarize before continuing
3. **Extract key information**: Move important details to reference files

### Example Workflow
```bash
# Start with a plan file
claude "Create implementation-plan.md with our architecture decisions"

# Work through tasks, referencing the plan
claude "Following implementation-plan.md, complete step 1"

# Periodically compact
claude "Summarize our progress in progress-summary.md, then continue with step 2"
```

---

## 5. MCP Servers (Model Context Protocol)

MCP allows Claude Code to reach beyond your local terminal and interact with external services.

### What MCP Servers Provide
- Access to external APIs and databases
- Browser automation (Playwright, Puppeteer)
- Documentation retrieval (Context7)
- Custom integrations with your tools

### Adding MCP Servers

#### Global Configuration
```bash
# Add a server globally
claude mcp add <server-name> <command>

# Example: Add Context7 for documentation
claude mcp add --transport http context7 https://mcp.context7.com/mcp \
  --header "CONTEXT7_API_KEY: YOUR_API_KEY"

# List active servers
claude mcp list
```

#### Project-Level Configuration
Create `.mcp.json` in your project root:
```json
{
  "mcpServers": {
    "playwright": {
      "command": "npx",
      "args": ["-y", "@mcp/playwright-server"]
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@mcp/github-server"],
      "env": {
        "GITHUB_TOKEN": "your-token"
      }
    }
  }
}
```

### Using MCP Servers
```bash
# Reference servers in your prompts
claude "Use context7 to get the latest Next.js authentication patterns"
claude "Use the playwright server to test our checkout flow"
```

---

## 6. Asking for Checklists and Testing

### Creating Comprehensive Checklists

Claude Code excels at breaking down complex tasks into manageable checklists.

#### Request Templates
```bash
# For feature implementation
claude "Create a detailed checklist for implementing user authentication with JWT tokens"

# For debugging
claude "Generate a debugging checklist for our performance issues"

# For testing
claude "Create a comprehensive test checklist for our API endpoints"
```

### Testing Workflows

#### Write Tests First
```bash
claude "Write failing tests for the shopping cart feature, then implement the code to make them pass"
```

#### Fix Existing Test Suites
```bash
# With permission prompts
claude "Run all tests, identify failures, and fix them one by one"

# Automated (dangerous mode)
claude --dangerously-skip-permissions "Fix all failing tests in the test suite"
```

#### Test-Driven Refactoring
```bash
claude "Create a refactoring checklist for the payment module, write tests for each step, then execute the refactoring"
```

### Best Practices for Checklists
1. **Be specific**: "Create a 10-step checklist for migrating from REST to GraphQL"
2. **Include validation**: "Add verification steps after each major change"
3. **Track progress**: Use markdown files with checkboxes
4. **Group related items**: Organize by feature, priority, or complexity

### Example: Complete Testing Workflow
```bash
# 1. Create test plan
claude "Create test-plan.md with comprehensive test scenarios for our e-commerce checkout"

# 2. Generate test files
claude "Following test-plan.md, create unit tests for each component"

# 3. Run and track
claude "Run all tests and update test-plan.md with results"

# 4. Fix failures systematically
claude "Fix failing tests one by one, updating test-plan.md as we go"
```

---

## Pro Tips & Common Patterns

### 1. The "YOLO Mode" Pattern
Containerize Claude, write failing tests for your most tedious task, flip on YOLO mode, and go to bed:
```bash
# In a container
docker run -it your-container
claude --dangerously-skip-permissions "Fix all ESLint errors and prettier formatting issues"
```

### 2. Iterative Development
```bash
# Use continue flag for ongoing work
claude -c  # Continue last conversation
claude --resume <session-id>  # Resume specific session
```

### 3. Headless Automation
```bash
# For CI/CD integration
claude -p "Run tests and fix any failures" \
  --dangerously-skip-permissions \
  --output-format json
```

### 4. Model Selection
```bash
# Within Claude session
/model opus-4.1  # Best for complex architecture
/model sonnet-4  # Balanced speed and quality

# Or use opusplan mode for best of both worlds
```

---

## Safety Reminders

1. **Default is Safe**: Claude uses read-only permissions by default
2. **Explicit Approval**: Every action requires permission unless using dangerous mode
3. **Isolation is Key**: When using `--dangerously-skip-permissions`, always isolate
4. **Backup Everything**: Maintain comprehensive backups before automated runs
5. **Start Small**: Test on non-critical tasks first

---

## Quick Command Reference

```bash
# Basic commands
claude                           # Start interactive session
claude "prompt"                  # One-shot command
claude -c                        # Continue last session
claude --resume <id>             # Resume specific session

# Permissions
claude --dangerously-skip-permissions  # Skip all prompts
claude config get allowedTools         # View permissions

# Context management
/clear                          # Clear context (in session)
/model <model-name>             # Switch models

# MCP servers
claude mcp list                 # List servers
claude mcp add <name> <cmd>     # Add server
claude --mcp-config .mcp.json   # Use project config

# Information
claude/doctor                   # Diagnose issues
/help                          # Show help (in session)
```

---

## Getting Started Checklist

- [ ] Check prerequisites (Node.js v20+, npm)
- [ ] Install Claude Code (see Installation Guide above)
- [ ] Run initial setup: `claude`
- [ ] Verify with `claude/doctor`
- [ ] Configure permissions for your workflow
- [ ] Set up MCP servers if needed
- [ ] Create a test project to practice
- [ ] Try the dangerous flag in a safe environment
- [ ] Develop your own patterns and workflows

---

*Remember: Claude Code is most powerful when you give it clear context, break down complex tasks, and use the right tools for each job. Start conservatively and expand your usage as you build confidence.*