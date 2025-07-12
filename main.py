import json
from pathlib import Path
from typing import Optional, List, Dict, Any

from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

app = FastAPI(title="Coffee Roaster Search", version="1.0.0")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")


coffees_json_path = Path(__file__).parent.joinpath("data", "coffees.json")



with open(str(coffees_json_path)) as infile:
    COFFEES = [ { "id": i, **o } for i, o in enumerate(json.load(infile), 1)]

def filter_coffees(search_term: str = "") -> List[Dict[str, Any]]:
    """Filter coffees based on search term"""
    if not search_term:
        return COFFEES

    search_term = search_term.lower()
    filtered = []

    for coffee in COFFEES:
        # Search in name
        searchable_text = f"{coffee['name']}".lower()
        if search_term in searchable_text:
            filtered.append(coffee)

    return filtered


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve the main page"""

    # Get initial data counts
    coffee_count = len(COFFEES)

    return templates.TemplateResponse("index.html", {
        "request": request,
        "coffee_count": coffee_count,
        "initial_coffees": COFFEES
    })


@app.get("/api/search")
async def search(
        type: str = Query(..., description="Type of search: 'roasters' or 'coffees'"),
        search: Optional[str] = Query("", description="Search term")
):
    """API endpoint for searching roasters or coffees"""

    if type == "coffees":
        results = filter_coffees(search)
    else:
        return {"error": "Invalid type. Must be 'roasters' or 'coffees'"}

    return {
        "data": results,
        "count": len(results),
        "search_term": search,
        "type": type
    }


@app.get("/api/coffee/{coffee_id}")
async def get_coffee(coffee_id: int):
    """Get detailed information about a specific coffee"""
    coffee = next((c for c in COFFEES if c["id"] == coffee_id), None)
    if not coffee:
        return {"error": "Coffee not found"}

    return {
        "coffee": coffee,
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "coffees": len(COFFEES)}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
