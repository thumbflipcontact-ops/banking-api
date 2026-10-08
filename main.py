from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware
from starlette.responses import Response

from routers.auth import router as auth_router
from routers.balance import router as balance_router
from routers.deposits import router as deposit_router
from routers.transfers import router as transfer_router
from routers.transactions import router as transactions_router


app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=[
        "localhost",
        "127.0.0.1",
        "testserver"
    ]
)


@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next
):
    response: Response = await call_next(request)

    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"

    return response


app.include_router(auth_router)
app.include_router(balance_router)
app.include_router(deposit_router)
app.include_router(transfer_router)
app.include_router(transactions_router)