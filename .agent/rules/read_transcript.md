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
