from clerk_backend_api import Clerk
import inspect

clerk = Clerk(bearer_auth="sk_test_...")
print(f"Available methods on clerk: {dir(clerk)}")
print(f"Available methods on clerk.sessions: {dir(clerk.sessions)}")
