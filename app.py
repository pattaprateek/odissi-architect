import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

# --- 1. APP CONFIGURATION ---
st.set_page_config(page_title="The Odissi Architect", layout="wide")
st.title("🎻 The Odissi Architect: Dashboard")
st.markdown("### Analysis")

# --- 2. DATA LOADING FUNCTION ---
@st.cache_data
def load_analysis_data(file_input):
    """Loads the analysis CSV (from path or uploaded file) and cleans data."""
    try:
        df = pd.read_csv(file_input)
        
        # Normalize Pitch (Hz -> Cents) relative to a baseline Sa (240Hz)
        TONIC_HZ = 240.0 
        # Filter silence/noise
        df = df[df['pitch_hz'] > 50]
        df['pitch_cents'] = 1200 * np.log2(df['pitch_hz'] / TONIC_HZ)
        
        # Clean Formants
        df['formant_f1'] = df['formant_f1'].replace(0, np.nan)
        df['formant_f2'] = df['formant_f2'].replace(0, np.nan)
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None

# --- 3. SIDEBAR: DATA SELECTION ---
st.sidebar.header("Data Source")

# Option A: Scan GitHub Repo for files
repo_files = [f for f in os.listdir('.') if f.endswith('_analysis.csv')]

# Option B: Upload a file manually
uploaded_file = st.sidebar.file_uploader("📂 Drag & Drop a CSV here", type=["csv"])

df = None
selected_filename = ""

if uploaded_file is not None:
    # Priority 1: Use the uploaded file
    df = load_analysis_data(uploaded_file)
    selected_filename = uploaded_file.name

elif repo_files:
    # Priority 2: Use files found in the GitHub repository
    selected_file = st.sidebar.selectbox("Or select from Archive:", repo_files)
    df = load_analysis_data(selected_file)
    selected_filename = selected_file

else:
    st.info("👈 Please upload a CSV file to the sidebar to begin.")
    st.stop()

if df is not None:
    # Extract Metadata if available, or use Filename
    artist = df['artist'].iloc[0] if 'artist' in df.columns else "Unknown"
    title = df['title'].iloc[0] if 'title' in df.columns else selected_filename
    st.sidebar.success(f"Loaded: {title}")

# --- 4. VISUALIZATIONS ---

if df is not None:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.subheader("Melodic Contour (Gamaka Trace)")
        
        fig, ax = plt.subplots(figsize=(10, 5))
        # Plot Pitch Curve
        ax.plot(df['time_sec'], df['pitch_cents'], color='#d9534f', linewidth=1.5, label='Pitch')
        
        # Reference Lines (Sa and Pa)
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5, label='Sa')
        ax.axhline(y=702, color='gray', linestyle=':', alpha=0.5, label='Pa')
        
        ax.set_ylabel("Cents")
        ax.set_xlabel("Time (s)")
        ax.legend()
        ax.grid(True, alpha=0.3)
        st.pyplot(fig)

    with col2:
        st.subheader("Vowel Fidelity (Ancient Sound)")
        
        fig2, ax2 = plt.subplots(figsize=(5, 5))
        # Scatter plot of F1 vs F2
        scatter = ax2.scatter(df['formant_f2'], df['formant_f1'], 
                              c=df['time_sec'], cmap='viridis', s=10, alpha=0.6)
        
        ax2.invert_yaxis() # Standard linguistic plot
        ax2.set_xlabel("F2 (Tongue Frontness)")
        ax2.set_ylabel("F1 (Jaw Openness)")
        
        # Reference Zones
        ax2.text(2500, 300, 'Bright/Head', color='green', fontsize=8)
        ax2.text(1000, 800, 'Dark/Chest', color='blue', fontsize=8)
        
        st.pyplot(fig2)

    st.info("Tip: The 'Dark/Ancient' zone (Low F2) indicates the heavy chest resonance used by Old Masters.")
