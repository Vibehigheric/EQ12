import sys
import os
import inspect

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    import eq12_player_eligibility_gate
    print(f"Module file: {eq12_player_eligibility_gate.__file__}")
    
    from eq12_player_eligibility_gate import PlayerEligibilityGate
    print("Successfully imported PlayerEligibilityGate class")
    
    gate = PlayerEligibilityGate()
    print("Successfully instantiated PlayerEligibilityGate")
    
    if hasattr(gate, 'evaluate_candidate'):
        print("✅ Method 'evaluate_candidate' EXISTS.")
        # Print signature
        sig = inspect.signature(gate.evaluate_candidate)
        print(f"Signature: {sig}")
    else:
        print("❌ Method 'evaluate_candidate' DOES NOT EXIST.")
        print("Available attributes:", dir(gate))

except ImportError as e:
    print(f"ImportError: {e}")
except Exception as e:
    print(f"An error occurred: {e}")
