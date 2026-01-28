"""
Patch for Pydantic compatibility with Python 3.13
"""

def apply_patch():
    """
    Apply the patch to fix the compatibility issue
    """
    import pydantic.typing

    # Define the patched function
    def patched_evaluate_forwardref(field, globalns, localns):
        try:
            # Try the new signature first (Python 3.13+)
            return field._evaluate(globalns, localns, frozenset())
        except TypeError:
            # Fall back to the old signature
            return field._evaluate(globalns, localns, set())

    # Apply the patch
    pydantic.typing.evaluate_forwardref = patched_evaluate_forwardref
    print("Applied Pydantic patch for Python 3.13 compatibility")

if __name__ == "__main__":
    apply_patch()