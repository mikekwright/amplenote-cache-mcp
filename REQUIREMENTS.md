Amplenote cache MCP
===========================================

This is an mcp that was quickly setup for local usage as no mcp solution
for amplenote exists, and amplenote is just much better for task management
compared to notion.

Core Features
--------------------------------------------

Core features include:
* Ability to search all notes by name and content.
* Ability to search all tasks by description and get their duration, dates, urgent and important level.
* Ability to get the most recently modified notes.
* Ability to get the most recently modified tasks.
* Ability to get the most recent tasks and not have to be restarted.
* Ability to select tasks by the date they were created (stored in attrs JSON).
* Ability to select tasks ordered by their point values.
* Ability to filter tasks by priority flags (urgent, important, none, or both).

Development Requirements
-----------------------------------------------

The final solution must:
* Have unit tests to verify the flow
* Be able to target a different location for amplenote database.
* Be very idiomatic in the python code
* Support smaller functions and more modules to make the solution clean.

