try:
    from clerk_backend_api import Clerk
    print("Successfully imported Clerk from clerk_backend_api")
    clerk = Clerk(bearer_auth="sk_test_...")
    print(f"Clerk sessions object: {clerk.sessions}")
    # Check if verify_token exists
    if hasattr(clerk.sessions, 'verify_token'):
        print("clerk.sessions has verify_token")
    else:
        print("clerk.sessions DOES NOT have verify_token")
except ImportError as e:
    print(f"Import Error: {e}")
except Exception as e:
    print(f"Error: {e}")
