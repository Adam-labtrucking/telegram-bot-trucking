# Second Brain

One place for all life and business admin: contracts, lease agreements, insurance,
permits, notes, PDFs — absolutely everything. Drop files in, and this system (or a
Claude session pointed at this folder) keeps it organized and findable.

## How it works — the 30-second version

1. **Drop everything into `00-inbox/`.** Don't think about where it goes. Scans,
   PDFs, photos of paperwork, random notes — all of it lands in the inbox.
2. **File it later** (or ask Claude to). Each item moves from the inbox into the
   right numbered folder below and gets a row in [`INDEX.md`](INDEX.md).
3. **Find things by reading `INDEX.md`** — it's the master catalog. One line per
   document: what it is, where it lives, and the dates that matter (renewals,
   expirations, deadlines).

## Folder map

| Folder | What goes in it |
|---|---|
| `00-inbox/` | Everything, before it's filed. The only folder you need to remember. |
| `10-contracts/` | Broker/carrier agreements, rate confirmations, customer contracts, service agreements. |
| `20-insurance/` | Policies, certificates of insurance, claims, accident-related paperwork. |
| `30-compliance/` | DOT/MC authority, IFTA, UCR, IRP, permits, drug & alcohol consortium, driver qualification files. |
| `40-vehicles/` | Truck/trailer titles, registrations, lease agreements, maintenance and inspection records. |
| `50-finance/` | Factoring agreements, bank documents, taxes, invoices, receipts. |
| `60-legal/` | Property leases, disputes, legal correspondence, anything with a lawyer's name on it. |
| `70-personal/` | Personal life admin — anything that isn't the business. |
| `90-notes/` | Free-form notes, ideas, meeting notes, research. Use `_templates/note.md`. |
| `_templates/` | Templates for notes and filing. |

## Filing rules

- **File naming:** `YYYY-MM-DD_who_what.ext` — e.g.
  `2026-08-01_progressive_liability-policy.pdf`,
  `2026-07-15_tql_rate-confirmation.pdf`. The date is the document's date, not
  the day you filed it.
- **Every filed document gets an INDEX.md row.** No row, not filed.
- **Dates that expire go in the index's "Key dates" column** — insurance
  renewals, permit expirations, lease end dates. That column is what you (or
  Claude) scan to catch renewals before they lapse.
- **When in doubt, inbox.** A document sitting in `00-inbox/` beats a document
  lost in email.

## Using this with Claude

Point a Claude session at this folder and ask things like:

- "File everything in the inbox" — Claude renames, moves, and indexes each item.
- "What insurance is expiring in the next 90 days?" — Claude reads `INDEX.md`.
- "Summarize the lease agreement for truck 12" — Claude finds and reads the PDF.
- "Start a note about the new broker" — Claude uses `_templates/note.md`.

## Privacy note

This folder lives in a git repository. Anything committed here is pushed to
GitHub — fine for a private repo you control, but think twice before filing
documents with SSNs, full account numbers, or medical records. Redact first, or
keep those in an untracked local folder.
