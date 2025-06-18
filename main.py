from fastapi import FastAPI
import logging
#from app.core.database import engine, Base
#import app.models  

from app.auth.routes import router as auth_router
from app.products.routes import router as product_admin_router
from app.products import public_routes
from app.cart.routes import router as cart_router
from app.checkout import routes as checkout_routes
from app.orders.routes import router as order_router

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Server is running!"}

# Base.metadata.create_all(bind=engine)

app.include_router(auth_router)
app.include_router(product_admin_router)
app.include_router(public_routes.router)
app.include_router(cart_router)
app.include_router(checkout_routes.router)
app.include_router(order_router)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger(__name__)

