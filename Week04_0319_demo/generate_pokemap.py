import os
import json
import requests
import time
from jinja2 import Environment, FileSystemLoader

# Define wild encounters
REGIONS = [
    {"country": "Japan", "poke": "pikachu", "wb_code": "JPN"},
    {"country": "Egypt", "poke": "cofagrigus", "wb_code": "EGY"},
    {"country": "Brazil", "poke": "tropius", "wb_code": "BRA"},
    {"country": "Iceland", "poke": "lapras", "wb_code": "ISL"},
    {"country": "Australia", "poke": "kangaskhan", "wb_code": "AUS"},
    {"country": "France", "poke": "mr-mime", "wb_code": "FRA"},
    {"country": "United States", "poke": "braviary", "wb_code": "USA"},
    {"country": "China", "poke": "pangoro", "wb_code": "CHN"}
]

def fetch_json(url):
    print(f"  Fetching: {url}")
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"  [ERROR] Failed to fetch {url}: {e}")
        return None

def build_pokemap():
    print("=== Building PokeWorld Megadex ===")
    
    megadex = []
    
    for r in REGIONS:
        print(f"\nProcessing {r['country']}...")
        
        # 1. REST Countries (Geodata, Capital, Flag)
        rc_data = fetch_json(f"https://restcountries.com/v3.1/name/{r['country']}?fullText=true")
        if not rc_data: continue
        country_info = rc_data[0]
        
        latlng = country_info.get("latlng", [0, 0])
        capital = country_info.get("capital", ["Unknown"])[0]
        flag_svg = country_info.get("flags", {}).get("svg", "")
        
        # 2. Open-Meteo (Live Weather at Capital's approx location or country center)
        # Using country latlng for simplicity
        meteo_data = fetch_json(f"https://api.open-meteo.com/v1/forecast?latitude={latlng[0]}&longitude={latlng[1]}&current=temperature_2m,weather_code")
        
        # 3. World Bank (Population)
        wb_data = fetch_json(f"http://api.worldbank.org/v2/country/{r['wb_code']}/indicator/SP.POP.TOTL?format=json&per_page=5")
        pop = "Unknown"
        if wb_data and len(wb_data) > 1 and isinstance(wb_data[1], list):
            for entry in wb_data[1]:
                if entry.get("value") is not None:
                    pop = entry["value"]
                    break
            
        # 4. PokeAPI (Pokemon Data)
        poke_data = fetch_json(f"https://pokeapi.co/api/v2/pokemon/{r['poke']}")
        
        if poke_data:
            sprite = poke_data["sprites"]["other"]["official-artwork"]["front_default"]
            shiny_sprite = poke_data["sprites"]["other"]["official-artwork"]["front_shiny"]
            types = [t["type"]["name"] for t in poke_data["types"]]
            cry = poke_data.get("cries", {}).get("latest", "")
            
            megadex.append({
                "country_name": r["country"],
                "capital": capital,
                "latlng": latlng,
                "flag": flag_svg,
                "population": pop,
                "weather": meteo_data.get("current", {}) if meteo_data else {},
                "pokemon": {
                    "name": r["poke"].capitalize(),
                    "sprite": sprite,
                    "shiny_sprite": shiny_sprite,
                    "types": types,
                    "cry": cry
                }
            })
            
        time.sleep(0.5) # Be nice to APIs

    # Render Template
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("pokemap.html")
    
    json_str = json.dumps(megadex, indent=2)
    rendered_html = template.render(megadex=megadex, json_str=json_str)
    
    os.makedirs("output", exist_ok=True)
    with open("output/pokemap.html", "w", encoding="utf-8") as f:
        f.write(rendered_html)
        
    print("\nPokeWorld Map generated at output/pokemap.html")

if __name__ == "__main__":
    build_pokemap()
