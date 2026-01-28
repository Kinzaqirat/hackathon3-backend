# Apply the patch before any other imports
import pydantic.typing

def patched_evaluate_forwardref(field, globalns, localns):
    try:
        # Try with recursive_guard as keyword argument (Python 3.13+)
        return field._evaluate(globalns, localns, recursive_guard=frozenset())
    except TypeError:
        # Fall back to the old signature
        return field._evaluate(globalns, localns, set())

# Apply the patch
pydantic.typing.evaluate_forwardref = patched_evaluate_forwardref
print("Applied Pydantic patch for Python 3.13 compatibility")

# Import the app after patching
import uvicorn
from main import app

if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False  # Disable reload to avoid import issues
    )