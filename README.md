# Masters_GenAI_Capstone1

Simple Streamlit app that provides insights from a car sales dataset. Use the app to run safe read-only SQL queries and view results.

Quick start
- Install dependencies: pip install -r requirements.txt
- Run locally: streamlit run app.py
- Or with Docker: build the image and run it (container serves on port 8080 by default)

Notes
- The app uses `data_insights.db` (SQLite). Do not run destructive SQL from the UI.
- Secrets (OpenAI key, GitHub token) are read from environment variables via a .env file.

That's it, the less is more :)
