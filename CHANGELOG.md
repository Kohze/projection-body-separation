# Changes

## 1.0.1 - 9 October 2026

The optional external replay passed all mathematics on Linux, then encountered
a comparison failure caused solely by Windows CRLF versus Linux LF report
newlines. Normalize the wrapper's report bytes and supplied report to LF;
retain strict full-report hash comparison. Add a regression test covering
newline normalization, idempotence and preserved JSON values. There are now
ten unit tests. Update the manuscript and availability links to this patch.
No mathematical constants, geometry, recurrence certificate or prior inputs
change. The original v1.0.0 tag and assets remain available.

## 1.0.0 - 9 October 2026

Initial public manuscript, data and code edition with the discussion,
conclusion, requested companion-paper AI disclosure and 16 references.
