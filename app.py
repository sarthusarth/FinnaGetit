from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from dashboard import generate_dashboard
import uvicorn

app = FastAPI()

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
    return HTMLResponse(content=html_content)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
