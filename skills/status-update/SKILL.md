---
name: status-update
description: Give a succinct, high-level progress update when the user asks for status during an ongoing task.
---

# Status update

Briefly explain where the work stands:

- What is complete.
- What is happening now and what remains.
- Any blocker or decision that needs the user's attention.

Lead with the overall state. Use a short paragraph or a few compact bullets. Translate implementation details into meaningful outcomes; omit file lists, command logs, and minor steps unless they explain a blocker.

Use existing context and lightweight checks when needed. Avoid delaying the update for extensive investigation. Distinguish verified results from work still being tested. Do not invent percentages or completion estimates.

During an active task, give the update in commentary, then continue the authorized work unless the user asks to pause or stop. A status request does not cancel the task.
