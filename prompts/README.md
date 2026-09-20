# Frozen prompt protocols

These files are the exact system prompts used for the three protocols reported
in the paper:

- `direct.txt`: shared task, input boundary, and Boolean output contract;
- `robust.txt`: Direct plus explicit prompt-injection defense guidance;
- `ours.txt`: Robust plus ordered injection assessment and auxiliary fields.

The email itself is supplied separately as the user message in the serialized
format implemented by `src/phishbench/prompts.py`. Unit tests verify that the
three files remain byte-for-byte equivalent to the runtime prompt builder.
