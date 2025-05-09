from app.routers.auth import router as auth_router
from app.routers.contracts import router as contracts_router
from app.routers.ai import router as ai_router
from app.routers.diagnostics import router as diagnostics_router
from app.routers.system_settings import router as system_settings_router
from app.routers.test_mistral import router as test_mistral_router

auth = auth_router
contracts = contracts_router
ai = ai_router
diagnostics = diagnostics_router
system_settings = system_settings_router
test_mistral = test_mistral_router
