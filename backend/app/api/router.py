from fastapi import APIRouter

from app.api.routes import (
    addresses,
    auth,
    calendars,
    categories,
    contracts,
    events,
    payment_methods,
    reviews,
    services,
    users,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/usuarios", tags=["usuarios"])
api_router.include_router(categories.router, prefix="/categorias", tags=["categorias"])
api_router.include_router(services.router, prefix="/servicios", tags=["servicios"])
api_router.include_router(calendars.router, prefix="/calendarios", tags=["calendarios"])
api_router.include_router(events.router, prefix="/eventos", tags=["eventos"])
api_router.include_router(
    contracts.router, prefix="/contrataciones", tags=["contrataciones"]
)
api_router.include_router(reviews.router, prefix="/resenas", tags=["resenas"])
api_router.include_router(
    payment_methods.router, prefix="/metodos-de-pago", tags=["metodos-de-pago"]
)
api_router.include_router(addresses.router, prefix="/direcciones", tags=["direcciones"])
