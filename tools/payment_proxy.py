from fastapi import FastAPI, HTTPException
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SK", "")
app = FastAPI()

@app.post("/pay")
def pay(card_token: str, amount: int, currency: str = "usd"):
    try:
        stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=card_token,
            description="OpenOperator-Pro payment"
        )
        return {"status": "success"}
    except stripe.error.CardError:
        raise HTTPException(status_code=400, detail="payment_failed")
