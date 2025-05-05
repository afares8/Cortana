from app.services.traffic.interface import TrafficInterface
from app.services.traffic.api.router import router as traffic_router

__all__ = ["TrafficInterface", "traffic_router"]
