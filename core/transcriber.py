import whisper
import tempfile
import os
from typing import Dict, Any

class MeetingTranscriber:
    def __init__(self, model_size: str = "base"):
        self.model = whisper.load_model(model_size)
    
    def transcribe(self, audio_file) -> Dict[str, Any]:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.getvalue())
            tmp_path = tmp.name
        
        try:
            result = self.model.transcribe(tmp_path)
            return {
                "text": result["text"],
                "segments": result["segments"],
                "language": result.get("language", "unknown"),
                "success": True
            }
        except Exception as e:
            return {
                "text": "",
                "segments": [],
                "language": "unknown",
                "success": False,
                "error": str(e)
            }
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
