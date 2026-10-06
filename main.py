from fastapi import FastAPI

from routers.auth import router as auth_router
from routers.balance import router as balance_router
from routers.deposits import router as deposit_router
from routers.transfers import router as transfer_router
from routers.transactions import router as transactions_router


app = FastAPI()


app.include_router(auth_router)
app.include_router(balance_router)
app.include_router(deposit_router)
app.include_router(transfer_router)
app.include_router(transactions_router)