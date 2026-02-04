"""
Sitemap configuration for GEUMHWA BOX website.
Provides XML sitemap for Google Search Console.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    """Sitemap for static pages."""

    priority = 0.5
    changefreq = 'weekly'
    protocol = 'https'

    def items(self):
        """Return list of static page names."""
        # Only include pages that exist and are accessible
        return [
            'home',
            'company',
            'products',
            'paper_box',
            # 'carton_box',  # Template not found
            # 'color_box',   # Template not found
            'equipment',
            'inquiry',
        ]

    def location(self, item):
        """Return URL for each page."""
        return reverse(item)

    def priority(self, item):
        """Set priority for each page."""
        priorities = {
            'home': 1.0,
            'products': 0.9,
            'paper_box': 0.8,
            'carton_box': 0.8,
            'color_box': 0.8,
            'company': 0.7,
            'equipment': 0.6,
            'inquiry': 0.8,
        }
        return priorities.get(item, 0.5)

    def changefreq(self, item):
        """Set change frequency for each page."""
        if item == 'home':
            return 'daily'
        elif item in ['products', 'paper_box', 'carton_box', 'color_box']:
            return 'weekly'
        else:
            return 'monthly'
