def risk_scan(contract_text):
    risky = ["indemnify", "exclusive jurisdiction", "termination"]
    flags = [clause for clause in risky if clause in contract_text.lower()]
    return flags

if __name__ == "__main__":
    contract = "This agreement shall include exclusive jurisdiction in New York and termination clauses."
    print(f"Risk Flags Found: {risk_scan(contract)}")
