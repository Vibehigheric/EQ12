import os
# import openai

class MockOpenAI:
    class ChatCompletion:
        @staticmethod
        def create(model, messages):
            return {"choices": [{"message": {"content": "Incident Summary: Suspect apprehended at 1400 hours..."}}]}

openai = MockOpenAI()

def extract_from_bodycam(audio, video):
    # Placeholder for extraction logic
    return "Raw transcript of incident..."

def generate_report(audio, video):
    incident_text = extract_from_bodycam(audio, video)
    summary = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": f"Summarize incident:\n{incident_text}"}]
    )
    return summary['choices'][0]['message']['content']

if __name__ == "__main__":
    print(generate_report("audio.wav", "video.mp4"))
