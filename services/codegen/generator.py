from __future__ import annotations

from typing import Any


def generate_landing_page(design_brief: dict[str, Any], assets: dict[str, Any]) -> str:
    brand_colors = assets.get("brand_colors", ["#111827", "#f59e0b", "#ffffff"])
    logo = assets.get("logo_url") or ""

    return f"""
<!DOCTYPE html>
<html lang=\"en\">
  <head>
    <meta charset=\"UTF-8\" />
    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1.0\" />
    <script src=\"https://cdn.tailwindcss.com\"></script>
    <script>
      tailwind.config = {{
        theme: {{
          extend: {{
            colors: {{
              brand: '{brand_colors[0]}',
              accent: '{brand_colors[1]}',
              light: '{brand_colors[2]}'
            }}
          }}
        }}
      }};
    </script>
    <title>{design_brief.get('business_name', 'Business')}</title>
  </head>
  <body class=\"bg-slate-50 text-slate-900\">
    <header class=\"bg-white shadow-sm\">
      <nav class=\"max-w-6xl mx-auto px-6 py-4 flex items-center justify-between\">
        <div class=\"flex items-center gap-3\">
          <img src=\"{logo}\" alt=\"Logo\" class=\"h-10 w-10 object-contain\" />
          <span class=\"text-xl font-bold\">{design_brief.get('business_name', 'Business')}</span>
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
          <h1 class=\"text-4xl md:text-6xl font-black leading-tight\">{design_brief.get('headline', 'Grow your business with confidence.')}</h1>
          <p class=\"mt-6 text-lg text-slate-600\">{design_brief.get('summary', 'High-impact services designed to turn attention into results.')}</p>
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
