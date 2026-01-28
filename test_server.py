import subprocess
import sys

# Try to import and run the main app to see any import errors
try:
    from main import app
    print("Successfully imported main app")
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()

# Try to import the auth routes specifically
try:
    from app.routes import auth
    print("Successfully imported auth routes")
except Exception as e:
    print(f"Auth routes import error: {e}")
    import traceback
    traceback.print_exc()

# Try to import the auth service
try:
    from app.services import AuthService
    print("Successfully imported AuthService")
except Exception as e:
    print(f"AuthService import error: {e}")
    import traceback
    traceback.print_exc()