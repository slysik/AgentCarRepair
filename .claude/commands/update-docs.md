---
allowed-tools: WebFetch, Write, Edit, mcp__firecrawl__firecrawl_scrape
description: Update ai_docs directory with latest Anthropic documentation
argument-hint: [page-name] | all
---

# Update AI Documentation

You are tasked with updating the `ai_docs/` directory with the latest content from Anthropic's official Claude Code documentation.

## Your Process

1. **Fetch the latest documentation** from https://docs.anthropic.com/en/docs/claude-code/ for the requested page
2. **Extract clean markdown content** from the official docs
3. **Update the corresponding file** in `ai_docs/` directory
4. **Add update metadata** including source URL and timestamp

## Available Pages to Update

- `hooks` -> `ai_docs/cc_hooks_docs.md`
- `subagents` -> `ai_docs/anthropic_docs_subagents.md`
- `slash-commands` -> `ai_docs/anthropic_custom_slash_commands.md`
- `output-styles` -> `ai_docs/anthropic_output_styles.md`
- `quick-start` -> `ai_docs/anthropic_quick_start.md`

## Instructions

**Arguments provided**: $ARGUMENTS

If $ARGUMENTS is "all", update all documentation pages.
If $ARGUMENTS is a specific page name, update only that page.
If no arguments, ask the user which page to update.

For each page:
1. Use WebFetch or Firecrawl to get the latest content from `https://docs.anthropic.com/en/docs/claude-code/[page-name]`
2. Clean and format the content appropriately
3. Add a header with update metadata:
   ```markdown
   # [Page Title]
   
   > Updated from Anthropic's official documentation
   > Source: [URL]
   > Last updated: [ISO timestamp]
   
   [Content...]
   ```
4. Update the corresponding file in `ai_docs/`
5. Report what was updated

Always backup existing files before overwriting them.