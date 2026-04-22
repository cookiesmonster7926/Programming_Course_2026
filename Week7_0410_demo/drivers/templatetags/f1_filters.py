from django import template
import re

register = template.Library()

TEAM_MAP = {
    'red bull': 'redbull',
    'red bull racing': 'redbull',
    'haas f1 team': 'haas',
    'alpine f1 team': 'alpine',
    'rb f1 team': 'racingbulls',
    'aston martin': 'astonmartin',
    'kick sauber': 'kicksauber',
    'sauber': 'kicksauber'
}

@register.filter(name='to_cdn_slug')
def to_cdn_slug(team_name):
    if not team_name:
        return 'f1'
    name = team_name.lower()
    # Normalize via map
    for k, v in TEAM_MAP.items():
        if k in name:
            return v
    
    # Strip non-alphanumeric
    return re.sub(r'[^a-z0-9]', '', name)

@register.filter(name='car_img_url')
def car_img_url(team_name, season=2026):
    slug = to_cdn_slug(team_name)
    if str(season) == "2026":
        return f"https://media.formula1.com/image/upload/c_lfill,w_720/q_auto/d_common:f1:2026:fallback:car:2026fallbackcarright.webp/common/f1/2026/{slug}/2026{slug}carright.webp"
    else:
        return f"https://media.formula1.com/d_team_car_fallback_image.png/content/dam/fom-website/teams/{season}/{slug}.png"
