import asyncio
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import httpx

from database import get_db, Base, engine
from clients import get_stripe_client, get_airalo_client
from schemas import TransactionSchema, PaymentIntentResponse, 


app = FastAPI(
    title="FinTech Async API",
    description="Szkielet asynchronicznego API integrującego Stripe i Airalo",
    version="1.0.0"
)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
      
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health", summary="Healthcheck bazy i API")
async def healthcheck(
    db: AsyncSession = Depends(get_db),
    stripe: httpx.AsyncClient = Depends(get_stripe_client)
):
    status = {"db": "down", "stripe": "down"}
    
    
    try:
        await db.execute(text("SELECT 1"))
        status["db"] = "ok"
    except Exception:
        pass

    
    try:
        resp = await stripe.get("/balance")
        if resp.status_code == 200:
            status["stripe"] = "ok"
    except Exception:
        pass

    if "down" in status.values():
        raise HTTPException(status_code=503, detail=status)
        
    return {"status": "ok", "details": status}

@app.post("/payments/create-intent", response_model=PaymentIntentResponse, summary="Tworzy PaymentIntent")
async def create_payment_intent(
    payload: TransactionSchema,
    stripe: httpx.AsyncClient = Depends(get_stripe_client),
    db: AsyncSession = Depends(get_db)
):
    
    data = {
        "amount": int(payload.amount * 100), 
        "currency": payload.currency
    }
    
    resp = await stripe.post("/payment_intents", data=data)
    if resp.status_code != 200:
        raise HTTPException(status_code=400, detail="Błąd Stripe API")
        
    stripe_data = resp.json()
    
    return PaymentIntentResponse(
        transaction_id=stripe_data["id"],
        client_secret=stripe_data["client_secret"],
        status=stripe_data["status"]
    )

@app.get("/esim/packages", summary="Pobiera paczki eSIM od Airalo")
async def get_esim_packages(
    country: str,
    airalo: httpx.AsyncClient = Depends(get_airalo_client)
):
    resp = await airalo.get(f"/packages?filter[country]={country}")
    if resp.status_code != 200:
         raise HTTPException(status_code=400, detail="Błąd Airalo API")
    return resp.json()