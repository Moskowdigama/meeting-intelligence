# 🎙️ Meeting Intelligence

An AI-powered meeting assistant that transcribes audio, extracts key decisions and action items, and enables intelligent chat with your meeting history.

**Live Demo:** [Meeting Intelligence App](https://meeting-intelligence-n3yf6jfo4sdwztqdwypsxq.streamlit.app/)

---

## ✨ Features

- **🎤 Audio Transcription** – Upload any meeting recording (MP3, WAV, M4A, FLAC) and get a full transcript using OpenAI's Whisper.
- **📋 Smart Extraction** – Automatically extract key decisions, action items (with assignees, deadlines, and priorities), and a meeting summary.
- **✅ Action Tracker** – A built-in SQLite database tracks action items. Mark them as "Done" and filter by status.
- **💬 RAG Chat** – Ask questions about your meeting history. The system uses ChromaDB for vector search to find relevant context and answer your queries.
- **📊 Dashboard** – View a summary of total, pending, and completed action items at a glance.

---

## 🏗️ Architecture

The application follows a modular architecture:

Audio Upload → Whisper (Transcription) → Mistral AI (Extraction) → SQLite (Actions) + ChromaDB (RAG)


| Component | Technology | Purpose |
| :--- | :--- | :--- |
| **UI** | Streamlit | User interface for uploading files, viewing data, and chatting. |
| **Transcription** | OpenAI Whisper | Converts audio to text. |
| **LLM** | Mistral AI | Extracts structured data and powers the RAG chat. |
| **Vector Store** | ChromaDB | Stores meeting transcripts for semantic search. |
| **Database** | SQLite | Tracks meetings and action items. |

---

## 🚀 Local Development

Follow these steps to run the project on your local machine.

### Prerequisites

- Python 3.9+
- [Mistral AI API Key](https://console.mistral.ai/)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/Moskowdigama/meeting-intelligence.git
    cd meeting-intelligence
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up secrets:**
    Create a `.streamlit` folder and a `secrets.toml` file inside it.
    ```bash
    mkdir -p .streamlit
    cp .streamlit/secrets.toml.example .streamlit/secrets.toml
    ```
    Edit `.streamlit/secrets.toml` and add your actual API key:
    ```toml
    MISTRAL_API_KEY = "your-mistral-api-key-here"
    ```

5.  **Run the app:**
    ```bash
    streamlit run app.py
    ```

---

## ☁️ Deployment

This app is configured for easy deployment on **[Streamlit Cloud](https://share.streamlit.io/)**.

1.  Push your code to a GitHub repository.
2.  On Streamlit Cloud, click **"New app"**.
3.  Select your repository, branch, and set the main file path to `app.py`.
4.  In the app settings, add your `MISTRAL_API_KEY` as a secret.
5.  Click **"Deploy"**.

---

## 📸 Screenshots

*(You can add screenshots of your app here)*

---

## 🛠️ Tech Stack

- [Streamlit](https://streamlit.io/) - Frontend UI
- [OpenAI Whisper](https://github.com/openai/whisper) - Audio Transcription
- [LangChain](https://www.langchain.com/) / [Mistral AI](https://mistral.ai/) - LLM Integration
- [ChromaDB](https://www.trychroma.com/) - Vector Database
- [SQLite](https://www.sqlite.org/) - Action Tracking Database

---

## 🗺️ Future Roadmap

- **Sarvam AI Integration:** Add support for transcribing Hinglish and Hindi audio.
- **Meeting Analytics:** Visualize meeting patterns (e.g., top speakers, common topics).
- **Action Item Reminders:** Send email or in-app reminders for upcoming deadlines.

---

## 👨‍💻 Author

Built by [Shanky](https://github.com/Moskowdigama)

---

## 📝 License

This project is licensed under the MIT License.
