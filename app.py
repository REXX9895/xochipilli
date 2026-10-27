import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

# ---------------------------------------------------------
# XOCHIPILLI | Class XII Informatics Practices Project
# ---------------------------------------------------------
st.set_page_config(
    page_title="Xochipilli | Spotify Song Analysis",
    page_icon="🎧",
    layout="wide",
    initial_sidebar_state="expanded",
)

GREEN = "#1ED760"
DARK_GREEN = "#087F3E"
PLOT_TEMPLATE = "plotly_dark"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] {{ font-family: 'DM Sans', sans-serif; }}
    .stApp {{ background: radial-gradient(ellipse at top left, #17251c 0%, #101010 42%); color: #F5F5F5; }}
    [data-testid="stSidebar"] {{ background: #171717; border-right: 1px solid #292929; }}
    h1, h2, h3 {{ color: {GREEN} !important; }}
    .hero {{
        padding: 1.4rem 1.6rem; border-radius: 22px;
        background: linear-gradient(115deg, #1d3928 0%, #142018 48%, #202020 100%);
        border: 1px solid #2c4935; margin-bottom: 1rem;
    }}
    .hero-kicker {{ color: {GREEN}; text-transform: uppercase; letter-spacing: 2px;
        font-size: .75rem; font-weight: 700; }}
    .hero h1 {{ margin: .25rem 0 .3rem 0; font-size: clamp(2rem, 4vw, 3.1rem); }}
    .hero p {{ color: #c9d2cb; margin: 0; font-size: 1rem; }}
    div[data-testid="stMetric"] {{
        background: linear-gradient(145deg, #202020, #181818);
        border: 1px solid #303830; padding: 16px 18px; border-radius: 16px;
    }}
    div[data-testid="stMetricValue"] {{ color: {GREEN}; }}
    div[data-testid="stMetricLabel"] {{ color: #c5c5c5; }}
    .stButton button, .stDownloadButton button {{
        background: {GREEN}; color: #101010; border-radius: 24px;
        border: none; font-weight: 700;
    }}
    .stButton button:hover, .stDownloadButton button:hover {{
        background: #55ed89; color: #101010; border: none;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: {GREEN}; border-bottom-color: {GREEN};
    }}
    .small-note {{ color: #a6a6a6; font-size: .85rem; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="hero">
      <div class="hero-kicker">Music • Data • Discovery</div>
      <h1>🎧 Xochipilli</h1>
      <p>Discover the data behind the music — an interactive Spotify tracks analysis dashboard.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# -------------------------- Data loading --------------------------
@st.cache_data(show_spinner=False)
def read_csv(source):
    return pd.read_csv(source)

def clean_data(source_df):
    df = source_df.copy()
    df.columns = [str(col).strip().lower() for col in df.columns]
    if "unnamed: 0" in df.columns:
        df = df.drop(columns=["unnamed: 0"])

    numeric_columns = [
        "popularity", "duration_ms", "danceability", "energy", "loudness",
        "speechiness", "acousticness", "instrumentalness", "liveness",
        "valence", "tempo", "key", "mode", "time_signature",
    ]
    for col in numeric_columns:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    for col in ["track_name", "artists", "track_genre", "album_name"]:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype(str).str.strip()
    if "track_name" in df.columns:
        df = df[df["track_name"].ne("")]
    if "popularity" in df.columns:
        df = df.dropna(subset=["popularity"])
    return df

with st.sidebar:
    st.markdown("## ⚙️ Dashboard controls")
    uploaded_file = st.file_uploader("Upload your Spotify CSV", type=["csv"])
    st.caption("Tip: You can upload a file here or place `dataset.csv` beside `app.py`.")
    st.divider()
    st.markdown("### 🎛️ Filters")

try:
    if uploaded_file is not None:
        raw_df = read_csv(uploaded_file)
        data_source = uploaded_file.name
    else:
        csv_path = Path(__file__).with_name("dataset.csv")
        if not csv_path.exists():
            st.info("**Ready when you are!** Upload a Spotify CSV using the sidebar to start exploring.")
            st.markdown(
                """
                **Expected columns**
                - Required: `track_name`, `artists`, `popularity`, `track_genre`
                - Optional: `album_name`, `duration_ms`, `danceability`, `energy`, `valence`,
                  `tempo`, `acousticness`, `instrumentalness`, `speechiness`, `liveness`
                """
            )
            st.stop()
        raw_df = read_csv(csv_path)
        data_source = "dataset.csv"
    df = clean_data(raw_df)
except Exception as error:
    st.error(f"Could not read this CSV file: {error}")
    st.stop()

required_columns = ["track_name", "artists", "popularity", "track_genre"]
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    st.error("This CSV is missing required columns: " + ", ".join(missing_columns))
    st.info("Please use a Spotify tracks dataset containing the required columns.")
    st.stop()

if df.empty:
    st.error("No usable tracks were found. Check that your CSV contains track names and numeric popularity values.")
    st.stop()

# -------------------------- Sidebar filters --------------------------
with st.sidebar:
    genres = sorted(df["track_genre"].dropna().astype(str).unique().tolist())
    selected_genres = st.multiselect("Genre", genres, default=[], help="Leave empty to include every genre.")

    min_pop = int(df["popularity"].min())
    max_pop = int(df["popularity"].max())
    if min_pop == max_pop:
        pop_range = (min_pop, max_pop)
        st.caption(f"Popularity: {min_pop} (only one value in this dataset)")
    else:
        pop_range = st.slider(
            "Popularity range",
            min_value=min_pop,
            max_value=max_pop,
            value=(min_pop, max_pop),
        )

    search_text = st.text_input("🔎 Search track or artist", placeholder="Type a name...")
    sort_choice = st.selectbox(
        "Sort tracks by",
        ["Popularity (high to low)", "Popularity (low to high)", "Track name (A–Z)"],
    )
    st.divider()
    st.caption(f"📁 Source: {data_source}")
    st.caption(f"🧾 Raw rows: {len(df):,}")

filtered = df[df["popularity"].between(pop_range[0], pop_range[1])].copy()
if selected_genres:
    filtered = filtered[filtered["track_genre"].astype(str).isin(selected_genres)]
if search_text.strip():
    search_mask = (
        filtered["track_name"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
        | filtered["artists"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
    )
    filtered = filtered[search_mask]

if filtered.empty:
    st.warning("No tracks match the current filters. Try widening the popularity range or clearing the search.")
    st.stop()

if sort_choice == "Popularity (high to low)":
    filtered = filtered.sort_values("popularity", ascending=False)
elif sort_choice == "Popularity (low to high)":
    filtered = filtered.sort_values("popularity", ascending=True)
else:
    filtered = filtered.sort_values("track_name", ascending=True)

# -------------------------- Metrics --------------------------
st.caption(f"Showing results from **{data_source}** based on your current filters.")
metric_cols = st.columns(4)
metric_cols[0].metric("🎵 Tracks in view", f"{len(filtered):,}")
metric_cols[1].metric("⭐ Avg. popularity", f"{filtered['popularity'].mean():.1f}")
metric_cols[2].metric("🎼 Genres in view", f"{filtered['track_genre'].nunique():,}")
if "artists" in filtered:
    metric_cols[3].metric("🎤 Unique artists", f"{filtered['artists'].nunique():,}")

tabs = st.tabs([
    "🏠 Overview",
    "🎼 Genre insights",
    "🎚️ Audio lab",
    "🎤 Artist rankings",
    "🔎 Track explorer",
])

# -------------------------- Overview --------------------------
with tabs[0]:
    st.subheader("Your music at a glance")
    left, right = st.columns([1.25, 1])
    with left:
        st.markdown("#### Most popular tracks")
        top_tracks = filtered.nlargest(10, "popularity").copy()
        hover_cols = [c for c in ["artists", "track_genre", "album_name"] if c in top_tracks.columns]
        fig = px.bar(
            top_tracks.sort_values("popularity"),
            x="popularity", y="track_name", orientation="h",
            color="popularity", color_continuous_scale=[DARK_GREEN, GREEN],
            hover_data=hover_cols, labels={"track_name": "Track", "popularity": "Popularity"},
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=440, coloraxis_showscale=False,
                          margin=dict(l=8, r=8, t=20, b=10), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### Popularity spread")
        fig = px.histogram(
            filtered, x="popularity", nbins=20,
            color_discrete_sequence=[GREEN],
            labels={"popularity": "Popularity score", "count": "Number of tracks"},
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=440,
                          margin=dict(l=8, r=8, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)

    if "duration_ms" in filtered:
        durations = filtered["duration_ms"].dropna()
        if not durations.empty:
            avg_minutes = durations.mean() / 60000
            median_minutes = durations.median() / 60000
            d1, d2, d3 = st.columns(3)
            d1.metric("⏱️ Average duration", f"{avg_minutes:.2f} min")
            d2.metric("Median duration", f"{median_minutes:.2f} min")
            d3.metric("Longest track", f"{durations.max()/60000:.2f} min")
    st.markdown("#### Quick facts")
    q1, q2 = st.columns(2)
    q1.info(f"**Most represented genre:** {filtered['track_genre'].value_counts().idxmax()}")
    q2.info(f"**Highest popularity in view:** {filtered['popularity'].max():.0f} / 100")

# -------------------------- Genre insights --------------------------
with tabs[1]:
    st.subheader("Explore music by genre")
    genre_counts = (
        filtered["track_genre"].value_counts().head(20)
        .rename_axis("Genre").reset_index(name="Tracks")
    )
    genre_left, genre_right = st.columns(2)
    with genre_left:
        st.markdown("#### Genres with the most tracks")
        fig = px.bar(
            genre_counts.sort_values("Tracks"), x="Tracks", y="Genre", orientation="h",
            color="Tracks", color_continuous_scale=[DARK_GREEN, GREEN],
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=580, coloraxis_showscale=False,
                          margin=dict(l=8, r=8, t=20, b=10))
        st.plotly_chart(fig, use_container_width=True)
    with genre_right:
        st.markdown("#### Average popularity by genre")
        genre_pop = (
            filtered.groupby("track_genre", as_index=False)["popularity"].mean()
            .sort_values("popularity", ascending=False).head(20)
        )
        fig = px.bar(
            genre_pop.sort_values("popularity"), x="popularity", y="track_genre",
            orientation="h", color_discrete_sequence=[GREEN],
            labels={"track_genre": "Genre", "popularity": "Average popularity"},
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=580,
                          margin=dict(l=8, r=8, t=20, b=10), yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown("#### Genre summary table")
    summary = filtered.groupby("track_genre").agg(
        Tracks=("track_name", "count"),
        Average_popularity=("popularity", "mean"),
        Unique_artists=("artists", "nunique"),
    ).reset_index().sort_values("Tracks", ascending=False)
    summary["Average_popularity"] = summary["Average_popularity"].round(2)
    st.dataframe(summary, use_container_width=True, hide_index=True)

# -------------------------- Audio lab --------------------------
with tabs[2]:
    st.subheader("What does the music sound like?")
    feature_labels = {
        "danceability": "Danceability",
        "energy": "Energy",
        "speechiness": "Speechiness",
        "acousticness": "Acousticness",
        "instrumentalness": "Instrumentalness",
        "liveness": "Liveness",
        "valence": "Valence (musical positivity)",
        "tempo": "Tempo (BPM)",
        "loudness": "Loudness (dB)",
    }
    available_features = [c for c in feature_labels if c in filtered.columns and filtered[c].notna().any()]
    if available_features:
        chosen_feature = st.selectbox(
            "Select an audio feature",
            available_features,
            format_func=lambda x: feature_labels[x],
        )
        feature_values = filtered[chosen_feature].dropna()
        fig = px.histogram(
            feature_values, x=chosen_feature, nbins=30,
            color_discrete_sequence=[GREEN],
            title=f"Distribution of {feature_labels[chosen_feature]}",
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=390,
                          yaxis_title="Number of tracks", margin=dict(l=8, r=8, t=55, b=10))
        st.plotly_chart(fig, use_container_width=True)
        st.caption(f"Average {feature_labels[chosen_feature].lower()}: **{feature_values.mean():.2f}**")
    else:
        st.info("No supported audio-feature columns were found in this CSV.")

    if {"energy", "danceability"}.issubset(filtered.columns):
        st.markdown("#### Energy vs danceability")
        scatter_cols = ["energy", "danceability", "popularity"]
        scatter_cols += [c for c in ["track_name", "track_genre", "artists"] if c in filtered.columns]
        sample = filtered[scatter_cols].dropna(subset=["energy", "danceability", "popularity"]).copy()
        if len(sample) > 5000:
            sample = sample.sample(5000, random_state=42)
        if not sample.empty:
            fig = px.scatter(
                sample, x="danceability", y="energy", color="popularity",
                hover_data=[c for c in ["track_name", "track_genre", "artists"] if c in sample.columns],
                color_continuous_scale=[DARK_GREEN, GREEN], opacity=0.7,
                labels={"danceability": "Danceability", "energy": "Energy"},
            )
            fig.update_layout(template=PLOT_TEMPLATE, height=500, margin=dict(l=8, r=8, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)

    available_corr = [c for c in available_features if pd.api.types.is_numeric_dtype(filtered[c])]
    if len(available_corr) >= 2:
        st.markdown("#### Audio-feature correlation")
        corr = filtered[available_corr].corr(numeric_only=True)
        fig = px.imshow(
            corr, text_auto=".2f", aspect="auto", color_continuous_scale="Greens",
            labels={"color": "Correlation"},
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=500)
        st.plotly_chart(fig, use_container_width=True)
        st.caption("Correlation shows how two numeric features vary together; it does not prove cause and effect.")

# -------------------------- Artist rankings --------------------------
with tabs[3]:
    st.subheader("Artist leaderboard")
    artist_counts = (
        filtered.groupby("artists", as_index=False)
        .agg(Track_count=("track_name", "count"), Average_popularity=("popularity", "mean"))
    )
    artist_counts["Average_popularity"] = artist_counts["Average_popularity"].round(2)
    artist_counts = artist_counts.sort_values(["Track_count", "Average_popularity"], ascending=False)
    top_n = st.slider("Number of artists to show", min_value=5, max_value=30, value=10, step=5)
    artist_left, artist_right = st.columns(2)
    with artist_left:
        st.markdown("#### Artists with the most tracks")
        fig = px.bar(
            artist_counts.head(top_n).sort_values("Track_count"),
            x="Track_count", y="artists", orientation="h",
            color_discrete_sequence=[GREEN],
            labels={"artists": "Artist", "Track_count": "Tracks"},
        )
        fig.update_layout(template=PLOT_TEMPLATE, height=500, yaxis_title="")
        st.plotly_chart(fig, use_container_width=True)
    with artist_right:
        st.markdown("#### Artists by average popularity")
        popular_artists = artist_counts[artist_counts["Track_count"] >= 2].nlargest(top_n, "Average_popularity")
        if popular_artists.empty:
            st.info("Not enough artists with multiple tracks to calculate this ranking.")
        else:
            fig = px.bar(
                popular_artists.sort_values("Average_popularity"),
                x="Average_popularity", y="artists", orientation="h",
                color_discrete_sequence=[GREEN],
                labels={"artists": "Artist", "Average_popularity": "Average popularity"},
            )
            fig.update_layout(template=PLOT_TEMPLATE, height=500, yaxis_title="")
            st.plotly_chart(fig, use_container_width=True)
    st.dataframe(artist_counts, use_container_width=True, hide_index=True)

# -------------------------- Track explorer --------------------------
with tabs[4]:
    st.subheader("Find, sort and export tracks")
    display_columns = [
        "track_name", "artists", "album_name", "track_genre", "popularity",
        "duration_ms", "explicit", "danceability", "energy", "valence", "tempo",
    ]
    display_columns = [c for c in display_columns if c in filtered.columns]
    track_table = filtered[display_columns].copy()
    if "duration_ms" in track_table.columns:
        track_table["duration_seconds"] = (track_table.pop("duration_ms") / 1000).round(1)
    st.caption(f"{len(track_table):,} tracks match your current filters.")
    st.dataframe(track_table, use_container_width=True, hide_index=True)
    csv_output = track_table.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Download filtered tracks as CSV",
        data=csv_output,
        file_name="xochipilli_filtered_tracks.csv",
        mime="text/csv",
    )

    if "popularity" in filtered.columns:
        st.markdown("#### Download the complete cleaned dataset")
        full_table = df.copy()
        st.download_button(
            "⬇️ Download cleaned dataset",
            data=full_table.to_csv(index=False).encode("utf-8"),
            file_name="xochipilli_cleaned_dataset.csv",
            mime="text/csv",
        )

st.divider()
with st.expander("ℹ️ About Xochipilli"):
    st.write(
        """
        Xochipilli is a Class XII Informatics Practices project that demonstrates data handling
        and visualisation using Python. Pandas cleans and analyses the CSV dataset, Streamlit
        builds the interactive website, and Plotly creates interactive charts. The results
        describe the dataset supplied by the user and are not live Spotify data.
        """
    )
    st.markdown("**Technologies used:** Python · Pandas · Streamlit · Plotly · CSV")
st.markdown(
    '<p class="small-note">Made for a Class XII Informatics Practices project • Xochipilli 🎧</p>',
    unsafe_allow_html=True,
)
