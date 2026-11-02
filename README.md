# fishwrap `state` branch

Archived output of the demo workflow (`.github/workflows/demo.yml` on `main`).
No code lives here. Each run of the workflow commits the day's edition under
`demo/vanilla/<YYYY-MM-DD>/`, rewrites `demo/vanilla/editions.html` (the index,
newest first) and `demo/vanilla/index.html` (a redirect to the newest edition),
then pushes. fishwrap.org serves the newest ninety days from this tree.

This branch shares no history with `main`. Never merge it anywhere.
