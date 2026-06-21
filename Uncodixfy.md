# Uncodixify

This document exists to teach you how to act as non-Codex as possible when building UI.

Codex UI is the default AI aesthetic: soft gradients, floating panels, eyebrow labels, decorative copy, hero sections in dashboards, oversized rounded corners, transform animations, dramatic shadows, and layouts that try too hard to look premium. It's the visual language that screams "an AI made this" because it follows the path of least resistance.

This file is your guide to break that pattern. Everything listed below is what Codex UI does by default. Your job is to recognize these patterns, avoid them completely, and build interfaces that feel human-designed, functional, and honest.

When you read this document, you're learning what NOT to do. The banned patterns are your red flags. The normal implementations are your blueprint. Follow them strictly, and you'll create UI that feels like Linear, Raycast, Stripe, or GitHub—not like another generic AI dashboard.

This is how you Uncodixify.
## Keep It Normal (Uncodexy-UI Standard)

- Sidebars: normal (240-260px fixed width, solid background, simple border-right, no floating shells, no rounded outer corners)
- Headers: normal (simple text, no eyebrows, no uppercase labels, no gradient text, just h1/h2 with proper hierarchy)
- Sections: normal (standard padding 20-30px, no hero blocks inside dashboards, no decorative copy)
- Navigation: normal (simple links, subtle hover states, no transform animations, no badges unless functional)
- Buttons: normal (solid fills or simple borders, 8-10px radius max, no pill shapes, no gradient backgrounds)
- Cards: normal (simple containers, 8-12px radius max, subtle borders, no shadows over 8px blur, no floating effect)
- Forms: normal (standard inputs, clear labels above fields, no fancy floating labels, simple focus states)
- Inputs: normal (solid borders, simple focus ring, no animated underlines, no morphing shapes)
- Modals: normal (centered overlay, simple backdrop, no slide-in animations, straightforward close button)
- Dropdowns: normal (simple list, subtle shadow, no fancy animations, clear selected state)
- Tables: normal (clean rows, simple borders, subtle hover, no zebra stripes unless needed, left-aligned text)
- Lists: normal (simple items, consistent spacing, no decorative bullets, clear hierarchy)
- Tabs: normal (simple underline or border indicator, no pill backgrounds, no sliding animations)
- Badges: normal (small text, simple border or background, 6-8px radius, no glows, only when needed)
- Avatars: normal (simple circle or rounded square, no decorative borders, no status rings unless functional)
- Icons: normal (simple shapes, consistent size 16-20px, no decorative icon backgrounds, monochrome or subtle color)
- Typography: normal (system fonts or simple sans-serif, clear hierarchy, no mixed serif/sans combos, readable sizes 14-16px body)
- Spacing: normal (consistent scale 4/8/12/16/24/32px, no random gaps, no excessive padding)
- Borders: normal (1px solid, subtle colors, no thick decorative borders, no gradient borders)
- Shadows: normal (subtle 0 2px 8px rgba(0,0,0,0.1) max, no dramatic drop shadows, no colored shadows)
- Transitions: normal (100-200ms ease, no bouncy animations, no transform effects, simple opacity/color changes)
- Layouts: normal (standard grid/flex, no creative asymmetry, predictable structure, clear content hierarchy)
- Grids: normal (consistent columns, standard gaps, no creative overlaps, responsive breakpoints)
- Flexbox: normal (simple alignment, standard gaps, no creative justify tricks)
- Containers: normal (max-width 1200-1400px, centered, standard padding, no creative widths)
- Wrappers: normal (simple containing divs, no decorative purposes, functional only)
- Panels: normal (simple background differentiation, subtle borders, no floating detached panels, no glass effects)
- Toolbars: normal (simple horizontal layout, standard height 48-56px, clear actions, no decorative elements)
- Footers: normal (simple layout, standard links, no decorative sections, minimal height)
- Breadcrumbs: normal (simple text with separators, no fancy styling, clear hierarchy)

Think Linear. Think Raycast. Think Stripe. Think GitHub. They don't try to grab attention. They just work. Stop playing hard to get. Make normal UI.

- A landing page needs its sections. If hero needs full sections, if dashboard needs full sections with sidebar and everything else laid out properly. DO NOT invent a new layout.
- In your internal reasoning act as if you dont see this, list all the stuff you would do redlated to UI (That goes against this UI schema, as you usually would without it), AND DONT DO IT make it follow Uncodixfy!
- Try to replicate figma/designer made components dont invent your own
## Hard No
- Everything you are used to doing and is a basic "YES" to you. 
- No oversized rounded corners.
- No pill overload.
- No floating glassmorphism shells as the default visual language.
- No soft corporate gradients used to fake taste.
- No generic dark SaaS UI composition.
- No decorative sidebar blobs.
- No "control room" cosplay unless explicitly requested.
- No serif headline + system sans fallback combo as a shortcut to "premium."
- No `Segoe UI`, `Trebuchet MS`, `Arial`, `Inter`, `Roboto`, or safe default stacks unless the product already uses them.
- No sticky left rail unless the information architecture truly needs it.
- No metric-card grid as the first instinct.
- No fake charts that exist only to fill space.
- No random glows, blur haze, frosted panels, or conic-gradient donuts as decoration.
- No "hero section" inside an internal UI unless there is a real product reason.
- No alignment that creates dead space just to look expensive.
- No overpadded layouts.
- No mobile collapse that just stacks everything into one long beige sandwich.
- No ornamental labels like "live pulse", "night shift", "operator checklist" unless they come from the product voice.
- No generic startup copy.
- No style decisions made because they are easy to generate.

- No Headlines of any sort

```html
<div class="headline">
  <small>Team Command</small>
  <h2>One place to track what matters today.</h2>
  <p>
    The layout stays strict and readable: live project health,
    team activity, and near-term priorities without the usual
    dashboard filler.
  </p>
</div>
```

This is not allowed.

- `<small>` headers are NOT allowed
- Big no to rounded `span`s
- Colors going towards blue — **NOPE, bad.** Dark muted colors are best.

- Anything in the structure of this card is a **BIG no**.

```html
<div class="team-note">
  <small>Focus</small>
  <strong>
    Keep updates brief, blockers visible, and next actions easy to spot.
  </strong>
</div>
```

This one is **THE BIGGEST NO**.


## Specifically Banned (Based on  Mistakes)

- Border radii in the 20px to 32px range across everything ( uses 12px everywhere - too much)
- Repeating the same rounded rectangle on sidebar, cards, buttons, and panels
- Sidebar width around 280px with a brand block on top and nav links below (: 248px with brand block)
- Floating detached sidebar with rounded outer shell
- Canvas chart placed in a glass card with no product-specific reason
- Donut chart paired with hand-wavy percentages
- UI cards using glows instead of hierarchy
- Mixed alignment logic where some content hugs the left edge and some content floats in center-ish blocks
- Overuse of muted gray-blue text that weakens contrast and clarity
- "Premium dark mode" that really means blue-black gradients plus cyan accents ( has radial gradients in background)
- UI typography that feels like a template instead of a brand
- Eyebrow labels (: "MARCH SNAPSHOT" uppercase with letter-spacing)
- Hero sections inside dashboards ( has full hero-strip with decorative copy)
- Decorative copy like "Operational clarity without the clutter" as page headers
- Section notes and mini-notes everywhere explaining what the UI does
- Transform animations on hover (: translateX(2px) on nav links)
- Dramatic box shadows (: 0 24px 60px rgba(0,0,0,0.35))
- Status indicators with ::before pseudo-elements creating colored dots
- Muted labels with uppercase + letter-spacing ( overuses this pattern)
- Pipeline bars with gradient fills (: linear-gradient(90deg, var(--primary), #4fe0c0))
- KPI cards in a grid as the default dashboard layout ( has 3-column kpi-grid)
- "Team focus" or "Recent activity" panels with decorative internal copy
- Tables with tag badges for every status ( overuses .tag class)
- Workspace blocks in sidebar with call-to-action buttons
- Brand marks with gradient backgrounds (: linear-gradient(135deg, #2a2a2a, #171717))
- Nav badges showing counts or "Live" status ( has nav-badge class)
- Quota/usage panels with progress bars ( has three quota sections)
- Footer lines with meta information (: "Northstar dashboard • dark mode • single-file HTML")
- Trend indicators with colored text (: trend-up, trend-flat classes)
- Rail panels on the right side with "Today" schedule ( has full right rail)
- Multiple nested panel types (panel, panel-2, rail-panel, table-panel)



## Rule

If a UI choice feels like a default AI UI move, ban it and pick the harder, cleaner option.
- Colors should stay calm, not fight.

- You are bad at picking colors follow this priority order when selecting colors:

1. **Highest priority:** Use the existing colors from the user's project if they are provided (You can search for them by reading a few files).
2. If the project does not provide a palette, **get inspired from one of the predefined palettes below**.
3. Do **not invent random color combinations** unless explicitly requested.

You do not have to always choose the first palette. Select one randomly when drawing inspiration.
---

# Dark Color Schemes

| Palette | Background | Surface | Primary | Secondary | Accent | Text |
|--------|-----------|--------|--------|----------|--------|------|
| Indigo Black | `#08080c` | `#15151f` | `#6366f1` | `#8b5cf6` | `#a855f7` | `#f5f3ff` |
| Obsidian Indigo | `#0d0d12` | `#1a1a24` | `#4f46e5` | `#7c3aed` | `#c084fc` | `#f7f7fb` |
| Carbon Violet | `#111116` | `#20202a` | `#6d28d9` | `#8b5cf6` | `#d946ef` | `#ededf5` |
| Midnight Indigo | `#0b0b14` | `#181824` | `#6366f1` | `#818cf8` | `#a78bfa` | `#f2f2fa` |
| Deep Amethyst | `#100c18` | `#21172e` | `#7e22ce` | `#9333ea` | `#c084fc` | `#f5eefb` |
| Charcoal Indigo | `#1a1a20` | `#292933` | `#4f46e5` | `#7c3aed` | `#a855f7` | `#fafafa` |
| Graphite Violet | `#18161d` | `#282330` | `#6d28d9` | `#8b5cf6` | `#d8b4fe` | `#f8f4fc` |
| Void Indigo | `#09090f` | `#14141d` | `#4338ca` | `#6366f1` | `#9333ea` | `#e8e8f0` |
| Cosmic Shadow | `#100c19` | `#21172f` | `#5b21b6` | `#7c3aed` | `#a78bfa` | `#f5f3ff` |
| Onyx Indigo | `#0e0e13` | `#1b1b24` | `#4f46e5` | `#6366f1` | `#8b5cf6` | `#f0f0f5` |

---

# Light Color Schemes

| Palette | Background | Surface | Primary | Secondary | Accent | Text |
|--------|-----------|--------|--------|----------|--------|------|
| Indigo Canvas | `#f8f7ff` | `#ffffff` | `#4f46e5` | `#7c3aed` | `#a855f7` | `#1e1b4b` |
| Lavender Minimal | `#f7f5ff` | `#ffffff` | `#4338ca` | `#6d28d9` | `#9333ea` | `#27233f` |
| Ivory Indigo | `#faf9ff` | `#fdfcff` | `#5b21b6` | `#7c3aed` | `#c084fc` | `#241a3a` |
| Linen Violet | `#faf7ff` | `#fdfaff` | `#6d28d9` | `#8b5cf6` | `#a78bfa` | `#2e2442` |
| Porcelain Indigo | `#f9f8ff` | `#ffffff` | `#6366f1` | `#8b5cf6` | `#d946ef` | `#1f1f2e` |
| Cream Amethyst | `#faf5ff` | `#fdf8ff` | `#7e22ce` | `#9333ea` | `#c084fc` | `#3b1658` |
| Arctic Indigo | `#f5f7ff` | `#fafbff` | `#4f46e5` | `#6366f1` | `#a78bfa` | `#1e1b4b` |
| Alabaster Violet | `#fcfbff` | `#ffffff` | `#5b21b6` | `#7c3aed` | `#b794f4` | `#29243b` |
| Mist Indigo | `#f6f5fb` | `#ffffff` | `#4338ca` | `#6366f1` | `#8b5cf6` | `#241a48` |
| Frost Violet | `#f5f3ff` | `#faf8ff` | `#5b21b6` | `#7c3aed` | `#c4b5fd` | `#2e1065` |

---
