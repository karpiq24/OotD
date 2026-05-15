---
trigger: always_on
---

# Rule: Always Read Full Transcript

## Trigger
This rule applies whenever the task involves reading a transcript file (e.g., `transcript.txt`, `transcript.json`) or any long text file that serves as the source material for summarization, analysis, or extraction.

## Action
When providing a summary, recap, or extraction from a transcript:

1. **Read EVERYTHING**: You MUST read the **entire** content of the file. Do not stop after the first view.
2. **Handle Pagination**: Use the `view_file` tool repeatedly, incrementing `StartLine` (e.g., 1-800, 801-1600, 1601-2400...) until you reach the end of the file.
3. **Verify Completeness**: Ensure you have consumed every line of dialogue before generating any output.
4. **Context Integrity**: Narrative details are often distributed throughout the session. Truncated reading leads to hallucinations and missed events. NEVER skip the middle or end of the file.

## Exception — rpg-summarizer skill (chunked subagent mode)

When the `rpg-summarizer` skill is active, the **main/orchestrating agent** must NOT pre-load the full transcript. Loading the entire transcript into the orchestrator's context defeats the purpose of chunk isolation.

The orchestrator should instead:
1. Determine total line count (e.g., via `wc -l`).
2. Scan for proper names — a grep or a light read of the file is sufficient; no need to hold all dialogue in context.
3. Delegate chunked reading to subagents.

Each **chunk subagent** must still follow this rule for its own slice: read the assigned line range completely before generating narrative output. Do not skip lines within the chunk.
