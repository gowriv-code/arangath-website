Redesign arangath.co.uk to match the mockup exports in /design-reference/mockup/ (Home, Services, Modelling detail) and the reference pages in /design-reference/arangath-4-pages.pdf. Where the mockup shows "[Existing Arangath logo]" or "[Existing BIM image]", use the existing files already in this repo. Keep the dark theme. Keep the existing logo design. Transparent versions of the logo mark are supplied in /assets/logo/: use arangath-mark-dark-bg.svg on the dark site (its fine inner lines are lightened so they show on dark backgrounds) and arangath-mark.svg on light backgrounds such as the capability PDF; build the lockup as on the old site: the mark stands in for the first "A", followed by the letters "RANGATH" in Poppins 600, with the second "A" (the one after the R) in logo green #3CC99F and the rest in #EEF4F1, so it reads ARANGATH. No "Info Solutions" line in the header or footer. Give the lockup aria-label "Arangath"; and reuse the existing BIM images for the three Kerala projects.

SETUP
- Copy this handoff pack into the repo: assets/illustrations/*.svg → /assets/illustrations/; assets/badges/* → /assets/badges/; tools/illustrations.py → /tools/illustrations.py; design-reference/ → /design-reference/.
- Work on a new branch.

DESIGN TOKENS (green is an accent only: buttons, eyebrows, links, logo triangles)
- Background #0D1319; alternate section #121A22; card #161F29; card border #243140; illustration panel #1A2531
- Text #EEF4F1; secondary text #C5CFDA; footnote #A3AFBD; chip and list text #DDE4EB. Minimum text size 14px (13px only for tags). Secondary text must reach at least 7:1 contrast on its background
- Accent green #34C17F (text on green: #06211A); illustration lines blue #4FB3E8 with secondary lines #8AA4BD; amber #F2A541 for clash callouts only
- Banner fills: Design consulting #24506B; Information management #1D6FA3; Modelling #1B2B3B; Delivery support #2E4A66; "25+" card #1E5A86; CTA band #0F1C2A with heading #8FD0F2
- Fonts: Poppins 600 headings, DM Sans 400/500/700 body (Google Fonts)
- Radius: cards 16-20px, buttons fully rounded; content width 1200px; section padding 96px desktop, 56px mobile

PAGES
1. Home (/): nav with existing logo; hero (eyebrow "Consulting and digital engineering for water", H1 "Engineered and modelled right, first time.", one sentence, buttons "Tell us about your scheme" and "See our services", treatment-works.svg model illustration); "Four ways we help" (4 service cards: Design consulting, Information management, BIM modelling and coordination, Digital delivery support); "Why Arangath" (3 cards); Projects: "Water projects our engineers have delivered" with 4 cards in one row (Chamravattom Bridge; Rural Water Supply, Kollam; 100 MLD WTP, Kollam; and the live 20 MLD WTP card with an amber "Live project" tag and filter-block.svg), each with its supplied project model, spec chips and one sentence, and the caption "BIM coordination models shown are illustrative"; memberships strip; contact section (heading, one sentence, email and both addresses on the left; a form on the right with Full name, Company, Email, Service drop-down listing the four service lines plus "Not sure yet", About your project, Send; wire it to Netlify Forms); footer. No separate live-project section and no "Assets we work on" list.
2. Services (/services): short page header; for each of the 4 service lines (Design consulting first) a ServiceBanner followed by a 3-column grid of ServiceCards (BEP Starter Pack is the one featured card).
3. Service detail (/services/modelling-coordination): header with breadcrumb; 2-line intro; four AssetBlocks (Treatment works; Pumping stations and reservoirs; Networks and sewers; Data centres), each followed by "What we model" and "What you receive" cards (copy as in the mockup, including COBie asset data to the client's asset information requirements); related services row; CTA band. Build detail pages for the other three service lines on the same template later.
4. Capability page: do NOT build it in this release. It will be added later with the capability statement PDF.
5. Project pages (/projects/chamravattom-bridge, /projects/kollam-rural-water-supply, /projects/kollam-100mld-wtp): one per Kerala project, opened from its home-page card, each with a live model (below), the project facts and the existing BIM images.
6. Blog (/blog) and post template (/blog/<slug>), matching the Blog and Blog post artboards. Add "Blog" to the main nav after Careers on every page and to the footer Company column.

BLOG
- Listing page: page header ("Blog", one line), category filter chips (All, Design consulting, Information management, BIM and coordination, Digital delivery, Company news), then a 3-column grid of post cards (cover image, category, title, date · read time), newest first.
- Empty state (what launches now): when there are no published posts, show the empty-state card from the mockup: hydraulic-profile illustration, "First posts coming soon", the sentence "We are preparing our first articles. Follow Arangath on LinkedIn to see new posts first.", and a "Follow on LinkedIn" button linking to https://www.linkedin.com/company/arangath/.
- Post template: breadcrumb, category tag, H1, summary, author · date · read time, full-width cover image with caption, a 760px body column styled for H2, paragraphs, lists, pull quotes and inline images, an inline "Working on something similar? Get in touch" box, and a "More from the blog" row of 3 posts from the same category (or newest).
- Content: one Markdown file per post in /content/blog/ with front matter: title, slug, date, summary, category (one of the chip categories), author (default "Arangath"), cover, cover_alt, draft (true/false). Compute read time. Exclude drafts from the build.
- Publishing without code: set up a browser-based editor (for example Decap CMS at /admin) for the blog collection, using an authentication method Netlify currently supports, so Gowri can write a post, upload a cover image, save a draft and publish. Write the steps in /docs/publishing-a-blog-post.md in plain language.
- Sharing and search: per-post page title and meta description from the summary; Open Graph and Twitter card image from the cover so LinkedIn previews look right; canonical URL; RSS feed at /blog/rss.xml; include posts in the sitemap.
- Nothing with placeholder text may reach the live site. To check the post template, add one example post on the preview branch only, marked draft: true, and delete it before merging to main. The launched blog must show only the empty state.

KERALA PROJECT LIVE MODELS
Static models of the three past Kerala projects are supplied in /assets/illustrations/projects/ (chamravattom-bridge.svg, kollam-rural-water-supply.svg, kollam-100mld-wtp.svg), generated by regulator_bridge(), rural_water_supply() and wtp_100mld() in tools/illustrations.py. Use them on the home project cards, and turn each into a live, interactive model on its project page by regrouping the scene into Structure / Pipework / Equipment layers (edit the generator rather than hand-editing the SVG). Show the existing BIM images from the current site on each project page as well, below the live model.
- Chamravattom Bridge: regulator-cum-bridge across the Bharathapuzha, 978 m long with 70 sluice gates. Show a run of about 8 bays (piers, deck with road, vertical-lift gates between piers, water higher on the upstream side) with break lines to show it continues; label "978 m · 70 sluice gates".
- Rural Water Supply, Kollam (Jal Jeevan Mission): the typical scheme elements: source and intake, treatment unit, elevated service reservoir on columns, distribution mains and household tap connections.
- 100 MLD WTP, Kollam (AMRUT, Kollam Corporation): a larger works than the home-page hero: several clarifiers, a multi-cell filter house, clear water reservoir, pump house and chemical house.
- Make them live with inline SVG and light JavaScript (no heavy 3D library): layer toggles (Structure / Pipework / Equipment) that show and hide SVG groups; hover or tap tooltips naming key elements; a slow water-flow animation along pipes and channels (animated stroke-dashoffset), switched off under prefers-reduced-motion; keyboard-accessible controls.
- Put a small static version of each model on its home-page project card.
- Caption every model: "Illustrative model based on the delivered project, not the as-built BIM model."
- Where a detail is unknown (unit counts, layout), keep it generic and list it in the PR description as a question for Vish to confirm. Do not invent specifications, dimensions or figures that are not in this brief or on the current site.

COMPONENTS
- Illustrations: use the SVGs in /assets/illustrations/ as <img> with alt text (hero: treatment-works.svg; service cards: hydraulic-profile, model-layers, drainage-network, delivery-support; live project card: filter-block; home contact section has no illustration; Services page: hydraulic-profile, model-layers, data-centre, delivery-support banners and pumping-station faded in the page header, drainage-network in the CTA circle; detail page: treatment-works, pumping-station, sewer-long-section, data-centre). Do not repeat the same illustration within one page. Only the home hero drawing carries a clash callout label; all others are supplied without labels.
- ServiceBanner: 260px tall, rounded; coloured panel with a diagonal edge (clip-path) holding title, one sentence and an outline button; model illustration on the other side. Alternate sides between banners.
- ServiceCard: 24px stroke icon top right, title, one sentence (max 15 words). Show a "Learn more" link only where a detail page exists (currently only BIM modelling and coordination); add links for the other service lines when their detail pages are built. Featured variant: blue border and solid green button.
- ProjectCard, AssetBlock, WhyCard, CTABand (a single circle: model illustration with a blue segment on its right edge), AccreditationStrip.
- AccreditationStrip: reads badges from a config file and shows only held badges. For now it shows ONLY the British Water Member badge: /assets/badges/bw-member-320.webp (PNG fallback), alt "British Water Member", on a white rounded tile, linking to https://www.britishwater.co.uk in a new tab, max width 160px, lazy-loaded. No placeholder slots.

COPY RULES
- Use the copy from the mockup verbatim. Hero sentence max 25 words; card text one sentence.
- Remove: any "Clash Detection Pilot" offer (hero primary button reads "Tell us about your scheme"), 4D/Synchro service, tools not in use (ACC/BIM 360, ProjectWise, Synchro), the Markets section, "BIM4Water Member". Relabel the compliance list "Standards we work to".
- Contact: hello@arangath.co.uk. Show the two addresses as separate, labelled blocks, never on one line: "UK office" — 66 Paul Street, London EC2A 4NA, United Kingdom (client-facing); "India office" — Near Petta Bus Stop, Ettumanoor–Ernakulam Road, Petta, Poonithura, Maradu, Kochi, Ernakulam, Kerala 682038, India (delivery; Google Maps plus code X82J+C7W, use it for a map link). In the footer use two columns headed "UK office" and "India office"; in the contact section put them side by side under the email.
- Footer legal line on every page (UK trading disclosure requirement): "© 2026 Arangath Ltd · Registered in England and Wales, company no. 17202121 · Registered office: 66 Paul Street, London EC2A 4NA". Footer LinkedIn link: https://www.linkedin.com/company/arangath/.
- Before opening the PR, search the built site for "[" and "__" and confirm no placeholder text remains on any page.
- Keep all copy geography-neutral: no AMP8 or other UK-only programme names in headings or buttons.
- Do not name LCGC or the Rajahmundry scheme on the live-project card until approval is confirmed.

QUALITY
- Responsive: 3-column grids become 1 column below 768px; banners stack illustration under text.
- Real <a> and <button> elements; alt text on images; text contrast at least 4.5:1.
- Page titles and meta descriptions per page; run Lighthouse and fix accessibility errors.
- Commit on a branch and open a Netlify preview deploy; do not merge to main until reviewed. In the PR description, list every open question (for example Kerala model details).
