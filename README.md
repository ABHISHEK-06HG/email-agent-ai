# Email Agent

This project implements an AI-powered email agent that can fetch, summarize, and act upon emails, specifically focusing on scheduling meetings.

## Features

*   **Email Fetching**: Retrieves the latest emails.
*   **Email Summarization**: Summarizes email content using a Generative AI model.
*   **Intent Detection**: Identifies the user's intent from the email (e.g., "schedule_meeting").
*   **Meeting Details Extraction**: Extracts relevant information for meeting scheduling (date, time, duration, subject).
*   **Meeting Scheduling**: Integrates with Google Calendar to schedule meetings.
*   **Conditional Routing**: Uses a graph-based approach to route tasks based on detected intent.

## Setup Instructions

To set up and run this project, please follow these steps:

### 1. Clone the Repository

```bash
git clone <repository_url>
cd emailabhishekhg
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to manage dependencies.

```bash
python -m venv venv
```

### 3. Activate the Virtual Environment

*   **On Windows:**
    ```bash
    .\venv\Scripts\activate
    ```
*   **On macOS/Linux:**
    ```bash
    source venv/bin/activate
    ```

### 4. Install Dependencies

Install the required Python packages using `requirements.txt`:

```bash
pip install -r requirements.txt
```

### 5. Google API Credentials Setup

This project uses Google Calendar API. You need to set up Google API credentials:

1.  Go to the [Google Cloud Console](https://console.cloud.google.com/).
2.  Create a new project or select an existing one.
3.  Enable the **Google Calendar API**.
4.  Go to "Credentials" and create a new **OAuth client ID** for a "Desktop app".
5.  Download the `credentials.json` file and place it in the project's root directory (`emailabhishekhg/`).

### 6. Google Generative AI API Key Setup

This project uses Google Generative AI for email summarization.

1.  Obtain an API key from the [Google AI Studio](https://aistudio.google.com/app/apikey).
2.  Set your API key as an environment variable:

    *   **On Windows (PowerShell):**
        ```bash
        $env:GOOGLE_API_KEY="YOUR_API_KEY"
        ```
    *   **On macOS/Linux:**
        ```bash
        export GOOGLE_API_KEY="YOUR_API_KEY"
        ```
    Replace `YOUR_API_KEY` with your actual API key.

### 7. Run the Application

#### Running the Email Agent (CLI)

Once everything is set up, you can run the main application:

```bash
python main.py
```

This will fetch an email, summarize it, detect the intent, and if the intent is to schedule a meeting, it will attempt to schedule it in your Google Calendar.

#### Running the Web API (Frontend Integration)

To integrate with a web frontend, you can run the Flask API:

```bash
python app.py
```

This will start a Flask development server, typically at `http://127.0.0.1:5000`. Your frontend can then send `POST` requests to `http://127.0.0.1:5000/process_email` with a JSON body containing the `email_content`.

Example `POST` request body:

```json
{
    "email_content": "Your email content here"
}
```

The API will respond with a JSON object representing the final state of the email processing.

## Project Structure

*   `main.py`: The entry point of the application, orchestrating the email agent workflow.
*   `app.py`: Flask web application for frontend integration.
*   `nodes/`: Contains individual processing nodes for the graph (e.g., `summarize_email.py`, `detect_intent.py`, `schedule_meeting.py`).
*   `utils/`: Contains utility functions, such as `google_auth.py` for Google API authentication.
*   `requirements.txt`: Lists all Python dependencies.
*   `credentials.json`: Google API credentials (downloaded from Google Cloud Console).
*   `token.pickle` or `token.pkl`: Stores Google API authentication tokens after the first successful authentication.

## How it Works

The application uses a graph-based approach (powered by `langgraph`) to define the flow of email processing. Each step (fetching, summarizing, intent detection, scheduling, displaying summary) is a "node" in the graph. The graph dynamically routes the email through these nodes based on the detected intent.