import re
from typing import Dict, Any, List
from langchain_mistralai import ChatMistralAI
from langchain_core.messages import HumanMessage, SystemMessage
from models.prompts import EXTRACTION_PROMPT

class MeetingExtractor:
    def __init__(self, api_key: str):
        self.llm = ChatMistralAI(
            model="mistral-small-latest",
            api_key=api_key,
            temperature=0.2
        )
    
    def extract(self, transcript: str) -> Dict[str, Any]:
        if not transcript or len(transcript) < 50:
            return {"decisions": [], "action_items": [], "summary": "Transcript too short.", "raw": transcript}
        
        if len(transcript) > 8000:
            transcript = transcript[:8000] + "... [truncated]"
        
        messages = [
            SystemMessage(content="You are a precise meeting analyst."),
            HumanMessage(content=f"{EXTRACTION_PROMPT}\n\n{transcript}")
        ]
        
        response = self.llm.invoke(messages)
        content = response.content
        
        # Parse decisions
        decisions = []
        match = re.search(r"DECISIONS:(.*?)(?:ACTION ITEMS:|SUMMARY:|$)", content, re.DOTALL | re.IGNORECASE)
        if match:
            for line in match.group(1).strip().split("\n"):
                line = line.strip()
                if line and line.startswith("-"):
                    decisions.append(line[1:].strip())
        
        # Parse action items
        actions = []
        match = re.search(r"ACTION ITEMS:(.*?)(?:SUMMARY:|$)", content, re.DOTALL | re.IGNORECASE)
        if match:
            for line in match.group(1).strip().split("\n"):
                line = line.strip()
                if line and line.startswith("-"):
                    parts = line[1:].strip().split("|")
                    action_data = {
                        "action": parts[0].strip() if parts else "",
                        "assigned_to": "Unassigned",
                        "deadline": "No deadline",
                        "priority": "MEDIUM"
                    }
                    for part in parts[1:]:
                        part = part.strip()
                        if "Assigned To:" in part:
                            action_data["assigned_to"] = part.replace("Assigned To:", "").strip()
                        elif "Deadline:" in part:
                            action_data["deadline"] = part.replace("Deadline:", "").strip()
                        elif "Priority:" in part:
                            action_data["priority"] = part.replace("Priority:", "").strip().upper()
                    actions.append(action_data)
        
        # Parse summary
        summary = ""
        match = re.search(r"SUMMARY:(.*?)$", content, re.DOTALL | re.IGNORECASE)
        if match:
            summary = match.group(1).strip()
        
        return {
            "decisions": decisions,
            "action_items": actions,
            "summary": summary,
            "raw": content
        }
