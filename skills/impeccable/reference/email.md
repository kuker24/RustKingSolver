# Email design and HTML email implementation

Load this reference when the user wants to draft, compose, design, redesign, critique, or build an email: newsletters, promotional campaigns, welcome sequences, transactional receipts, password resets, onboarding digests, milestone celebrations, or win-back emails.

Modern web CSS, Tailwind, div-based layouts, CSS Grid, Flexbox, and React/shadcn web components **actively break email clients**. Email clients render with outdated engines (Outlook on Windows still uses Microsoft Word's HTML/Word rendering engine; Gmail strips head styles in certain web views; iOS Mail and Outlook web rewrite color schemes).

This guide unifies anti-slop visual design principles with bulletproof email client rendering.

---

## 1. Anti-slop email principles

AI-generated email defaults to generic slop: wide empty white gaps, generic blue CTAs, interchangeable stock layouts, and lifeless footers. Replace those defaults with committed choices:

1. **Own a color.** Pick one primary signature color for buttons, key borders, and accents that connects to brand identity. Never default to generic SaaS purple or blue unless that is the verified brand color.
2. **Restrained palette.** Limit the email to 4 colors:
   - 1 dominant brand accent (CTA, key emphasis)
   - 1 neutral dark for body text (`#111827`, `#1e293b`; never harsh `#000000`)
   - 1 neutral muted for labels/footer (`#64748b`, `#6b7280`)
   - 1 canvas neutral (`#f8fafc`, `#ffffff`, `#f9fafb`)
3. **Intentional imagery.** Sourced or clearly prompted image slots with defined aspect ratios and styled fallback text. Never place decorative AI stock graphics without purpose.
4. **No orphan whitespace.** Avoid random 80px gaps between two-line sentences. Spacing must be rhythmic and structured (typically 16px, 24px, or 32px between sections).
5. **Distinctive voice.** Tailor the rhythm of copy and visual layout to match the chosen archetype.

---

## 2. The Six Email Archetypes

Commit to an archetype before drafting markup. Do not blend them into a mushy hybrid.

| Archetype | Best for | Hallmarks | Typography | Key styling |
| --- | --- | --- | --- | --- |
| **Editorial** | Newsletters, essays, brand stories, long-form digests | Single column, generous leading, drop caps, bylines, reading rhythm | Serif headline (Georgia, Times New Roman), clean sans body | Warm paper canvas, subtle dividing rules, high copy density |
| **Bold-mono** | Releases, tech announcements, changelogs, developer updates | High data density, structured key-value grids, commit logs, sharp borders | Monospace headers (Courier New, Consolas, Monaco), sans body | High contrast, 1px solid borders, pill badges, terminal aesthetic |
| **Minimal-lux** | Luxury retail, architecture, portfolio, private invitations | Single photo focus, whisper borders, generous margins, restrained copy | Elegant serif or tracked geometric sans | Monochromatic base, muted brass or slate accent, quiet CTA |
| **Founder letter** | Welcome, milestones, churn win-back, CEO updates | Plain-text feel, first-person narrative, short paragraphs (1-3 sentences) | Clean native sans (`system-ui`, Arial) | Zero template chrome, no hero image, simple hyperlinked text or quiet button |
| **Punk / Character** | Drops, creator economy, music, streetwear, youth brands | High contrast, bold borders, asymmetrical card accents, irreverent copy | Heavy bold display sans, tight tracking | High saturation accents, thick borders (2px solid black), energetic tags |
| **Lookbook** | Visual commerce, fashion, food, visual product releases | 80% photography, 20% copy, visual gallery grid, hero banner | Minimal discreet sans | Full-bleed hero image, 2-column image grid (stacks on mobile), minimal text overlays |

---

## 3. Strict Email Client Rules (Non-Negotiable)

When generating email markup, web development instincts must be set aside:

### A. Layout: Presentation Tables Only
- **Zero `<div>` grid/column layouts, zero CSS Grid, zero Flexbox, zero `float`.**
- For raw HTML emails, every layout container must be a `<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%">`.
- `<div>` elements are strictly forbidden for layout columns, grids, or visual containers. However, `<div>` tags are explicitly permitted for hidden preheader text wrappers (`mso-hide:all; display:none;`) and progressive enhancement client hacks.
- **Email framework exemption:** If the project uses modern email component frameworks such as **React Email** (`@react-email/components`), **JSX Email**, or **MJML**, write idiomatic framework components (`<Html>`, `<Head>`, `<Preview>`, `<Body>`, `<Container>`, `<Section>`, `<Column>`, `<Row>`, `<Text>`, `<Button>`, `<Img>`, `<Hr>`) instead of hand-crafting raw nested HTML tables. The framework compiler handles generating client-safe nested tables automatically. All visual principles (archetypes, color restraint, typography, spacing, 100 KB budget) remain mandatory.
- Standard container width is **600px max**, centered:
  ```html
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" bgcolor="#f8fafc" style="background-color: #f8fafc;">
    <tr>
      <td align="center" style="padding: 24px 16px;">
        <!--[if mso]>
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="600" align="center">
        <tr><td>
        <![endif]-->
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="max-width: 600px; background-color: #ffffff; border-radius: 8px;" bgcolor="#ffffff">
          <!-- Content rows -->
        </table>
        <!--[if mso]>
        </td></tr>
        </table>
        <![endif]-->
      </td>
    </tr>
  </table>
  ```

### B. Styling: Inline CSS
- Apply inline `style="..."` attributes to every `<table>`, `<td>`, `<p>`, `<a>`, and `<span>`.
- Embedded `<style>` blocks in `<head>` are allowed **only** for progressive enhancement:
  - Media queries (`@media only screen and (max-width: 600px)`)
  - Dark mode overrides (`@media (prefers-color-scheme: dark)`)
  - Hover states for clients that support them

### C. Color: Six-Digit Hex Only
- Always write `#111827`, `#ffffff`, `#2563eb`.
- **Forbidden:** 3-digit hex (`#fff`), `rgb()`, `rgba()`, `hsl()`, CSS custom properties (`var(--primary)`). Outlook and older Android clients completely drop properties with modern color notation.

### D. Spacing: Cell Padding Only
- Margin on `<p>`, `<div>`, and `<table>` is stripped or broken by Outlook.
- Set all vertical and horizontal spacing via `padding` on `<td>` elements.
- For vertical gaps between content blocks, use dedicated spacer rows:
  ```html
  <tr style="line-height:0;font-size:0;">
    <td height="24" style="height:24px;line-height:24px;font-size:0;">&nbsp;</td>
  </tr>
  ```

### E. Images: Explicit Dimensions and Styled Alt Text
- Always declare `display: block; border: 0; outline: none; text-decoration: none;`.
- Set explicit HTML attributes `width="..."` and `height="..."`, plus CSS `style="width: 100%; max-width: 560px; height: auto; display: block;"`.
- Because Outlook and corporate webmail block images by default, provide styled alt text so the email remains legible:
  ```html
  <img src="https://example.com/hero.jpg" width="560" height="280" alt="New release overview" style="display:block; width:100%; max-width:560px; height:auto; border:0; outline:none; font-family:Arial, sans-serif; font-size:14px; color:#475569; background-color:#f1f5f9;">
  ```

### F. Bulletproof Button (CTA)
Anchors (`<a>`) with padding fail in Outlook on Windows because Word engine strips vertical padding on inline elements. Use a padded table-cell button with Outlook VML fallback or spacer padding:

```html
<table role="presentation" cellpadding="0" cellspacing="0" border="0" align="center" style="margin: 0 auto;">
  <tr>
    <td align="center" bgcolor="#2563eb" style="border-radius: 6px; background-color: #2563eb;">
      <a href="https://example.com/action" target="_blank" style="display: inline-block; padding: 14px 28px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; font-size: 15px; font-weight: 600; color: #ffffff; text-decoration: none; border-radius: 6px; mso-padding-alt: 0;">
        <!--[if mso]>
        <i style="letter-spacing: 28px; mso-font-width: -100%; mso-text-raise: 20pt;">&nbsp;</i>
        <![endif]-->
        <span style="mso-text-raise: 10pt;">Get Started Today &rarr;</span>
        <!--[if mso]>
        <i style="letter-spacing: 28px; mso-font-width: -100%;">&nbsp;</i>
        <![endif]-->
      </a>
    </td>
  </tr>
</table>
```

### G. Preheader Text with Anti-Spill Padding
Always place an invisible preheader right after `<body>`. Add zero-width non-joiners (`&#847;&zwnj;&nbsp;`) so that subsequent body copy or header navigation is not pulled into the client's inbox preview snippet:

```html
<div style="display:none;font-size:1px;color:#ffffff;line-height:1px;max-height:0px;max-width:0px;opacity:0;overflow:hidden;mso-hide:all;">
  Concise preheader snippet summarizing the email value proposition (80-100 chars).
  &#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;&#847;&zwnj;&nbsp;
</div>
```

### H. Dark Mode Support
Support dark mode without breaking light mode:
1. In `<head>`:
   ```html
   <meta name="color-scheme" content="light dark">
   <meta name="supported-color-schemes" content="light dark">
   <style>
     :root { color-scheme: light dark; supported-color-schemes: light dark; }
     @media (prefers-color-scheme: dark) {
       .dark-bg { background-color: #0f172a !important; }
       .dark-card { background-color: #1e293b !important; }
       .dark-text { color: #f8fafc !important; }
       .dark-muted { color: #94a3b8 !important; }
       .dark-border { border-color: #334155 !important; }
     }
     [data-ogsc] .dark-bg { background-color: #0f172a !important; }
     [data-ogsc] .dark-card { background-color: #1e293b !important; }
     [data-ogsc] .dark-text { color: #f8fafc !important; }
     [data-ogsc] .dark-muted { color: #94a3b8 !important; }
   </style>
   ```
2. Transparent logos must have a subtle outer glow/stroke or live in a defined background box so they do not become invisible on inverted dark backgrounds.

### I. Size Limit and Deliverability
- **Keep total HTML file size under 100 KB.** Gmail clips emails at 102 KB, hiding content behind a `[Message clipped] View entire message` link and breaking unsubscribe tracking.
- Every marketing/newsletter email **must** include a compliant footer:
  - Organization legal name
  - Valid physical postal address
  - Clear, functional Unsubscribe link (`<a href="{{unsubscribe_url}}">Unsubscribe</a>`)
  - Optional: Preferences link (`<a href="{{manage_preferences_url}}">Manage Preferences</a>`)

### J. Plain-Text Twin
Always accompany an HTML email with a clean, formatted plain-text alternative (`.txt`):
- Maintain clean vertical spacing with blank lines.
- Format links directly below CTA text or inline in brackets.
- Retain the legal footer and unsubscribe link.

---

## 4. Verification Checklist Before Delivery

Before delivering any email markup, verify every item:
- [ ] Tested width: Max 600px, centers cleanly on desktop and scales to 100% on mobile.
- [ ] No `div` containers for column layout (all table-cell based in raw HTML; React Email / MJML components if using an email framework).
- [ ] All colors are 6-digit hex codes (`#xxxxxx`).
- [ ] All spacing is on `<td>` padding or dedicated spacer rows (no `margin`).
- [ ] CTA button uses table cell padding with Outlook VML/padding fix.
- [ ] Preheader included with ZWNJ anti-spill characters.
- [ ] All images have `display:block`, explicit width/height, and styled `alt` text.
- [ ] Total HTML payload is strictly under 100 KB (no bloated inline base64 images).
- [ ] Paired plain-text version provided.
