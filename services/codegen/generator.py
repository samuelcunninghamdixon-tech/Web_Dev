from __future__ import annotations

import html
import re
from typing import Any


SAFE_COLOR = re.compile(r"^#[0-9a-fA-F]{3,8}$")


def _text(value: Any, default: str) -> str:
    return html.escape(str(value if value is not None else default), quote=False)


def _safe_url(value: Any, allowed_urls: set[str]) -> str:
  candidate = str(value or "").strip()
  if candidate.startswith(("https://", "http://")) and candidate in allowed_urls:
    return html.escape(candidate, quote=True)
  return ""


def generate_landing_page(
    design_brief: dict[str, Any],
    assets: dict[str, Any],
    approved_external_links: list[str] | None = None,
) -> str:
    brand_colors = assets.get("brand_colors", ["#111827", "#f59e0b", "#ffffff"])
    if not isinstance(brand_colors, list):
        brand_colors = []
    colors = [
        color if isinstance(color, str) and SAFE_COLOR.fullmatch(color) else fallback
        for color, fallback in zip(brand_colors[:3], ["#111827", "#f59e0b", "#ffffff"])
    ]
    colors.extend(["#111827", "#f59e0b", "#ffffff"][len(colors):])
    allowed_urls = set(approved_external_links or assets.get("allowed_urls", []))
    logo = _safe_url(assets.get("logo_url"), allowed_urls)
    logo_markup = f'<img src="{logo}" alt="Logo" class="h-10 w-10 object-contain" />' if logo else '<div role="img" aria-label="Logo placeholder" class="h-10 w-10"></div>'
    business_name = _text(design_brief.get("business_name"), "Business")
    headline = _text(design_brief.get("headline"), "Grow your business with confidence.")
    summary = _text(design_brief.get("summary"), "High-impact services designed to turn attention into results.")

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <title>{business_name}</title>
  </head>
  <body class=\"bg-slate-50 text-slate-900\">
    <header class=\"bg-white shadow-sm\">
      <nav class=\"max-w-6xl mx-auto px-6 py-4 flex items-center justify-between\">
        <div class=\"flex items-center gap-3\">
          {logo_markup}
          <span class=\"text-xl font-bold\">{business_name}</span>
        </div>
        <div class=\"hidden md:flex gap-6 text-sm\">
          <a href=\"#services\" class=\"hover:text-brand\">Services</a>
          <a href=\"#about\" class=\"hover:text-brand\">About</a>
          <a href=\"#testimonials\" class=\"hover:text-brand\">Reviews</a>
          <a href=\"#contact\" class=\"hover:text-brand\">Contact</a>
        </div>
      </nav>
    </header>

    <main>
      <section class=\"max-w-6xl mx-auto px-6 py-20 grid md:grid-cols-2 gap-10 items-center\">
        <div>
          <p class=\"mb-4 inline-block rounded-full bg-brand/10 px-3 py-1 text-sm font-medium text-brand\">Modern growth partner</p>
          <h1 class=\"text-4xl md:text-6xl font-black leading-tight\">{headline}</h1>
          <p class=\"mt-6 text-lg text-slate-600\">{summary}</p>
          <div class=\"mt-8 flex gap-4\">
            <a href=\"#contact\" class=\"bg-brand text-white px-6 py-3 rounded-lg font-semibold shadow-lg\">Book a Call</a>
            <a href=\"#services\" class=\"border border-slate-300 px-6 py-3 rounded-lg font-semibold\">Explore Services</a>
          </div>
        </div>
        <div class=\"rounded-3xl bg-gradient-to-br from-brand to-accent p-8 text-white shadow-2xl\">
          <div class=\"bg-white/10 backdrop-blur rounded-2xl p-6\">
            <h2 class=\"text-2xl font-bold\">Why clients choose us</h2>
            <ul class=\"mt-6 space-y-4\">
              <li>• Clear strategy and measurable outcomes</li>
              <li>• Fast response and transparent communication</li>
              <li>• Results-focused execution and design</li>
            </ul>
          </div>
        </div>
      </section>

      <section id=\"services\" class=\"max-w-6xl mx-auto px-6 py-20\">
        <div class=\"text-center mb-12\">
          <p class=\"text-brand font-semibold uppercase tracking-widest\">Services</p>
          <h2 class=\"text-3xl font-bold\">What we do best</h2>
        </div>
        <div class=\"grid md:grid-cols-3 gap-8\">
          <article class=\"bg-white rounded-2xl shadow-md p-6\">
            <h3 class=\"text-xl font-bold\">Brand Strategy</h3>
            <p class=\"mt-4 text-slate-600\">Position your business to stand out and communicate value clearly.</p>
          </article>
          <article class=\"bg-white rounded-2xl shadow-md p-6\">
            <h3 class=\"text-xl font-bold\">Web Design</h3>
            <p class=\"mt-4 text-slate-600\">Modern, mobile-friendly experiences built to convert visitors into leads.</p>
          </article>
          <article class=\"bg-white rounded-2xl shadow-md p-6\">
            <h3 class=\"text-xl font-bold\">Growth Systems</h3>
            <p class=\"mt-4 text-slate-600\">Automation and customer journeys that sustain momentum after launch.</p>
          </article>
        </div>
      </section>

      <section id=\"testimonials\" class=\"bg-slate-900 text-white py-20\">
        <div class=\"max-w-6xl mx-auto px-6\">
          <h2 class=\"text-3xl font-bold text-center\">Client Feedback</h2>
          <div class=\"mt-10 grid md:grid-cols-3 gap-8\">
            <blockquote class=\"bg-white/5 rounded-2xl p-6\">\"The new website made our business more credible immediately.\"</blockquote>
            <blockquote class=\"bg-white/5 rounded-2xl p-6\">\"They translated our vision into a more polished and conversion-ready experience.\"</blockquote>
            <blockquote class=\"bg-white/5 rounded-2xl p-6\">\"The process was smooth, strategic, and focused on results.\"</blockquote>
          </div>
        </div>
      </section>

      <section id=\"contact\" class=\"max-w-6xl mx-auto px-6 py-20\">
        <div class=\"grid md:grid-cols-2 gap-10 items-center\">
          <div>
            <p class=\"text-brand font-semibold uppercase tracking-widest\">Contact</p>
            <h2 class=\"text-3xl font-bold mt-3\">Let’s build your next chapter.</h2>
            <p class=\"mt-4 text-slate-600\">Reach out today to discuss your goals, timeline, and the next opportunities for your business.</p>
          </div>
          <form class=\"bg-white rounded-2xl shadow-lg p-6 border border-slate-200\">
            <div class=\"grid gap-4\">
              <input class=\"border rounded-lg px-4 py-3\" placeholder=\"Your name\" />
              <input class=\"border rounded-lg px-4 py-3\" placeholder=\"Email address\" />
              <textarea class=\"border rounded-lg px-4 py-3 h-32\" placeholder=\"Tell us about your project\"></textarea>
              <button class=\"bg-brand text-white px-6 py-3 rounded-lg font-semibold\" type=\"button\">Send message</button>
            </div>
          </form>
        </div>
      </section>
    </main>
  </body>
</html>
"""
