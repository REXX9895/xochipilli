# Xochipilli — Spotify Song Analysis

Class XII Informatics Practices project built with Python, Streamlit, Pandas, Plotly, and CSV data.

## Files
- `app.py` — the Streamlit website
- `requirements.txt` — required Python packages
- `dataset.csv` — add your own Spotify dataset here (not included)

## Run on Windows
1. Install Python and make sure it is available from Command Prompt.
2. Put your Spotify CSV file in this folder and name it `dataset.csv`, or upload it from the app sidebar.
3. Open Command Prompt in this folder.
4. Install dependencies:
   `python -m pip install -r requirements.txt`
5. Start the website:
   `python -m streamlit run app.py`
6. Open `http://localhost:8501` if the browser does not open automatically.

If `python` does not work, replace `python` with the full path to your Python executable.

## Required CSV columns
- `track_name`
- `artists`
- `popularity`
- `track_genre`

Optional columns include `album_name`, `duration_ms`, `danceability`, `energy`, `speechiness`, `acousticness`, `instrumentalness`, `liveness`, `valence`, `tempo`, `loudness`, and `explicit`.

This app analyses the supplied CSV; it does not connect to Spotify or show live Spotify data.
