from fastapi import APIRouter

auth_router = APIRouter(
    prefix='/auth',
    tags=['Auth'],
)

# NOTE: Legacy authentication routes are now handled by Clerk.
# This router is deactivated to ensure all auth flows go through Clerk.
# Custom logic has been moved to app.auth.services.auth_services