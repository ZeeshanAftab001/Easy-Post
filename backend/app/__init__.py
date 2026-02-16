# First import Base and then all models
from app.core.database import Base
from app.user.models.user import User  # Import User first
from app.oauth.models.social import SocialAccount  # Then SocialAccount