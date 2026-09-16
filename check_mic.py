import sounddevice as sd
print("Available audio devices:")
print(sd.query_devices())
print("\nDefault Input Device:")
print(sd.default.device[0])
