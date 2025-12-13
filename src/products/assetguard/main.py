import numpy as np

def predict_failure(vibration, temp):
    score = 0.7*vibration + 0.3*temp
    return score > 0.5

if __name__ == "__main__":
    vibration_level = 0.6
    temperature_level = 0.4
    failure_risk = predict_failure(vibration_level, temperature_level)
    print(f"Failure Predicted: {failure_risk}")
