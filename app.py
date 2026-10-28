import streamlit as st
import tempfile
import os
import html
from pathlib import Path
import importlib.machinery
import importlib.util

# -----------------------------
# LOAD BACKEND
# -----------------------------
@st.cache_resource
def load_pipeline():
    base = Path(__file__).parent
    candidates = [base / "agentic_pipeline", base / "agentic_pipeline.py"]
    path = next((p for p in candidates if p.exists()), None)
    if path is None:
        raise FileNotFoundError("Could not find agentic_pipeline backend file.")

    loader = importlib.machinery.SourceFileLoader("agentic_pipeline", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    if spec is None:
        raise RuntimeError("Unable to load pipeline spec.")
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module.handle_request

handle_request = load_pipeline()

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="Multi-Modal AI", layout="wide")

# -----------------------------
# HEADER
# -----------------------------
st.title("🤖 Multi-Modal AI Assistant")
st.caption("Chat | Image Analysis | File-to-Speech Conversion | Video Transcription | Export Results")

# -----------------------------
# SESSION STATE
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


st.markdown(
    """
    <style>
    .user-attachment-card {
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 14px;
        padding: 12px 14px;
        max-width: 320px;
        margin-bottom: 10px;
        background: rgba(255, 255, 255, 0.03);
    }
    .user-attachment-name {
        font-weight: 600;
        font-size: 1.05rem;
        line-height: 1.2;
    }
    .user-attachment-type {
        opacity: 0.75;
        margin-top: 2px;
    }
    .user-text-wrap {
        display: flex;
        justify-content: flex-start;
        margin-bottom: 10px;
    }
    .user-text-bubble {
        background: rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 10px 14px;
        max-width: 460px;
        word-break: break-word;
        display: inline-block;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def render_artifact_downloads(artifacts, key_prefix="persist"):
    for label, artifact in artifacts.items():
        data = artifact.get("data") if isinstance(artifact, dict) else None
        filename = artifact.get("filename", f"{label}.txt") if isinstance(artifact, dict) else f"{label}.txt"
        if data:
            st.download_button(
                label=f"Download {label}",
                data=data,
                file_name=filename,
                key=f"{key_prefix}_{label}_{filename}",
            )


def is_audio_only_artifacts(artifacts):
    return isinstance(artifacts, dict) and len(artifacts) == 1 and "audio" in artifacts


def render_assistant_content(content, key_prefix="assistant"):
    if isinstance(content, dict):
        text = content.get("text", "")
        artifacts = content.get("artifacts", {})

        if text:
            st.write(text)
        audio_artifact = artifacts.get("audio") if isinstance(artifacts, dict) else None
        if isinstance(audio_artifact, dict) and audio_artifact.get("data"):
            filename = str(audio_artifact.get("filename", "")).lower()
            audio_format = "audio/wav"
            if filename.endswith(".mp3"):
                audio_format = "audio/mpeg"
            elif filename.endswith(".m4a"):
                audio_format = "audio/mp4"
            st.audio(audio_artifact.get("data"), format=audio_format)
        if artifacts:
            render_artifact_downloads(artifacts, key_prefix=key_prefix)
    else:
        st.write(content)


def render_user_content(text, attachments):
    if text:
        safe_text = html.escape(str(text))
        st.markdown(
            f"""
            <div class="user-text-wrap">
                <div class="user-text-bubble">{safe_text}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    for name in attachments:
        safe_name = html.escape(str(name))
        ext = Path(str(name)).suffix.lower()
        file_kind = "Document"
        if ext in {".mp4", ".mov", ".mkv", ".avi"}:
            file_kind = "Video"
        elif ext in {".png", ".jpg", ".jpeg", ".webp"}:
            file_kind = "Image"
        elif ext in {".wav", ".mp3", ".m4a", ".aac", ".ogg", ".flac"}:
            file_kind = "Audio"

        st.markdown(
            f"""
            <div class="user-attachment-card">
                <div class="user-attachment-name">{safe_name}</div>
                <div class="user-attachment-type">{file_kind}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

# -----------------------------
# CHAT HISTORY
# -----------------------------
for idx, msg in enumerate(st.session_state.messages):
    with st.chat_message(msg["role"]):
        if msg.get("role") == "user" and isinstance(msg.get("content"), dict):
            payload = msg["content"]
            render_user_content(
                text=payload.get("text", ""),
                attachments=payload.get("attachments", []),
            )
        elif msg.get("role") == "assistant":
            render_assistant_content(msg.get("content"), key_prefix=f"hist_{idx}")
        else:
            st.write(msg["content"])

# -----------------------------
# UNIFIED INPUT (TEXT + MIC + FILE)
# -----------------------------
prompt = st.chat_input(
    "Say or record something and/or attach a file",
    accept_audio=True,
    accept_file=True,
    file_type=["pdf", "png", "jpg", "jpeg", "mp4", "wav", "mp3", "m4a"],
)

# -----------------------------
# PROCESS REQUEST
# -----------------------------
if prompt:
    typed_text = (prompt.text if getattr(prompt, "text", None) else "").strip()
    user_input = typed_text

    files = []
    try:
        files = prompt["files"] or []
    except Exception:
        files = getattr(prompt, "files", []) or []

    audio_file = getattr(prompt, "audio", None)

    file_obj = files[0] if files else None

    if not user_input:
        if audio_file is not None:
            user_input = "Transcribe this audio"
        elif file_obj is not None and hasattr(file_obj, "name"):
            user_input = f"Analyze attached file: {file_obj.name}"
        else:
            user_input = "Analyze this"

    attachment_names = []
    for f in files:
        name = getattr(f, "name", None)
        if name:
            attachment_names.append(name)

    if audio_file is not None:
        audio_name = getattr(audio_file, "name", None) or "recorded_audio.wav"
        attachment_names.append(audio_name)

    display_text = typed_text if typed_text else user_input
    if display_text.strip().lower() == "transcribe this audio":
        display_text = ""
    display_user_message = {
        "text": display_text,
        "attachments": attachment_names,
    }

    # Show user message
    st.session_state.messages.append({"role": "user", "content": display_user_message})
    with st.chat_message("user"):
        render_user_content(text=display_text, attachments=attachment_names)

    with st.chat_message("assistant"):
        with st.spinner("Processing..."):

            file_path = None
            mic_audio_path = None

            # If user speaks via mic (without typed text), transcribe first and use transcript as query.
            if audio_file is not None and not typed_text:
                audio_suffix = ".wav"
                if hasattr(audio_file, "name"):
                    audio_suffix = os.path.splitext(audio_file.name)[1] or ".wav"

                with tempfile.NamedTemporaryFile(delete=False, suffix=audio_suffix) as mic_tmp:
                    mic_tmp.write(audio_file.read())
                    mic_audio_path = mic_tmp.name

                mic_transcript = handle_request(
                    user_input="Transcribe this audio",
                    file_path=mic_audio_path,
                )

                if isinstance(mic_transcript, str):
                    transcript_text = mic_transcript.strip()
                    if transcript_text and not transcript_text.lower().startswith("error"):
                        user_input = transcript_text

            # Save file temporarily
            if file_obj:
                suffix = ".wav"
                if hasattr(file_obj, "name"):
                    suffix = os.path.splitext(file_obj.name)[1]

                with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
                    tmp.write(file_obj.read())
                    file_path = tmp.name

            # CALL BACKEND
            response = handle_request(
                user_input=user_input,
                file_path=file_path
            )

            # -----------------------------
            # OUTPUT HANDLING
            # -----------------------------
            assistant_content = None

            if isinstance(response, dict):
                st.success("🎥 Video processed!")

                saved_artifacts = {}
                for k, v in response.items():
                    p = Path(v)
                    if p.exists() and p.is_file():
                        with open(p, "rb") as f:
                            saved_artifacts[k] = {
                                "filename": p.name,
                                "data": f.read(),
                            }

                if saved_artifacts:
                    render_artifact_downloads(saved_artifacts, key_prefix="new_video")
                    output_text = "Transcript & report generated."
                    assistant_content = {
                        "text": output_text,
                        "artifacts": saved_artifacts,
                    }
                else:
                    output_text = "Video processed, but output files were not found."
                    st.write(output_text)
                    assistant_content = {"text": output_text}

            elif isinstance(response, str) and response.endswith(".wav"):
                audio_path = Path(response)
                if audio_path.exists() and audio_path.is_file():
                    with open(audio_path, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/wav")
                    audio_artifacts = {
                        "audio": {
                            "filename": audio_path.name,
                            "data": audio_bytes,
                        }
                    }
                    render_artifact_downloads(audio_artifacts, key_prefix="new_audio")
                    output_text = "🎧 Audio generated."
                    assistant_content = {
                        "text": output_text,
                        "artifacts": audio_artifacts,
                    }
                else:
                    output_text = "Audio generated, but file was not found for download."
                    st.write(output_text)
                    assistant_content = {"text": output_text}

            else:
                output_text = response
                st.write(output_text)
                assistant_content = {"text": output_text}

            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_content
            })

            # cleanup
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except PermissionError:
                    pass

            if mic_audio_path and os.path.exists(mic_audio_path):
                try:
                    os.remove(mic_audio_path)
                except PermissionError:
                    pass