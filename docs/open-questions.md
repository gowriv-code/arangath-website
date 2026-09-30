# Open questions and things to confirm (PR description)

## Missing from the handoff pack
- **Mockup exports** (`design-reference/mockup/` contained only a "put exports here" note). I built from BRIEF.md, the design tokens and the old site's copy. Every place the brief says "copy as in the mockup" (service cards, detail-page "What we model / What you receive" lists, Why Arangath cards, page intros) is **my draft copy**. Please compare against the mockup and paste in the verbatim text.
- `design-reference/arangath-4-pages.pdf` is a light-theme reference of an older layout; I used it for structure only.
- "Existing BIM images": the old site had no separate image files, only the three inline project SVG models and one hero photo. The three inline models are saved in `assets/projects/*-bim.svg` and shown under each live model. The old hero photo is kept as `assets/images/bim-coordination.jpg` but is not used on any page.

## For Vish to confirm (Kerala models and facts)
- All three live models are generic: unit counts and layout are illustrative. Specifically confirm or correct: bridge shown as 8 bays (real structure has 70 gates); rural scheme elements (intake, one treatment unit, one elevated reservoir, mains, 6 sample houses); 100 MLD works shows 3 clarifiers, a 10-cell filter house (the old site text says 24 filter beds), one clear water reservoir, pump house, chemical house, admin.
- The bridge model has no pipework, so its third layer toggle is **Water** instead of **Pipework**.
- Project facts and descriptions on the three project pages are the old site's text verbatim (including the 38 km saving, "thousands of hectares", "24 filter beds", "Government of India", "Kollam Corporation"). Confirm they are still approved for publication.
- Live 20 MLD card: no client, location or scope beyond "20 MLD water treatment plant currently in delivery" (LCGC and Rajahmundry not named, per the brief).
- Design consulting service line: the old site did not list it. The three cards (Design review, Design coordination, Constructability input) are my draft. Is this scope right?

## Decisions I made that you may want to change
- Careers pages are ported into the new design. Changes from the old text: ACC/BIM360/ProjectWise and Synchro/4D mentions removed; Mumbai removed (Kochi only); BIM Lead is now "on-site / hybrid"; "UK-hours overlap" removed. "AMP8" remains in job-ad body text (not in any heading or button).
- Blog category chips are hidden while there are no posts (they would do nothing). They appear with the first published post.
- "About" in the nav links to the "Why Arangath" section on the home page.
- Featured card (BEP Starter Pack) has the tag "Entry offer" and a green "Ask about this" button linking to the contact form.
- Detail-page "What you receive" says "native and IFC formats" and "drawings and schedules": confirm these deliverables.
- `treatment-works-plain.svg` is a no-callout version of the hero drawing, generated from `tools/illustrations.py` (with labels off) for the detail page, since only the home hero should carry the clash callout.
- Default social card (1200x630) for all non-post pages is `assets/social/og-default.png`, made from `tools/social/card.html`. Re-render it with headless Chrome if the headline changes.

## Before merging to main
- Complete the one-time GitHub OAuth setup in `docs/publishing-a-blog-post.md` so /admin works. I could not test /admin sign-in from here.
- In Netlify, check the form named **contact** appears under Forms after the first deploy (it is detected from the built HTML).
- Run Lighthouse on the preview URL. I could not run it here (no Node/Chrome CLI); I checked structure, alt text, focus styles, keyboard controls and link integrity manually.
- No example blog post is committed. The template was checked with a temporary draft, since deleted.
