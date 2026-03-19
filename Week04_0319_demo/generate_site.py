import os
import json
import requests
from jinja2 import Environment, FileSystemLoader

# Define API Endpoints
APIS = {
    "jsonplaceholder": "https://jsonplaceholder.typicode.com/posts/1",
    "github": "https://api.github.com/repos/tj/commander.js",
    "worldbank": "https://api.worldbank.org/v2/country/WLD/indicator/SP.POP.TOTL?format=json&per_page=60",
    "openmeteo": "https://api.open-meteo.com/v1/forecast?latitude=25.0478&longitude=121.5319&current=temperature_2m,wind_speed_10m,weather_code&hourly=temperature_2m,weather_code&timezone=Asia%2FTaipei",
    "restcountries": "https://restcountries.com/v3.1/name/japan",
    "pokeapi": "https://pokeapi.co/api/v2/pokemon/pikachu",
    "dogcat": "https://api.thecatapi.com/v1/images/search?limit=9",
    "randomuser": "https://randomuser.me/api/?results=10"
}

def fetch_data(name, url):
    print(f"Fetching {name} data...")
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def build_site():
    import shutil
    # Setup rendering environment
    env = Environment(loader=FileSystemLoader("templates"))
    
    # Ensure output directory exists
    os.makedirs("output", exist_ok=True)
    if os.path.exists("output/static"):
        shutil.rmtree("output/static")
    shutil.copytree("static", "output/static")

    # 1. Fetch all API data
    data_store = {}
    for name, url in APIS.items():
        try:
            data = fetch_data(name, url)
            # Pretty-print JSON for the data view
            json_str = json.dumps(data, indent=2)
            data_store[name] = {
                "raw": data,
                "json_str": json_str
            }
        except Exception as e:
            print(f"Failed to fetch {name}: {e}")
            data_store[name] = {"raw": {}, "json_str": f"Error: {e}"}

    # 2. Render individual API pages
    for name in APIS.keys():
        template = env.get_template(f"api_pages/{name}.html")
        rendered_html = template.render(data=data_store[name]["raw"], json_str=data_store[name]["json_str"])
        with open(f"output/{name}.html", "w", encoding="utf-8") as f:
            f.write(rendered_html)
            
    # 3. Render Index Page
    index_template = env.get_template("index.html")
    index_html = index_template.render()
    with open("output/index.html", "w", encoding="utf-8") as f:
        f.write(index_html)
        
    print("Static site build completed in output/ directory.")

if __name__ == "__main__":
    build_site()
