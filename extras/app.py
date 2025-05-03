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


@app.post("/schedule-payment")
async def create_schedule_payment(
    amount: float = Query(..., description="Amount to transfer"),
    description: str = Query(..., description="Payment description"),
    recipient_email: str = Query(..., description="Recipient email"),
    time_start: str = Query(..., description="Start time (YYYY-MM-DD HH:MM:SS.SSSSSS)"),
    time_end: str = Query(None, description="End time (YYYY-MM-DD HH:MM:SS.SSSSSS)"),
    recurrence_unit: str = Query(..., description="ONCE, HOURLY, DAILY, WEEKLY, MONTHLY, YEARLY"),
    recurrence_size: int = Query(1, description="Recurrence size"),
    monetary_account_id: int = Query(2108197, description="Monetary account ID")
):
    """
    Creates a scheduled payment and returns the schedule payment ID.
    """
    from bunq.sdk.model.generated.endpoint import SchedulePaymentApiObject
    from bunq.sdk.model.generated.object_ import AmountObject, PointerObject
    
    # Create the payment details
    payment = {
        "amount": AmountObject(str(amount), "EUR"),
        "counterparty_alias": PointerObject("EMAIL", recipient_email),
        "description": description
    }
    
    # Create the schedule details
    schedule = {
        "time_start": time_start,
        "time_end": time_end,
        "recurrence_unit": recurrence_unit,
        "recurrence_size": recurrence_size
    }
    
    # Create the scheduled payment
    response = SchedulePaymentApiObject.create(
        payment=payment,
        schedule=schedule,
        monetary_account_id=monetary_account_id
    )
    
    # Return the schedule payment ID
    return {"schedule_payment_id": response.value}

