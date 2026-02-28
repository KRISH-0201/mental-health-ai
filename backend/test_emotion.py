from services.emotion_service import predict_emotion

text = input("Enter text: ")

result = predict_emotion(text)

print("\nDetected Emotions:")
print(result)