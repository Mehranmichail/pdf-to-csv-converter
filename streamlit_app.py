import streamlit as st
import pandas as pd
import pdfplumber
from io import BytesIO
import re

# Page configuration
st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    /* Main container styling */
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Card styling */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Title styling */
    .title-text {
        font-size: 3.5rem;
        font-weight: 700;
        text-align: center;
        color: white;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    
    .subtitle-text {
        font-size: 1.3rem;
        text-align: center;
        color: rgba(255,255,255,0.9);
        margin-bottom: 3rem;
        font-weight: 300;
    }
    
    /* File uploader styling */
    [data-testid="stFileUploader"] {
        background-color: white;
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
    }
    
    /* Button styling */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        font-size: 1.1rem;
        padding: 0.75rem 2rem;
        border-radius: 30px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    
    /* Info box styling */
    .info-box {
        background-color: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 2rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Success message styling */
    .success-box {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
    }
    
    /* Feature cards */
    .feature-card {
        background-color: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="title-text">🏦 Bank Statement Converter</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle-text">Convert your bank PDF statements to Excel with automatic categorization</p>', unsafe_allow_html=True)

# Add some spacing
st.markdown("<br>", unsafe_allow_html=True)

# Main content area
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    # Info note
    st.markdown("""
        <div class="info-box">
            <h3 style="color: #667eea; margin-top: 0;">📌 Important Note</h3>
            <p style="margin-bottom: 0; color: #333;">
                Works with original PDF files downloaded from your bank. 
                For best results, ensure your PDF contains clear tabular data.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # File uploader
    uploaded_file = st.file_uploader(
        "Drop your PDF file here or click to browse",
        type=['pdf'],
        help="Upload a bank statement PDF file (max 200MB)",
        label_visibility="collapsed"
    )
    
    if uploaded_file is not None:
        st.success("✅ File uploaded successfully!")
        
        # Add a convert button
        if st.button("🚀 Convert to CSV", use_container_width=True):
            with st.spinner("⏳ Processing your PDF... This may take a moment."):
                try:
                    # Extract tables from PDF
                    tables = []
                    with pdfplumber.open(uploaded_file) as pdf:
                        for page in pdf.pages:
                            table = page.extract_table()
                            if table:
                                tables.extend(table)
                    
                    if tables:
                        # Convert to DataFrame
                        df = pd.DataFrame(tables[1:], columns=tables[0])
                        
                        # Display preview
                        st.markdown("""
                            <div class="success-box">
                                <h4 style="margin-top: 0;">✨ Conversion Complete!</h4>
                                <p style="margin-bottom: 0;">Preview of your data (first 10 rows):</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.dataframe(df.head(10), use_container_width=True)
                        
                        # Convert to CSV
                        csv = df.to_csv(index=False).encode('utf-8')
                        
                        # Download button
                        st.download_button(
                            label="📥 Download CSV File",
                            data=csv,
                            file_name="converted_statement.csv",
                            mime="text/csv",
                            use_container_width=True
                        )
                        
                        st.balloons()
                    else:
                        st.error("❌ No tables found in the PDF. Please make sure your PDF contains tabular data.")
                
                except Exception as e:
                    st.error(f"❌ Error processing PDF: {str(e)}")
                    st.info("💡 Try a different PDF file or check if the file is corrupted.")

# Features section
st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown('<h2 style="text-align: center; color: white; margin-bottom: 2rem;">✨ Key Features</h2>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🚀</div>
            <h4 style="color: #667eea;">Fast</h4>
            <p style="color: #666; font-size: 0.9rem;">Quick conversion in seconds</p>
        </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🔒</div>
            <h4 style="color: #667eea;">Secure</h4>
            <p style="color: #666; font-size: 0.9rem;">Data processed locally in your browser</p>
        </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">💯</div>
            <h4 style="color: #667eea;">Free</h4>
            <p style="color: #666; font-size: 0.9rem;">No registration required</p>
        </div>
    """, unsafe_allow_html=True)

with col4:
    st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📊</div>
            <h4 style="color: #667eea;">Smart</h4>
            <p style="color: #666; font-size: 0.9rem;">Automatic categorization</p>
        </div>
    """, unsafe_allow_html=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: rgba(255,255,255,0.7); padding: 2rem;">
        <p>Made with ❤️ using Streamlit | <a href="https://github.com/Mehranmichail/pdf-to-csv-converter" style="color: white;">View on GitHub</a></p>
    </div>
""", unsafe_allow_html=True)
