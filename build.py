#!/usr/bin/env python3
"""Arangath website build. Standard library only, so Netlify needs no install step.

    python3 build.py              # writes dist/
    INCLUDE_DRAFTS=1 python3 build.py   # also renders draft posts (preview only)

Pages are generated from the data and templates below; blog posts come from content/blog/*.md.
"""
import datetime
import html
import json
import math
import os
import re
import shutil
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(ROOT, "dist")
sys.path.insert(0, os.path.join(ROOT, "tools"))
import illustrations as ill  # noqa: E402

SITE = "https://arangath.co.uk"
EMAIL = "hello@arangath.co.uk"
LINKEDIN = "https://www.linkedin.com/company/arangath/"
LEGAL = "© 2026 Arangath Ltd · Registered in England and Wales, company no. 17202121 · Registered office: 66 Paul Street, London EC2A 4NA"
MAPS = "https://www.google.com/maps/search/?api=1&query=X82J%2BC7W%20Kochi%20Kerala"
DEFAULT_OG = "/assets/social/og-default.png"  # 1200x630; source: tools/social/card.html
INCLUDE_DRAFTS = os.environ.get("INCLUDE_DRAFTS") == "1"

CATEGORIES = ["Design consulting", "Information management", "BIM and coordination", "Digital delivery", "Company news"]


def e(s):
    return html.escape(str(s), quote=True)


# ---------------------------------------------------------------- data
ICONS = {
    "ruler": '<path d="M3 17 17 3l4 4L7 21z"/><path d="M7 13l2 2M10 10l2 2M13 7l2 2"/>',
    "layers": '<path d="M12 3 3 8l9 5 9-5z"/><path d="M3 13l9 5 9-5"/>',
    "cube": '<path d="M12 3l8 4.5v9L12 21l-8-4.5v-9z"/><path d="M12 12l8-4.5M12 12v9M12 12 4 7.5"/>',
    "route": '<circle cx="6" cy="18" r="2"/><circle cx="18" cy="6" r="2"/><path d="M8 18h6a3 3 0 0 0 0-6h-4a3 3 0 0 1 0-6h6"/>',
    "file": '<path d="M14 3H7a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h10a2 2 0 0 0 2-2V8z"/><path d="M14 3v5h5M9 13h6M9 17h6"/>',
    "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 3 3 5-6"/>',
    "db": '<ellipse cx="12" cy="6" rx="8" ry="3"/><path d="M4 6v6c0 1.7 3.6 3 8 3s8-1.3 8-3V6M4 12v6c0 1.7 3.6 3 8 3s8-1.3 8-3v-6"/>',
    "users": '<circle cx="9" cy="8" r="3"/><path d="M3 20c0-3.3 2.7-6 6-6s6 2.7 6 6"/><circle cx="17" cy="9" r="2.5"/><path d="M17 14c2.5 0 4 2 4 5"/>',
    "search": '<circle cx="11" cy="11" r="7"/><path d="m21 21-5-5"/>',
    "clip": '<rect x="6" y="4" width="12" height="17" rx="2"/><path d="M9 4h6v3H9zM9 12h6M9 16h4"/>',
    "draw": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M3 9h18M9 9v11"/>',
    "wrench": '<path d="M14.7 6.3a4 4 0 0 0-5.4 5.1L3 17.7 6.3 21l6.3-6.3a4 4 0 0 0 5.1-5.4l-2.6 2.6-2.4-.6-.6-2.4z"/>',
}


def icon(name):
    return f'<svg class="icon" viewBox="0 0 24 24" aria-hidden="true">{ICONS[name]}</svg>'


SERVICES = [
    {
        "slug": "design-consulting", "title": "Design consulting", "color": "#24506B", "icon": "ruler",
        "home_img": "hydraulic-profile", "banner_img": "hydraulic-profile",
        "sentence": "Engineer-led design support for treatment, pumping and network assets.",
        "banner": "Engineer-led design support that gets treatment, pumping and network designs right before they are modelled.",
        "cards": [
            ("Design review", "ruler", "Independent review of process and hydraulic design before it is modelled."),
            ("Design coordination", "layers", "Civil, structural, process and electrical design brought into one coordinated set."),
            ("Constructability input", "wrench", "Engineer-led checks on how the design will actually be built."),
        ],
    },
    {
        "slug": "information-management", "title": "Information management", "color": "#1D6FA3", "icon": "layers",
        "home_img": "model-layers", "banner_img": "model-layers",
        "sentence": "BIM execution plans, EIR responses and common data environments built to ISO 19650.",
        "banner": "BIM execution plans, EIR responses and common data environments, built to ISO 19650.",
        "cards": [
            ("BEP Starter Pack", "file", "A BIM Execution Plan built to your client's Employer's Information Requirements.", True),
            ("EIR response", "clip", "Clear, compliant responses to Employer's Information Requirements at tender stage."),
            ("CDE setup and administration", "db", "Common Data Environments set up and run to ISO 19650 conventions."),
        ],
    },
    {
        "slug": "modelling-coordination", "title": "BIM modelling and coordination", "color": "#1B2B3B", "icon": "cube",
        "home_img": "drainage-network", "banner_img": "data-centre", "detail": "/services/modelling-coordination",
        "sentence": "Coordinated models of your assets, checked for clashes before they reach site.",
        "banner": "Coordinated models of your assets, checked for clashes before they reach site.",
        "cards": [
            ("Discipline model production", "cube", "Civil, structural, mechanical and process models built to agreed levels of information."),
            ("Clash detection and coordination", "search", "Federated models checked, reported and resolved through structured coordination reviews."),
            ("Drawings and asset data", "draw", "Drawings and COBie asset data extracted from the coordinated model."),
        ],
    },
    {
        "slug": "delivery-support", "title": "Digital delivery support", "color": "#2E4A66", "icon": "route",
        "home_img": "delivery-support", "banner_img": "delivery-support",
        "sentence": "Practical setup and onboarding so your team can deliver digitally from day one.",
        "banner": "Practical setup and onboarding so your team can deliver digitally from day one.",
        "cards": [
            ("Workflow setup", "route", "Templates, naming and review workflows set up around what your client requires."),
            ("Team onboarding", "users", "Your project team trained on the tools and standards the job needs."),
            ("Tender and mobilisation support", "check", "Help through tender responses and the first weeks of project delivery."),
        ],
    },
]

ASSETS = [
    ("Treatment works", "treatment-works-plain", "Clarifiers, filter blocks, process pipework and the buildings around them, modelled as one coordinated works.",
     ["Clarifiers and settlement tanks", "Filter blocks and washwater systems", "Process pipework, valves and chemical dosing", "Buildings and supporting structures"]),
    ("Pumping stations and reservoirs", "pumping-station", "Wet wells, pump halls, pipework and service reservoirs, modelled to the level of information your design stage needs.",
     ["Wet wells and pump chambers", "Pumps, pipework, valves and lifting equipment", "Electrical and control rooms", "Reservoir tanks, chambers and access"]),
    ("Networks and sewers", "sewer-long-section", "Pipelines, chambers and long sections, modelled against existing utilities and ground levels.",
     ["Gravity sewers and rising mains", "Manholes, chambers and valve pits", "Existing utilities and crossings", "Long sections and ground profiles"]),
    ("Data centres", "data-centre", "Halls, plant and building services, modelled for dense, fast-moving building projects.",
     ["Data halls and building structure", "Mechanical and electrical plant", "Cooling, power and containment routes", "Plant rooms and service risers"]),
]
RECEIVE = ["Federated model in native and IFC formats", "Clash reports with agreed resolutions", "Drawings and schedules from the model",
           "COBie asset data to the client's asset information requirements"]

PROJECTS = [
    {
        "slug": "chamravattom-bridge", "title": "Chamravattom Bridge", "loc": "Malappuram, Kerala", "static": "chamravattom-bridge",
        "chips": ["978 m", "70 sluice gates", "Road and irrigation"],
        "sentence": "A regulator-cum-bridge across the Bharathapuzha that carries road traffic and controls river flow.",
        "desc": "One of Kerala's longest bridges at nearly a kilometre, built across the Bharathapuzha river in southern India. It carries road traffic while controlling the flow of water through 70 sluice gates — a dual-purpose design that cuts the driving distance between two of Kerala's major cities by 38km and irrigates thousands of hectares of farmland. A complex civil and hydraulic engineering contract requiring precise coordination between road, bridge and water management systems.",
        "facts": [("Location", "Malappuram, Kerala"), ("Length", "978 m"), ("Sluice gates", "70"), ("Type", "Civil · hydraulic")],
        "model": ill.regulator_bridge, "layers": [("structure", "Structure"), ("equipment", "Equipment"), ("water", "Water")],
        "legacy": "chamravattom-bridge-bim",
        "meta": "Chamravattom Bridge, Kerala: a 978 m regulator-cum-bridge with 70 sluice gates across the Bharathapuzha, with an interactive illustrative model.",
    },
    {
        "slug": "kollam-rural-water-supply", "title": "Rural Water Supply, Kollam", "loc": "Kollam, Kerala", "static": "kollam-rural-water-supply",
        "chips": ["Jal Jeevan Mission", "Pipe networks", "Pumping stations"],
        "sentence": "Piped drinking water to rural households across Kollam district under the Jal Jeevan Mission.",
        "desc": "Drinking water infrastructure delivered under India's Jal Jeevan Mission — a government programme bringing piped clean water to every rural household across the country. Works in Kollam district included laying underground water mains, building pumping stations and elevated storage tanks, drilling tube wells, and connecting thousands of homes to clean water for the first time. A community-scale civil engineering contract with direct impact on public health.",
        "facts": [("Location", "Kollam, Kerala"), ("Programme", "Jal Jeevan Mission"), ("Type", "Water supply · rural"), ("Sponsor", "Government of India")],
        "model": ill.rural_water_supply, "layers": [("structure", "Structure"), ("pipework", "Pipework"), ("equipment", "Equipment")],
        "legacy": "kollam-rural-water-supply-bim",
        "meta": "Rural water supply in Kollam, Kerala, delivered under the Jal Jeevan Mission, with an interactive illustrative model of a typical scheme.",
    },
    {
        "slug": "kollam-100mld-wtp", "title": "100 MLD WTP, Kollam", "loc": "Kollam, Kerala", "static": "kollam-100mld-wtp",
        "chips": ["100 MLD", "AMRUT", "Kollam Corporation"],
        "sentence": "A 100 million litre a day treatment works serving Kollam city and surrounding communities.",
        "desc": "A large-scale drinking water treatment facility built to serve Kollam city and surrounding communities in southern Kerala — processing 100 million litres of raw water every day into safe drinking water. The plant takes water from source, aerates it to remove odours, passes it through three large circular settling tanks, filters it through 24 filter beds, and disinfects it before pumping it through a new trunk main to the city. Delivered under India's AMRUT programme, addressing chronic water scarcity across one of Kerala's largest urban areas.",
        "facts": [("Location", "Kollam, Kerala"), ("Capacity", "100 MLD"), ("Programme", "AMRUT"), ("Client", "Kollam Corporation")],
        "model": ill.wtp_100mld, "layers": [("structure", "Structure"), ("pipework", "Pipework"), ("equipment", "Equipment")],
        "legacy": "kollam-100mld-wtp-bim",
        "meta": "100 MLD water treatment plant in Kollam, Kerala, delivered under AMRUT, with an interactive illustrative model.",
    },
]
LIVE_PROJECT = {"title": "20 MLD Water Treatment Plant", "chips": ["20 MLD", "Water treatment"], "sentence": "A 20 MLD water treatment plant currently in delivery."}
MODEL_CAPTION = "Illustrative model based on the delivered project, not the as-built BIM model."


def load_badges():
    with open(os.path.join(ROOT, "config", "badges.json")) as f:
        return [b for b in json.load(f) if b.get("held")]


# ---------------------------------------------------------------- layout
def lockup(cls=""):
    # The mark stands in for the first "A"; the A after the R is logo green.
    return (f'<a class="lockup {cls}" href="/" aria-label="Arangath">'
            '<img src="/assets/logo/arangath-mark-dark-bg.svg" alt="" width="26" height="34">'
            '<span aria-hidden="true">R<span class="g">A</span>NGATH</span></a>')


NAV = [("Services", "/services"), ("Projects", "/#projects"), ("About", "/#why"), ("Careers", "/careers"), ("Blog", "/blog")]


def header(current=""):
    items = []
    for label, href in NAV:
        cur = ' aria-current="page"' if current == label else ""
        items.append(f'<li><a href="{href}"{cur}>{label}</a></li>')
    items.append('<li><a class="btn btn-primary btn-mobile" href="/#contact">Get in touch</a></li>')
    return f'''<header class="site-header"><div class="wrap nav">
{lockup()}
<ul class="nav-links" id="nav-links">{"".join(items)}</ul>
<a class="btn btn-primary" href="/#contact">Get in touch</a>
<button class="nav-toggle" type="button" aria-expanded="false" aria-controls="nav-links" aria-label="Menu"><svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
</div></header>'''


def footer():
    svc = "".join(f'<li><a href="{s.get("detail", "/services#" + s["slug"])}">{e(s["title"])}</a></li>' for s in SERVICES)
    return f'''<footer class="site-footer"><div class="wrap">
<div class="footer-grid">
<div>{lockup("sm")}<p class="footer-note">Consulting and digital engineering for water.</p></div>
<div><h2>Company</h2><ul><li><a href="/#why">About</a></li><li><a href="/careers">Careers</a></li><li><a href="/blog">Blog</a></li><li><a href="{LINKEDIN}" rel="noopener" target="_blank">LinkedIn</a></li></ul></div>
<div><h2>Services</h2><ul>{svc}</ul></div>
<div><h2>UK office</h2><address>66 Paul Street<br>London EC2A 4NA<br>United Kingdom<br><a href="mailto:{EMAIL}">{EMAIL}</a></address></div>
<div><h2>India office</h2><address>Near Petta Bus Stop, Ettumanoor–Ernakulam Road, Petta, Poonithura, Maradu, Kochi, Ernakulam, Kerala 682038, India</address></div>
</div>
<div class="footer-legal"><span>{e(LEGAL)}</span><a href="{LINKEDIN}" rel="noopener" target="_blank">Arangath on LinkedIn</a></div>
</div></footer>'''


def page(title, desc, body, path, current="", og_image=None, og_type="website", extra_head="", scripts="", noindex=False):
    canonical = SITE + path
    img = og_image or DEFAULT_OG
    if img.startswith("/"):
        img = SITE + img
    robots = '<meta name="robots" content="noindex">' if noindex else ""
    return f'''<!DOCTYPE html>
<html lang="en-GB">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
<meta name="description" content="{e(desc)}">
<link rel="canonical" href="{canonical}">
{robots}
<meta property="og:site_name" content="Arangath">
<meta property="og:type" content="{og_type}">
<meta property="og:title" content="{e(title)}">
<meta property="og:description" content="{e(desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:image" content="{img}">
{"<meta property=og:image:width content=1200><meta property=og:image:height content=630>" if img.endswith("og-default.png") else ""}
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{e(title)}">
<meta name="twitter:description" content="{e(desc)}">
<meta name="twitter:image" content="{img}">
<meta name="theme-color" content="#0D1319">
<link rel="icon" type="image/png" href="/assets/logo/arangath-mark-dark-bg-512.png">
<link rel="alternate" type="application/rss+xml" title="Arangath blog" href="/blog/rss.xml">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Poppins:wght@600&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/css/site.css">
{extra_head}
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
{header(current)}
<main id="main">
{body}
</main>
{footer()}
<script src="/assets/js/site.js" defer></script>
{scripts}
</body>
</html>
'''


def img(name, alt, cls="", loading="lazy", w=None, h=None):
    return f'<img src="/assets/illustrations/{name}.svg" alt="{e(alt)}"{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} loading="{loading}"{f" width={chr(34)}{w}{chr(34)}" if w else ""}{f" height={chr(34)}{h}{chr(34)}" if h else ""}>'


ALT = {
    "hydraulic-profile": "Illustration of a hydraulic profile through a treatment works",
    "model-layers": "Illustration of a BIM model split into information layers",
    "drainage-network": "Illustration of a drainage network model",
    "delivery-support": "Illustration of a project delivery workflow",
    "treatment-works": "Model illustration of a water treatment works with a highlighted clash",
    "treatment-works-plain": "Model illustration of a water treatment works",
    "pumping-station": "Model illustration of a pumping station",
    "sewer-long-section": "Illustration of a sewer long section",
    "data-centre": "Model illustration of a data centre",
    "filter-block": "Model illustration of a filter block",
    "clarifier": "Model illustration of a clarifier",
}


def breadcrumb(items):
    lis = []
    for i, (label, href) in enumerate(items):
        if href and i < len(items) - 1:
            lis.append(f'<li><a href="{href}">{e(label)}</a></li>')
        else:
            lis.append(f'<li aria-current="page">{e(label)}</li>')
    return f'<nav class="crumbs" aria-label="Breadcrumb"><ol>{"".join(lis)}</ol></nav>'


def cta_band(title, text, img_name, btn="Tell us about your scheme", href="/#contact"):
    return f'''<section class="cta"><div class="wrap cta-inner">
<div><h2>{e(title)}</h2><p>{e(text)}</p><div class="btn-row"><a class="btn btn-primary" href="{href}">{e(btn)}</a></div></div>
<div class="cta-circle">{img(img_name, ALT[img_name])}</div>
</div></section>'''


def service_card(card, link=None):
    title, ic, sentence = card[0], card[1], card[2]
    featured = len(card) > 3 and card[3]
    tag = '<span class="tag-feat">Entry offer</span>' if featured else ""
    cta = ""
    if link:
        cta = f'<div class="card-cta"><a href="{link}">Learn more <span aria-hidden="true">→</span></a></div>'
    elif featured:
        cta = '<div class="card-cta"><a class="btn btn-primary" href="/#contact">Ask about this</a></div>'
    return f'<article class="card service{" featured" if featured else ""}">{icon(ic)}{tag}<h3>{e(title)}</h3><p>{e(sentence)}</p>{cta}</article>'


# ---------------------------------------------------------------- pages
def contact_section():
    options = "".join(f"<option>{e(s['title'])}</option>" for s in SERVICES) + "<option>Not sure yet</option>"
    return f'''<section class="section" id="contact"><div class="wrap contact-grid">
<div>
<p class="eyebrow">Contact</p>
<h2>Tell us about your scheme</h2>
<p class="lede">Send a few lines on what you are building. We reply within one business day.</p>
<a class="contact-email" href="mailto:{EMAIL}">{EMAIL}</a>
<div class="addr-grid">
<div class="addr"><h3>UK office</h3><address>66 Paul Street<br>London EC2A 4NA<br>United Kingdom</address><span class="role">Client-facing</span></div>
<div class="addr"><h3>India office</h3><address>Near Petta Bus Stop, Ettumanoor–Ernakulam Road, Petta, Poonithura, Maradu, Kochi, Ernakulam, Kerala 682038, India</address><span class="role">Delivery · <a href="{MAPS}" rel="noopener" target="_blank">Open in Google Maps</a> (X82J+C7W)</span></div>
</div>
</div>
<form class="form" name="contact" method="POST" action="/thank-you/" data-netlify="true" netlify-honeypot="bot-field">
<input type="hidden" name="form-name" value="contact">
<p class="hp"><label>Do not fill this in <input name="bot-field" tabindex="-1" autocomplete="off"></label></p>
<div><label for="f-name">Full name</label><input id="f-name" type="text" name="name" autocomplete="name" required></div>
<div><label for="f-company">Company</label><input id="f-company" type="text" name="company" autocomplete="organization"></div>
<div><label for="f-email">Email</label><input id="f-email" type="email" name="email" autocomplete="email" required></div>
<div><label for="f-service">Service</label><select id="f-service" name="service"><option value="" disabled selected>Choose a service</option>{options}</select></div>
<div><label for="f-msg">About your project</label><textarea id="f-msg" name="message"></textarea></div>
<button class="btn btn-primary" type="submit">Send</button>
</form>
</div></section>'''


def project_card_home(p):
    chips = "".join(f'<li class="chip">{e(c)}</li>' for c in p["chips"])
    return f'''<article class="card project-card"><div class="pic"><img src="/assets/illustrations/projects/{p["static"]}.svg" alt="{e("Illustrative model of " + p["title"])}" loading="lazy" width="1000" height="620"></div>
<div class="body"><h3>{e(p["title"])}</h3><p class="loc">{e(p["loc"])}</p><ul class="chips">{chips}</ul><p>{e(p["sentence"])}</p>
<div class="card-cta"><a class="link" href="/projects/{p["slug"]}">View project <span aria-hidden="true">→</span></a></div></div></article>'''


def home():
    svc_cards = ""
    for s in SERVICES:
        cta = f'<div class="card-cta"><a class="link" href="{s["detail"]}">Learn more <span aria-hidden="true">→</span></a></div>' if s.get("detail") else ""  # only where a detail page exists
        svc_cards += f'''<article class="card service-home"><div class="pic">{img(s["home_img"], ALT[s["home_img"]])}</div><div class="body">{icon(s["icon"])}<h3>{e(s["title"])}</h3><p>{e(s["sentence"])}</p>{cta}</div></article>'''
    why = [("Built on engineering", "Advice grounded in 25 years of water and civil contracting, not a software background."),
           ("Standards-led", "ISO 19650 and the UK BIM Framework, interpreted carefully and applied consistently."),
           ("Efficient delivery", "UK-led client contact with production in Kochi, India, for senior-grade output at a lower cost.")]
    why_cards = "".join(f'<article class="card"><h3>{e(t)}</h3><p>{e(x)}</p></article>' for t, x in why)
    live = f'''<article class="card project-card"><div class="pic"><span class="tag-live">Live project</span>{img("filter-block", ALT["filter-block"])}</div>
<div class="body"><h3>{e(LIVE_PROJECT["title"])}</h3><p class="loc">In delivery</p><ul class="chips">{"".join(f'<li class="chip">{e(c)}</li>' for c in LIVE_PROJECT["chips"])}</ul><p>{e(LIVE_PROJECT["sentence"])}</p></div></article>'''
    std = ["ISO 19650 Parts 1 and 2", "UK BIM Framework", "CIC BIM Protocol", "Uniclass 2015", "COBie"]
    std_chips = "".join(f'<li class="chip">{e(s)}</li>' for s in std)
    badges = "".join(
        f'<a class="badge-tile" href="{e(b["url"])}" target="_blank" rel="noopener"><picture><source srcset="{b["src"]}.webp" type="image/webp"><img src="{b["src"]}.png" alt="{e(b["name"])}" loading="lazy" width="160" height="{b.get("h", 100)}"></picture></a>'
        for b in load_badges())
    body = f'''<section class="hero"><div class="wrap hero-grid">
<div><p class="eyebrow">Consulting and digital engineering for water</p>
<h1>Engineered and modelled right, first time.</h1>
<p class="lede">We give water-sector contractors the design consulting, information management and BIM modelling to get schemes coordinated before they reach site.</p>
<div class="btn-row"><a class="btn btn-primary" href="#contact">Tell us about your scheme</a><a class="btn btn-outline" href="#services">See our services</a></div></div>
<div class="illus-panel">{img("treatment-works", ALT["treatment-works"], loading="eager", w=800, h=560)}</div>
</div></section>
<section class="section alt" id="services"><div class="wrap">
<div class="section-head"><p class="eyebrow">Services</p><h2>Four ways we help</h2></div>
<div class="grid grid-4">{svc_cards}</div></div></section>
<section class="section" id="why"><div class="wrap">
<div class="why-top"><div class="section-head"><p class="eyebrow">Why Arangath</p><h2>Engineering judgement behind every model</h2><p class="lede">We are engineers first. That shows in what we model, what we ask and what we flag.</p></div>
<div class="card stat"><div class="num">25+</div><p>years of civil and environmental engineering experience behind our technical advisory.</p></div></div>
<div class="grid grid-3">{why_cards}</div></div></section>
<section class="section alt" id="projects"><div class="wrap">
<div class="section-head"><p class="eyebrow">Projects</p><h2>Water projects our engineers have delivered</h2></div>
<div class="grid grid-4">{"".join(project_card_home(p) for p in PROJECTS)}{live}</div>
<p class="caption">BIM coordination models shown are illustrative</p></div></section>
<section class="strip"><div class="wrap strip-inner">
<div><h2>Standards we work to</h2><ul class="chips">{std_chips}</ul></div>
{f'<div><h2>Memberships</h2>{badges}</div>' if badges else ''}
</div></section>
{contact_section()}'''
    return page("Arangath | Consulting and digital engineering for water",
                "Design consulting, information management and BIM modelling for water-sector contractors. UK-led, with production in Kochi, India.",
                body, "/", current="")


def services_page():
    groups = ""
    for i, s in enumerate(SERVICES):
        flip = " flip" if i % 2 else ""
        if s.get("detail"):
            btn = f'<a class="btn btn-outline" href="{s["detail"]}">See the detail</a>'
        else:
            btn = '<a class="btn btn-outline" href="/#contact">Talk to us</a>'
        cards = ""
        for c in s["cards"]:
            cards += service_card(c, link=s.get("detail"))  # "Learn more" only where a detail page exists
        groups += f'''<section class="svc-group" id="{s["slug"]}">
<div class="banner{flip}" style="background:{s["color"]}"><div class="panel" style="background:{s["color"]}"><h2>{e(s["title"])}</h2><p>{e(s["banner"])}</p>{btn}</div>{img(s["banner_img"], ALT[s["banner_img"]])}</div>
<div class="grid grid-3">{cards}</div></section>'''
    body = f'''<section class="page-head">{img("pumping-station", "", "fade", loading="eager").replace('alt=""', 'alt="" aria-hidden="true"')}<div class="wrap">
{breadcrumb([("Home", "/"), ("Services", None)])}
<h1>Services</h1><p class="lede">Four service lines covering design, information, modelling and delivery, so you can start with one deliverable and add more.</p></div></section>
<section class="section"><div class="wrap">{groups}</div></section>
{cta_band("Not sure where to start?", "Tell us about your scheme and we will suggest the smallest useful first step.", "drainage-network", btn="Tell us about your scheme")}'''
    return page("Services | Arangath", "Design consulting, information management, BIM modelling and coordination, and digital delivery support for water-sector contractors.", body, "/services", current="Services")


def modelling_page():
    blocks = ""
    for i, (title, im, sentence, model) in enumerate(ASSETS):
        flip = " flip" if i % 2 else ""
        mli = "".join(f"<li>{e(x)}</li>" for x in model)
        rli = "".join(f"<li>{e(x)}</li>" for x in RECEIVE)
        blocks += f'''<section class="asset{flip}"><div class="asset-top"><div class="illus-panel">{img(im, ALT[im])}</div>
<div><p class="eyebrow">Asset type</p><h2>{e(title)}</h2><p class="lede">{e(sentence)}</p></div></div>
<div class="grid grid-2"><article class="card"><h3 class="small">What we model</h3><ul>{mli}</ul></article><article class="card"><h3 class="small">What you receive</h3><ul>{rli}</ul></article></div></section>'''
    related = "".join(
        f'<article class="card service">{icon(s["icon"])}<h3>{e(s["title"])}</h3><p>{e(s["sentence"])}</p><div class="card-cta"><a class="link" href="/services#{s["slug"]}">See the service <span aria-hidden="true">→</span></a></div></article>'
        for s in SERVICES if s["slug"] != "modelling-coordination")
    body = f'''<section class="page-head"><div class="wrap">
{breadcrumb([("Home", "/"), ("Services", "/services"), ("BIM modelling and coordination", None)])}
<h1>BIM modelling and coordination</h1>
<p class="lede">Coordinated models of the assets you build, produced to ISO 19650 conventions and checked for clashes before they reach site.</p>
<p class="lede">From treatment works to networks, each model carries the asset data your client asks for.</p></div></section>
<section class="section"><div class="wrap">{blocks}</div></section>
<section class="section alt"><div class="wrap"><div class="section-head"><p class="eyebrow">Related</p><h2>Related services</h2></div><div class="grid grid-3">{related}</div></div></section>
{cta_band("Tell us about your scheme", "Send a few lines on what you are building and we will come back within one business day.", "model-layers")}'''
    return page("BIM modelling and coordination | Arangath",
                "Coordinated BIM models of treatment works, pumping stations, networks and data centres, built to ISO 19650 with COBie asset data.",
                body, "/services/modelling-coordination", current="Services")


def model_block(p):
    ill.FLOW = True
    scene = p["model"]()
    svg = scene.svg('id="model-svg"', label_=f"Illustrative model: {p['title']}")
    ill.FLOW = False
    layers = "".join(f'<button class="layer-btn" type="button" data-layer="{k}" aria-pressed="true">{v}</button>' for k, v in p["layers"])
    seen, keys = set(), ""
    for m in re.finditer(r'data-key="([^"]+)" data-tip="([^"]+)"', svg):
        k, t = m.group(1), m.group(2)
        if t in seen:
            continue
        seen.add(t)
        keys += f'<li><button class="key-btn" type="button" data-key="{e(k)}" aria-pressed="false">{e(t)}</button></li>'
    return f'''<div class="model" data-model="{p["slug"]}">
<div class="model-controls" role="group" aria-label="Model layers"><span class="lbl">Layers</span>{layers}<span class="sp"></span><button class="flow-btn" type="button" aria-pressed="false">Pause flow</button></div>
<div class="model-stage">{svg}<div class="model-tip" role="tooltip" aria-hidden="true"></div></div>
<p class="model-status" aria-live="polite">Hover, tap, or choose a key element below.</p>
<h3 class="small" style="font-size:14px;letter-spacing:.08em;text-transform:uppercase;color:var(--text-3);margin-top:14px">Key elements</h3>
<ul class="model-keys">{keys}</ul>
</div>
<p class="caption">{MODEL_CAPTION}</p>'''


def project_page(p):
    facts = "".join(f'<div class="fact"><div class="k">{e(k)}</div><div class="v">{e(v)}</div></div>' for k, v in p["facts"])
    chips = "".join(f'<li class="chip">{e(c)}</li>' for c in p["chips"])
    body = f'''<section class="page-head"><div class="wrap">
{breadcrumb([("Home", "/"), ("Projects", "/#projects"), (p["title"], None)])}
<h1>{e(p["title"])}</h1><p class="lede">{e(p["sentence"])}</p></div></section>
<section class="section"><div class="wrap">
{model_block(p)}
<div class="facts">{facts}</div>
<div class="narrow"><h2 style="font-size:26px;margin-bottom:14px">About the project</h2><p style="font-size:18px">{e(p["desc"])}</p><ul class="chips" style="margin-top:20px">{chips}</ul></div>
<div style="margin-top:64px"><h2 style="font-size:26px;margin-bottom:18px">BIM coordination view</h2>
<div class="legacy-img"><img src="/assets/projects/{p["legacy"]}.svg" alt="{e("Illustrative BIM coordination model of " + p["title"])}" loading="lazy" width="1120" height="560"></div>
<p class="caption">Illustrative BIM coordination model.</p></div>
</div></section>
{cta_band("Tell us about your scheme", "Send a few lines on what you are building and we will come back within one business day.", "model-layers")}'''
    return page(f'{p["title"]} | Arangath', p["meta"], body, f'/projects/{p["slug"]}',
                current="", scripts='<script src="/assets/js/model.js" defer></script>')


# ---------------------------------------------------------------- careers (ported from the previous site)
CAREERS_FIXES = [
    ("Common Data Environments (ACC / BIM360 / ProjectWise)", "Common Data Environments"),
    ("Work within a Common Data Environment (ACC / BIM360 / ProjectWise)", "Work within a Common Data Environment"),
    ("Familiarity with Common Data Environments (BIM360 / ACC or ProjectWise).", "Familiarity with Common Data Environments."),
    ("Support 4D sequencing (Synchro) and digital-delivery consultancy for Tier 2 contractors entering AMP8 frameworks.", "Support digital-delivery consultancy for Tier 2 contractors entering new frameworks."),
    ("Synchro 4D sequencing, Dynamo automation, or Scan to BIM leadership.", "Dynamo automation or Scan to BIM leadership."),
    ("based in India (Kochi and Mumbai)", "based in Kochi, India"),
    ("based in Kochi and Mumbai, India", "based in Kochi, India"),
]


def careers_pages():
    out = {}
    src = os.path.join(ROOT, "content", "careers-src")
    for rel, path, title_key in (("index.html", "/careers", "Careers"), ("bim-lead/index.html", "/careers/bim-lead", "Careers"), ("bim-modeller/index.html", "/careers/bim-modeller", "Careers")):
        s = open(os.path.join(src, rel), encoding="utf-8").read()
        title = html.unescape(re.search(r"<title>(.*?)</title>", s, re.S).group(1))
        desc = html.unescape(re.search(r'<meta name="description" content="(.*?)">', s, re.S).group(1).replace("\\'", "'"))
        ld = re.findall(r'<script type="application/ld\+json">.*?</script>', s, re.S)
        body = s[s.index("</nav>") + 6:s.index("<!-- FOOTER")]
        for a, b in CAREERS_FIXES:
            body = body.replace(a, b)
        body = re.sub(r'<p style="font-family:var\(--serif\)[^"]*">', '<p class="lede">', body)
        body = re.sub(r'<span class="tooltip-wrap">(AMP8)<span class="tooltip-box">.*?</span></span>', r"\1", body, flags=re.S)
        body = body.replace('<div class="hero-label" style="margin-bottom:20px;">Careers</div>', '<p class="eyebrow">Careers</p>')
        body = body.replace('style="grid-template-columns: repeat(2, 1fr);"', "").replace('class="services-grid"', 'class="grid grid-2"')
        body = body.replace('class="service-card"', 'class="card"')
        # wrap loose sections in the site container
        body = re.sub(r'<section class="(careers-hero|job-hero|roles-section)">', r'<section class="\1"><div class="wrap">', body)
        body = re.sub(r"</section>", "</div></section>", body)
        ldj = "\n".join(ld)
        out[path] = page(title, desc, body, path, current="Careers", extra_head=ldj)
    return out


# ---------------------------------------------------------------- blog
def parse_front_matter(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", text, re.S)
    if not m:
        return {}, text
    meta = {}
    for line in m.group(1).splitlines():
        if ":" not in line or line.lstrip().startswith("#"):
            continue
        k, v = line.split(":", 1)
        v = v.strip()
        if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
            v = v[1:-1].replace('\\"', '"')
        if v.lower() in ("true", "false"):
            v = v.lower() == "true"
        meta[k.strip()] = v
    return meta, m.group(2)


def inline_md(t):
    t = e(t)
    t = re.sub(r"`([^`]+)`", r"<code>\1</code>", t)
    t = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", t)
    t = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?!\*)", r"<em>\1</em>", t)
    t = re.sub(r"!\[([^\]]*)\]\(([^)\s]+)(?:\s+&quot;([^&]*)&quot;)?\)", lambda m: f'<img src="{m.group(2)}" alt="{m.group(1)}" loading="lazy">', t)
    t = re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", lambda m: f'<a href="{m.group(2)}">{m.group(1)}</a>', t)
    return t


def markdown(md):
    lines = md.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    while i < len(lines):
        ln = lines[i]
        if not ln.strip():
            i += 1
        elif ln.startswith("```"):
            j = i + 1
            while j < len(lines) and not lines[j].startswith("```"):
                j += 1
            out.append("<pre><code>" + e("\n".join(lines[i + 1:j])) + "</code></pre>")
            i = j + 1
        elif re.match(r"^#{1,4}\s", ln):
            n = len(ln) - len(ln.lstrip("#"))
            n = max(n, 2) if n == 1 else n  # the page title is the only h1
            out.append(f"<h{n}>{inline_md(ln.lstrip('#').strip())}</h{n}>")
            i += 1
        elif re.match(r"^(-{3,}|\*{3,})\s*$", ln):
            out.append("<hr>")
            i += 1
        elif ln.startswith(">"):
            buf = []
            while i < len(lines) and lines[i].startswith(">"):
                buf.append(lines[i].lstrip("> ").rstrip())
                i += 1
            out.append("<blockquote><p>" + inline_md(" ".join(buf)) + "</p></blockquote>")
        elif re.match(r"^\s*[-*]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*[-*]\s+", lines[i]):
                items.append(re.sub(r"^\s*[-*]\s+", "", lines[i]))
                i += 1
            out.append("<ul>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ul>")
        elif re.match(r"^\s*\d+[.)]\s+", ln):
            items = []
            while i < len(lines) and re.match(r"^\s*\d+[.)]\s+", lines[i]):
                items.append(re.sub(r"^\s*\d+[.)]\s+", "", lines[i]))
                i += 1
            out.append("<ol>" + "".join(f"<li>{inline_md(x)}</li>" for x in items) + "</ol>")
        elif re.match(r"^!\[[^\]]*\]\([^)]+\)\s*$", ln):
            m = re.match(r'^!\[([^\]]*)\]\(([^)\s]+)(?:\s+"([^"]*)")?\)\s*$', ln)
            cap = f"<figcaption>{e(m.group(3))}</figcaption>" if m and m.group(3) else ""
            out.append(f'<figure><img src="{e(m.group(2))}" alt="{e(m.group(1))}" loading="lazy">{cap}</figure>')
            i += 1
        else:
            buf = []
            while i < len(lines) and lines[i].strip() and not re.match(r"^(#{1,4}\s|>|```|\s*[-*]\s+|\s*\d+[.)]\s+|!\[)", lines[i]):
                buf.append(lines[i].strip())
                i += 1
            if not buf:  # safety: never loop forever on odd input
                buf = [lines[i].strip()]
                i += 1
            out.append("<p>" + inline_md(" ".join(buf)) + "</p>")
    return "\n".join(out)


def load_posts():
    posts = []
    d = os.path.join(ROOT, "content", "blog")
    for fn in sorted(os.listdir(d)):
        if not fn.endswith(".md"):
            continue
        meta, body = parse_front_matter(open(os.path.join(d, fn), encoding="utf-8").read())
        if meta.get("draft") is True and not INCLUDE_DRAFTS:
            continue
        slug = meta.get("slug") or fn[:-3]
        cat = meta.get("category", "")
        if cat not in CATEGORIES:
            raise SystemExit(f"{fn}: category '{cat}' must be one of {CATEGORIES}")
        for req in ("title", "date", "summary"):
            if not meta.get(req):
                raise SystemExit(f"{fn}: missing '{req}'")
        words = len(re.findall(r"\w+", body))
        date = datetime.date.fromisoformat(str(meta["date"])[:10])
        posts.append({"slug": slug, "title": meta["title"], "date": date, "summary": meta["summary"], "category": cat,
                      "author": meta.get("author") or "Arangath", "cover": meta.get("cover") or "/assets/illustrations/hydraulic-profile.svg",
                      "cover_alt": meta.get("cover_alt") or "", "draft": meta.get("draft") is True,
                      "read": max(1, math.ceil(words / 200)), "html": markdown(body)})
    posts.sort(key=lambda p: p["date"], reverse=True)
    return posts


def fmt_date(d):
    return f"{d.day} {d.strftime('%B %Y')}"


def post_card(p):
    return f'''<a class="card post-card" href="/blog/{p["slug"]}" data-post-cat="{e(p["category"])}"><img src="{e(p["cover"])}" alt="{e(p["cover_alt"])}" loading="lazy" width="640" height="360">
<div class="body"><span class="cat">{e(p["category"])}</span><h3>{e(p["title"])}</h3><p class="meta">{fmt_date(p["date"])} · {p["read"]} min read</p></div></a>'''


def blog_index(posts):
    if posts:
        chips = '<button type="button" data-cat="all" aria-pressed="true">All</button>' + "".join(
            f'<button type="button" data-cat="{e(c)}" aria-pressed="false">{e(c)}</button>' for c in CATEGORIES)
        main = f'''<div class="chip-filter" role="group" aria-label="Filter by category">{chips}</div>
<div class="grid grid-3">{"".join(post_card(p) for p in posts)}</div>
<p id="filter-empty" hidden>No posts in this category yet.</p>'''
    else:
        main = f'''<div class="card empty">{img("hydraulic-profile", "Illustration of a hydraulic profile through a treatment works")}
<h2>First posts coming soon</h2><p>We are preparing our first articles. Follow Arangath on LinkedIn to see new posts first.</p>
<div><a class="btn btn-primary" href="{LINKEDIN}" target="_blank" rel="noopener">Follow on LinkedIn</a></div></div>'''
    body = f'''<section class="page-head"><div class="wrap">{breadcrumb([("Home", "/"), ("Blog", None)])}<h1>Blog</h1>
<p class="lede">Notes on design, information management and BIM for water and infrastructure delivery.</p></div></section>
<section class="section"><div class="wrap">{main}</div></section>'''
    return page("Blog | Arangath", "Notes on design, information management and BIM for water and infrastructure delivery, from the Arangath team.", body, "/blog", current="Blog")


def blog_post(p, posts):
    same = [x for x in posts if x["category"] == p["category"] and x["slug"] != p["slug"]]
    more = (same + [x for x in posts if x["category"] != p["category"] and x["slug"] != p["slug"]])[:3]
    more_html = ""
    if more:
        more_html = f'<section class="section alt"><div class="wrap"><div class="section-head"><h2>More from the blog</h2></div><div class="grid grid-3">{"".join(post_card(x) for x in more)}</div></div></section>'
    cover_url = p["cover"] if p["cover"].startswith("http") else SITE + p["cover"]
    ld = {"@context": "https://schema.org", "@type": "BlogPosting", "headline": p["title"], "description": p["summary"],
          "datePublished": p["date"].isoformat(), "author": {"@type": "Organization" if p["author"] == "Arangath" else "Person", "name": p["author"]},
          "publisher": {"@type": "Organization", "name": "Arangath"}, "image": cover_url, "mainEntityOfPage": f'{SITE}/blog/{p["slug"]}'}
    ldx = '<script type="application/ld+json">' + json.dumps(ld).replace("</", "<\\/") + "</script>"
    cap = f"<figcaption>{e(p['cover_alt'])}</figcaption>" if p["cover_alt"] else ""
    body = f'''<article><section class="post-head"><div class="wrap">{breadcrumb([("Home", "/"), ("Blog", "/blog"), (p["title"], None)])}
<span class="cat">{e(p["category"])}</span><h1>{e(p["title"])}</h1><p class="summary">{e(p["summary"])}</p>
<p class="byline">{e(p["author"])} · {fmt_date(p["date"])} · {p["read"]} min read</p></div></section>
<div class="wrap"><figure class="post-cover"><img src="{e(p["cover"])}" alt="{e(p["cover_alt"])}" width="1200" height="520">{cap}</figure>
<div class="prose">{p["html"]}
<div class="inline-cta"><h2>Working on something similar? Get in touch</h2><a class="btn btn-primary" href="/#contact">Tell us about your scheme</a></div></div></div></article>
{more_html}'''
    return page(f'{p["title"]} | Arangath', p["summary"], body, f'/blog/{p["slug"]}', current="Blog", og_image=p["cover"], og_type="article", extra_head=ldx,
                noindex=p["draft"])


def rss(posts):
    items = ""
    for p in posts:
        dt = datetime.datetime(p["date"].year, p["date"].month, p["date"].day, 9, 0)
        items += (f'<item><title>{e(p["title"])}</title><link>{SITE}/blog/{p["slug"]}</link><guid>{SITE}/blog/{p["slug"]}</guid>'
                  f'<pubDate>{dt.strftime("%a, %d %b %Y %H:%M:%S +0000")}</pubDate><category>{e(p["category"])}</category><description>{e(p["summary"])}</description></item>')
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0"><channel><title>Arangath blog</title><link>{SITE}/blog</link><description>Notes on design, information management and BIM for water and infrastructure delivery.</description><language>en-gb</language>{items}</channel></rss>
'''


# ---------------------------------------------------------------- output
def write(path, content):
    full = os.path.join(DIST, path.lstrip("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(content)


def route(path):
    return "index.html" if path == "/" else path.strip("/") + "/index.html"


def main():
    if os.path.isdir(DIST):
        shutil.rmtree(DIST)
    os.makedirs(DIST)
    posts = load_posts()
    pages = {"/": home(), "/services": services_page(), "/services/modelling-coordination": modelling_page(), "/blog": blog_index(posts)}
    for p in PROJECTS:
        pages[f'/projects/{p["slug"]}'] = project_page(p)
    pages.update(careers_pages())
    for p in posts:
        pages[f'/blog/{p["slug"]}'] = blog_post(p, posts)
    for path, content in pages.items():
        write(route(path), content)
    write("thank-you/index.html", page("Thank you | Arangath", "Thanks for getting in touch.", '<section class="section"><div class="wrap narrow"><h1>Thank you</h1><p class="lede" style="margin:16px 0 28px">We have your message and will reply within one business day.</p><a class="btn btn-primary" href="/">Back to the home page</a></div></section>', "/thank-you/", noindex=True))
    write("404.html", page("Page not found | Arangath", "That page does not exist.", '<section class="section"><div class="wrap narrow"><h1>Page not found</h1><p class="lede" style="margin:16px 0 28px">That page does not exist. Try the home page or our services.</p><div class="btn-row"><a class="btn btn-primary" href="/">Home</a><a class="btn btn-outline" href="/services">Services</a></div></div></section>', "/404.html", noindex=True))
    write("blog/rss.xml", rss(posts))
    urls = [SITE + (p if p != "/" else "/") for p in pages if not any(x["draft"] and p == f'/blog/{x["slug"]}' for x in posts)]
    write("sitemap.xml", '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' + "".join(f"<url><loc>{u}</loc></url>" for u in sorted(urls)) + "</urlset>\n")
    write("robots.txt", f"User-agent: *\nAllow: /\nDisallow: /admin/\n\nSitemap: {SITE}/sitemap.xml\n")
    # static assets
    shutil.copytree(os.path.join(ROOT, "assets"), os.path.join(DIST, "assets"))
    for sub in ("css", "js"):
        os.makedirs(os.path.join(DIST, "assets", sub), exist_ok=True)
        for fn in os.listdir(os.path.join(ROOT, "src", sub)):
            shutil.copy(os.path.join(ROOT, "src", sub, fn), os.path.join(DIST, "assets", sub, fn))
    shutil.copytree(os.path.join(ROOT, "admin"), os.path.join(DIST, "admin"))
    print(f"built {len(pages) + 2} pages, {len(posts)} posts -> dist/")


if __name__ == "__main__":
    main()
