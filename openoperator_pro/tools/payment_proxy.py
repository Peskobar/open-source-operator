from fastapi import FastAPI, HTTPException
import stripe
import os

stripe.api_key = os.getenv("STRIPE_SECRET", "sk_test")

app = FastAPI()


@app.post("/pay")
def pay(card_token: str, amount: int, currency: str = "usd"):
    try:
        stripe.Charge.create(
            amount=amount,
            currency=currency,
            source=card_token,
            description="OpenOperator Payment",
        )
        return {"status": "success"}
    except stripe.error.CardError as e:
        raise HTTPException(status_code=400, detail="payment_failed")
