import random
import time
from typing import Tuple

def generate_timestamp_sequence(
    start: int,
    step: int,
    random_range: int,
    count: int = 10
) -> Tuple[int, ...]:
    """
    Generates a sequence of Unix-like timestamps (integers) with a fixed step
    and a random integer offset.

    Args:
        start: The starting timestamp (integer).
        step: The fixed difference (in seconds) between the base of successive timestamps (integer).
        random_range: The maximum absolute value of the random integer offset (integer).
        count: The number of timestamps to generate (integer, default is 10).

    Returns:
        A tuple of generated integer timestamps.
    """
    # --- Input Validation ---
    if not all(isinstance(arg, int) for arg in [start, step, random_range, count]):
        raise TypeError("All input arguments (start, step, random_range, count) must be integers.")
    if random_range < 0:
        raise ValueError("random_range cannot be negative.")
    if count < 0:
        raise ValueError("count cannot be negative.")
    if count == 0:
        return ()

    generated_timestamps = []
    for i in range(count):
        # 1. Calculate the base number
        base_timestamp = start + (i * step)

        # 2. Generate a random INTEGER offset (can be positive or negative)
        # randrange(a, b) returns a random integer N such that a <= N < b.
        random_offset = random.randrange(-random_range, random_range + 1)

        # 3. Add the offset to the base number
        final_timestamp = base_timestamp + random_offset

        generated_timestamps.append(final_timestamp)

    return tuple(generated_timestamps)

# --- Self-Test / Execution Block ---

def run_self_test():
    """Performs a series of tests to verify the function's integrity."""
    print("--- 🧪 Running Self-Tests for generate_timestamp_sequence ---")

    # Test Case 1: Basic functionality
    print("\n[Test 1] Basic Sequence Generation (5 items)")
    start_ts = int(time.time()) - 86400  # Start roughly 1 day ago
    step_val = 3600  # 1 hour step
    range_val = 600  # +/- 10 minutes random offset
    count_val = 5
    
    try:
        results = generate_timestamp_sequence(start_ts, step_val, range_val, count_val)
        print(f"  Input: Start={start_ts}, Step={step_val}, Range={range_val}, Count={count_val}")
        print(f"  Output: {results}")
        
        # Assertions
        assert isinstance(results, tuple), "FAIL: Output is not a tuple."
        assert len(results) == count_val, f"FAIL: Expected {count_val} items, got {len(results)}."
        assert all(isinstance(t, int) for t in results), "FAIL: Not all items are integers."
        print("  ✅ Test 1 Passed: Basic generation is correct.")
        
    except Exception as e:
        print(f"  ❌ Test 1 Failed with exception: {e}")

    # Test Case 2: Edge case - Zero count
    print("\n[Test 2] Zero Count (Should return empty tuple)")
    try:
        results = generate_timestamp_sequence(100, 10, 5, 0)
        assert results == (), "FAIL: Zero count did not return an empty tuple."
        print("  ✅ Test 2 Passed: Zero count returns empty tuple.")
    except Exception as e:
        print(f"  ❌ Test 2 Failed with exception: {e}")

    # Test Case 3: Invalid input type (Floating Point)
    print("\n[Test 3] Invalid Input Type (Should raise TypeError)")
    try:
        # Pass a float for step
        generate_timestamp_sequence(100, 10.5, 5, 5)  # type: ignore
        print("  ❌ Test 3 Failed: Did not raise TypeError for float input.")
    except TypeError:
        print("  ✅ Test 3 Passed: Successfully raised TypeError.")
    except Exception as e:
        print(f"  ❌ Test 3 Failed: Raised wrong exception: {type(e).__name__}")
        
    print("\n--- Self-Tests Complete ---")

# This is the "submodule" part: it determines if the file is being run directly
# or imported into another script.
if __name__ == "__main__":
    # If run directly (python timestamp_generator.py), execute the self-test.
    run_self_test()
    
    # You can also add an example run here
    print("\n--- Example Execution ---")
    start_ts = int(time.time())
    print(f"Generating 3 timestamps starting at current time: {start_ts}")
    example_output = generate_timestamp_sequence(
        start=start_ts, 
        step=60, 
        random_range=10, 
        count=3
    )
    print(f"Result: {example_output}")