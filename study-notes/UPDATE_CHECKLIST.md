# Update checklist — keep the four study docs in step

The Acronyms and Basic Commands docs are copies of material in `CCNA.docx`, so they drift apart.
Use this list every time you add or change notes.

## After adding or changing notes in CCNA.docx
1. **New command?** Add it to `Basic_Configuration_Commands.docx` (same four columns: Command, Purpose, Description, Device).
2. **New acronym?** Add it to `Acronyms.docx`. In `CCNA.docx` an acronym appears in the first section that uses it only — do not repeat it in later sections.
3. **Exam reference changed?** Check the Review Status table (end of `CCNA.docx`) and the Coverage Tracker.
4. **Gap filled?** Update three places: the gap box, the Coverage Tracker row, and the "Still to add" line on the matching Domain Cheat Sheet (Part 19). Also add the new defaults to Part 15 and any new `show` command to Parts 14 and 16.
5. **Run the check:** `python3 study-notes/tools/check_docs_in_sync.py study-notes` (or point it at the folder where your copies live). It lists commands and acronyms that are in one doc but missing from the other. Fix anything in the first and third lists.
6. **Log it:** add the change to `CHANGELOG.md` (where, before, after) so it can be reverted.

## After a lab or practice question shows something is wrong
- Fix it in `CCNA.docx` first, then repeat steps 1–2 for any copy in the other docs.
- Put a tick in the "Lab-tested?" column of the Review Status table for that Part.

## Before you export to OneDrive
- Open `CCNA.docx` in Word, right-click the contents list → Update Field → Update entire table (page numbers move when you edit).
- Check the Review Status table still reflects reality.
