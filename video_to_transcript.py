# from openai import OpenAI
# import os
# from moviepy import VideoFileClip

# # Use env variable (IMPORTANT)
# client = OpenAI(api_key="sk-LI-QW-voerJ_V0kjtcXnLj8swgF2q_2I8qFbiCslljT3BlbkFJGxHGY8iOXoDL3K2PQPaHiy3aZElQFNXT9uf73cIvkA")

# # -----------------------------
# # 1. Extract audio (MP4 → MP3)
# # -----------------------------
# def extract_audio(video_path, output_audio="audio.mp3"):
#     video = VideoFileClip(video_path)
#     video.audio.write_audiofile(output_audio)
#     return output_audio


# # -----------------------------
# # 2. Transcribe
# # -----------------------------
# def transcribe(audio_file):
#     with open(audio_file, "rb") as f:
#         transcript = client.audio.transcriptions.create(
#             model="gpt-4o-transcribe",
#             file=f
#         )
#     return transcript.text

# # -----------------------------
# # 3. Full pipeline
# # -----------------------------
# def video_to_text(video_path, output_text_file="output.txt"):
#     print("🎥 Converting MP4 → MP3...")
#     audio = extract_audio(video_path)

#     print("🧠 Transcribing...")
#     text = transcribe(audio)

#     # Save to file
#     with open(output_text_file, "w", encoding="utf-8") as f:
#         f.write(text)

#     print(f"✅ Transcript saved to {output_text_file}")
#     return output_text_file


# # -----------------------------
# # Example
# # -----------------------------
# if __name__ == "__main__":
#     output_file = video_to_text("sample_video.mp4")

from openai import OpenAI
import os
from moviepy import VideoFileClip

client = OpenAI(api_key="sk-LI-QW-voerJ_V0kjtcXnLj8swgF2q_2I8qFbiCslljT3BlbkFJGxHGY8iOXoDL3K2PQPaHiy3aZElQFNXT9uf73cIvkA")


# -----------------------------
# 1. Extract audio
# -----------------------------
def extract_audio(video_path, output_audio="audio.mp3"):
    video = VideoFileClip(video_path)
    video.audio.write_audiofile(output_audio)
    return output_audio


# -----------------------------
# 2. Transcribe
# -----------------------------
def transcribe(audio_file):
    with open(audio_file, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model="gpt-4o-transcribe",
            file=f
        )
    return transcript.text


# -----------------------------
# 3. Generate Meeting Report
# -----------------------------
def generate_report(transcript):
    prompt = f"""
    Convert the following transcript into a professional meeting report.

    Include:
    - Title
    - Summary
    - Key Discussion Points
    - Decisions Made
    - Risks / Issues

    Transcript:
    {transcript}
    """

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3
    )

    return response.choices[0].message.content


# -----------------------------
# 4. Full pipeline
# -----------------------------
def video_to_outputs(video_path):
    print("🎥 Extracting audio...")
    audio = extract_audio(video_path)

    print("🧠 Transcribing...")
    transcript = transcribe(audio)

    # Save raw transcript
    with open("transcript.txt", "w", encoding="utf-8") as f:
        f.write(transcript)

    print("📝 Generating meeting report...")
    report = generate_report(transcript)

    # Save formatted report
    with open("meeting_report.txt", "w", encoding="utf-8") as f:
        f.write(report)

    print("✅ Files saved:")
    print(" - transcript.txt")
    print(" - meeting_report.txt")

    return "transcript.txt", "meeting_report.txt"


# -----------------------------
# Example
# -----------------------------
if __name__ == "__main__":
    video_to_outputs("sample_video.mp4")