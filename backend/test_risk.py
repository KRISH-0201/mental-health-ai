from services.risk_service import detect_risk

text = input("Enter text: ")

result = detect_risk(text)

print("\nRisk Analysis:")
print(result)