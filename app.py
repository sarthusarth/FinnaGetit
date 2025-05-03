from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from dashboard import generate_dashboard
import uvicorn

app = FastAPI()


dashboards = {}

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(
    goal: str = Query(..., description="The savings goal"),
    duration: int = Query(..., description="Duration in months"),
    amount: float = Query(..., description="Amount to save"),
    monetary_account_id: int = Query(2108197, description="Monetary account ID")
):
    """
    Serves the savings dashboard as an HTML page.
    """
    html_content = generate_dashboard(goal, duration, amount, monetary_account_id)
    dashboards[goal_id] = html_content
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)


@app.get("/dashboard/{goal_id}", response_class=HTMLResponse)
async def get_dashboard(goal_id: int):
    """
    Retrieves the savings dashboard for a given goal ID.
    """

    return HTMLResponse(content=dashboards[goal_id])

