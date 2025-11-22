import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os

st.set_page_config(page_title="The Odissi Architect", layout="wide")
st.title("🎻 The Odissi Architect: Dashboard")

# --- DATA LOADING ---
@st.cache_data
def load_data(base_filename):
    # Load Time-Series Data (Pitch/Formant)
    try:
        df_main = pd.read_csv(f"{base_filename}_analysis.csv")
        # Pitch Norm
        df_main = df_main[df_main['pitch_hz'] > 50]
        df_main['pitch_cents'] = 1200 * np.log2(df_main['pitch_hz'] / 240.0)
        
        # Load Spectral Data (Timbre)
        df_spec = pd.read_csv(f"{base_filename}_spectral.csv")
        
        return df_main, df_spec
    except Exception as e:
        return None, None

# --- SIDEBAR ---
# We look for the _analysis.csv files to list songs
available_songs = [f.replace("_analysis.csv", "") for f in os.listdir('.') if f.endswith('_analysis.csv')]
selected_song = st.sidebar.selectbox("Select Recording", available_songs)

df, df_spec = load_data(selected_song)

if df is not None:
    st.sidebar.success(f"Loaded: {selected_song}")
    
    # --- VISUALIZATIONS ---
    
    # TAB 1: MELODY
    st.header("1. Melodic Contour")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['time_sec'], df['pitch_cents'], color='#d9534f')
    ax.set_ylabel("Cents"); ax.set_xlabel("Time (s)")
    ax.grid(True, alpha=0.3)
    st.pyplot(fig)

    # TAB 2: TIMBRE (THE NEW FEATURE)
    st.header("2. Spectral Fingerprint (Timbre)")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        # Plot Frequency vs Loudness
        ax2.semilogx(df_spec['frequency_hz'], df_spec['amplitude_db'], color='purple', linewidth=2)
        
        # Highlight Ancient vs Modern Zones
        ax2.axvspan(200, 800, color='yellow', alpha=0.2, label="Chest/Warmth (Ancient)")
        ax2.axvspan(2000, 5000, color='green', alpha=0.1, label="Head/Bright (Modern)")
        
        ax2.set_ylabel("Energy (dB)")
        ax2.set_xlabel("Frequency (Hz) - Log Scale")
        ax2.legend()
        ax2.grid(True)
        st.pyplot(fig2)
        
    with col2:
        st.info("""
        **How to read this:**
        - **High bump in Yellow:** Deep, heavy voice (Chest).
        - **High bump in Green:** Bright, nasal voice (Head).
        """)
        
    # TAB 3: FORMANTS
    st.header("3. Vowel Alignment")
    fig3, ax3 = plt.subplots()
    ax3.scatter(df['formant_f2'], df['formant_f1'], c=df['time_sec'], s=5, alpha=0.5)
    ax3.invert_yaxis()
    ax3.set_xlabel("F2 (Brightness)"); ax3.set_ylabel("F1 (Openness)")
    st.pyplot(fig3)

else:
    st.warning("Data not found. Run the Factory v3.0 and upload both CSVs!")
