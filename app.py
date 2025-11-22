import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import librosa
import librosa.display

st.set_page_config(page_title="The Odissi Architect", layout="wide")
st.title("🎻 The Odissi Architect: Dashboard")

# --- HELPER: ARC DIAGRAM (MOTIF DISCOVERY) ---
def plot_structure(pitch_seq, time_seq):
    """
    Generates a Self-Similarity Matrix to find Motifs.
    """
    # 1. Downsample pitch to speed up calculation (10Hz is enough for structure)
    hop = 10 
    pitch_small = pitch_seq[::hop]
    time_small = time_seq[::hop]
    
    # 2. Calculate Self-Similarity (Recurrence)
    # We compare every point to every other point
    # Using Euclidean distance on Cents
    if len(pitch_small) < 100: return None # Too short
    
    recurrence = librosa.segment.recurrence_matrix(
        pitch_small.reshape(1, -1), 
        mode='affinity', 
        width=5, # Minimum motif width
        metric='euclidean'
    )
    
    # 3. Plot
    fig, ax = plt.subplots(figsize=(10, 6))
    librosa.display.specshow(recurrence, x_axis='time', y_axis='time', 
                             x_coords=time_small, y_coords=time_small, ax=ax, cmap='magma_r')
    ax.set_title("Structure & Motif Repetition (Darker = Match)")
    ax.set_xlabel("Time (s)")
    ax.set_ylabel("Time (s)")
    return fig

# --- LOADING ---
uploaded_file = st.sidebar.file_uploader("Upload Analysis CSV", type=["csv"])

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    
    # 1. GET TONIC (From CSV Metadata)
    if 'detected_tonic' in df.columns:
        tonic = df['detected_tonic'].iloc[0]
        st.sidebar.success(f"Tonic Detected: {tonic:.1f} Hz")
    else:
        tonic = 240.0 # Fallback
        st.sidebar.warning("Tonic not found in file. Using default 240Hz.")

    # 2. NORMALIZE
    df = df[df['pitch_hz'] > 50]
    df['pitch_cents'] = 1200 * np.log2(df['pitch_hz'] / tonic)
    
    # --- TABS ---
    tab1, tab2, tab3 = st.tabs(["Melody", "Motifs (Structure)", "Timbre"])
    
    with tab1:
        st.subheader("Melodic Contour")
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(df['time_sec'], df['pitch_cents'], color='#d9534f')
        ax.axhline(0, color='gray', linestyle='--', label='Sa')
        ax.axhline(702, color='gray', linestyle=':', label='Pa')
        ax.legend()
        st.pyplot(fig)
        
    with tab2:
        st.subheader("Pattern Discovery (Arc Matrix)")
        st.markdown("""
        **How to read this:**
        - **Diagonal Line:** The song playing forward.
        - **Dark Squares off-diagonal:** Phrases that repeat. 
        - *If you see a box at (X=10s, Y=40s), the phrase at 10s returns at 40s (Pallavi).*
        """)
        fig_struct = plot_structure(df['pitch_cents'].values, df['time_sec'].values)
        if fig_struct:
            st.pyplot(fig_struct)
        else:
            st.warning("Song too short for structure analysis.")

    with tab3:
        st.subheader("Vowel Fidelity")
        fig2, ax2 = plt.subplots()
        ax2.scatter(df['formant_f2'], df['formant_f1'], c=df['time_sec'], s=5, alpha=0.5)
        ax2.invert_yaxis()
        st.pyplot(fig2)
