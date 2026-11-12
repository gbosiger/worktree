# Planned Neovim integration

A developer can find, reference, edit, and advance live Markdown tickets from the editor. The toolkit remains usable without Neovim. Git publication, AI chat, and a new archive reader are outside this feature.

## Editor design

Sketch the completion menu, board tree, picker, and previews before building them. Specify minimum supported versions, plugin distribution, configurable commands/mappings, CLI discovery in a checkout and installed project, and a measurable responsiveness target. Select initial completion adapters (blink.cmp or nvim-cmp are candidates). Telescope and Neo-tree are optional and independent. Keep core list, selection, and lifecycle commands usable without either. The terminal list interface stays as documented.

## Board discovery

Resolve the board from the active buffer with an explicit root override. Keep caches separate across projects and linked worktrees. Read JSON-frontmatter Markdown as data, including groups. Expose ID, title, kind, status, parent, path, and preview. Define a stable read interface before depending on CLI output. Report missing boards, duplicate IDs, and malformed records while displaying other valid tickets.

Refresh asynchronously after saves, external creates/edits/moves/removals, successful commands, and manual refresh. Discard stale results. Re-resolve a selected ID to its current path before opening or changing it.

## Reference completion

Match ID fragments and title words in documented reference contexts and plugin command arguments, with manual invocation elsewhere. Rank matches consistently. Show ID, title, kind, and status, with parent and acceptance details in preview. Insert only the ID at the reference fragment and preserve the surrounding text and cursor. Parent and dependency prompts exclude known invalid selections. Ordinary prose can reference any live ticket.

## Tree navigation

Offer a Neo-tree source alongside existing sources and mappings. Show status lanes, optional groups, epics, and their children by status. Support keyboard navigation, search/filter, preview, open, and copy ID. Distinguish statuses and kinds using text, including in narrow windows. Show meaningful empty states. Preserve selection and expansion by ID after refresh, including when an item moves or disappears.

## Picker

Use the shared board model for Telescope list and action selection. Show ID, title, kind, and status, fuzzy-match ID/title, filter by status, and preview Markdown and parent context. Distinguish duplicate titles. Resolve moved selections by ID. Explain a missing result and refresh. Cancelling leaves the board and buffers untouched. An action picker returns the selected ID and board to the action handler. Load Telescope on demand.

## Ticket actions

Provide open, preview, copy ID, create, start, review, done, and reopen. Validate parent kind on creation. An explicit ID overrides the open buffer. A picker/tree action targets its selection. Otherwise use the current buffer's validated identity and board membership, including container READMEs. Prompt for selection or report an error on ambiguous, missing, stale, or edited identity.

Pass literal arguments to the project CLI asynchronously. Prompt for reviewer and evidence when required, and save affected unsaved buffers or cancel. Preserve CLI gates and unchecked criteria. Report stderr and exit failures. Reconcile open buffers after successful moves and leave failed edits recoverable. Never switch worktrees or publish implicitly.

## Verification

Use fixture boards and headless tests for missing tools, malformed data, duplicate titles, stale results, external moves, unsaved edits, rejected actions, cancellation, shell metacharacters, and separate worktrees. Measure responsiveness using the design target. Smoke-test supported editor and adapter versions with a real tree and picker. Walk through filtering to review, previewing and opening a ticket, and invoking done from its buffer, including a rejected gate. Document tested versions, checkout/install setup, optional mappings, refresh, and archive limitations.
