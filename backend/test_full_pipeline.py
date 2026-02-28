from services.mental_state_analyzer import analyze_and_respond

text = input("Enter text: ")

result = analyze_and_respond(text)

print("\n--- ANALYSIS ---")
print(result["analysis"])

print("\n--- RESPONSE ---")
print(result["response"])  # response is a string, not a dict