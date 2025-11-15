import streamlit as st
import pdfplumber
import pandas as pd
import csv
import io
import re
from typing import List, Tuple

# Page configuration
st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="📄",
    layout="centered"
)

# Custom CSS for professional look
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        max-width: 900px;
        margin: 0 auto;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 3rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .subtitle {
        color: rgba(255,255,255,0.95);
        text-align: center;
        font-size: 1.2rem;
        margin-bottom: 2rem;
    }
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        font-size: 1.1rem;
        border-radius: 8px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.3);
    }
    </style>
    """, unsafe_allow_html=True)

class SmartPDFConverter:
    """Professional PDF to CSV converter with smart extraction."""
    
    def is_date(self, text: str) -> bool:
        """Check if text looks like a date."""
        if not text or not str(text).strip():
            return False
        
        text = str(text).strip()
        date_patterns = [
            r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',
            r'^\d{1,2}/\d{1,2}/\d{2,4}$',
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{1,2}-\d{1,2}-\d{2,4}$',
            r'^\d{1,2}-(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)-\d{2}$',
        ]
        return any(re.match(pattern, text) for pattern in date_patterns)
    
    def has_amount(self, text: str) -> bool:
        """Check if text looks like a monetary amount."""
        if not text:
            return False
        text = str(text).strip()
        return bool(re.match(r'^[\d,]+\.?\d{0,2}$', text))
    
    def is_transaction_row(self, row: List[str]) -> bool:
        """Determine if a row is a transaction."""
        if not row or len(row) < 3:
            return False
        clean_row = [cell for cell in row if cell and str(cell).strip()]
        if len(clean_row) < 3:
            return False
        if not self.is_date(clean_row[0]):
            return False
        return any(self.has_amount(cell) for cell in clean_row[2:])
    
    def is_junk_row(self, row: List[str]) -> bool:
        """Determine if a row is junk."""
        if not row:
            return True
        row_text = ' '.join(str(cell).lower() for cell in row if cell).strip()
        if not row_text or len(row_text) < 5:
            return True
        
        junk_keywords = [
            'page', 'business owner', 'account number', 'sort code', 
            'statement for', 'total paid', 'transactions',
            'bank account legal', 'clearbank', 'tide', 'fscs',
            'to be billed', 'transaction fee', 'regulation',
            'your tide account', 'registered', 'authorised',
            'balance (£) on'
        ]
        return any(keyword in row_text for keyword in junk_keywords)
    
    def clean_cell(self, cell) -> str:
        """Clean individual cell content."""
        if cell is None:
            return ''
        text = str(cell).strip()
        text = ' '.join(text.split())
        return text
    
    def extract_transaction_from_row(self, row: List[str]) -> List[str]:
        """Extract transaction data from raw PDF row."""
        while len(row) < 7:
            row.append('')
        
        date = self.clean_cell(row[0])
        trans_type = self.clean_cell(row[1])
        details = self.clean_cell(row[2])
        paid_in = self.clean_cell(row[4]) if len(row) > 4 else ''
        paid_out = self.clean_cell(row[5]) if len(row) > 5 else ''
        balance = self.clean_cell(row[6]) if len(row) > 6 else ''
        
        if not balance:
            for i in range(len(row) - 1, 2, -1):
                if row[i] and self.has_amount(str(row[i])):
                    balance = self.clean_cell(row[i])
                    break
        
        return [date, trans_type, details, paid_in, paid_out, balance]
    
    def extract_smart_transactions(self, pdf_file) -> Tuple[List[str], List[List[str]]]:
        """Extract transactions using actual Paid In/Out columns from PDF."""
        all_transactions = []
        header = ['Date', 'Transaction Type', 'Details', 'Paid In', 'Paid Out', 'Balance']
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    for row in table:
                        if not row:
                            continue
                        
                        clean_row = [self.clean_cell(cell) for cell in row]
                        if self.is_junk_row(clean_row):
                            continue
                        
                        if self.is_transaction_row(clean_row):
                            transaction = self.extract_transaction_from_row(row)
                            all_transactions.append(transaction)
        
        return header, all_transactions
    
    def convert_to_csv(self, pdf_file) -> str:
        """Convert PDF to clean CSV."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)
        writer.writerows(transactions)
        
        return output.getvalue()
    
    def convert_to_excel(self, pdf_file) -> bytes:
        """Convert PDF to clean Excel."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        df = pd.DataFrame(transactions, columns=header)
        
        for col in df.columns:
            if 'paid' in col.lower() or 'balance' in col.lower():
                df[col] = df[col].str.replace(',', '')
        
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transactions')
            
            worksheet = writer.sheets['Transactions']
            for idx, col in enumerate(df.columns):
                max_length = max(df[col].astype(str).apply(len).max(), len(col))
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        return output.getvalue()

# Header
st.markdown("<h1>📄 PDF to CSV Converter</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Transform your bank statements into clean, ready-to-use spreadsheets</p>", unsafe_allow_html=True)

# Main container
with st.container():
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a bank statement or transaction PDF"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        conversion_mode = st.selectbox(
            "📊 Conversion Mode",
            options=['Smart (Clean Transactions)', 'Standard (All Data)'],
            index=0
        )
    
    with col2:
        output_format = st.selectbox(
            "📁 Output Format",
            options=['CSV', 'Excel'],
            index=0
        )
    
    if conversion_mode == 'Smart (Clean Transactions)':
        st.info("🧠 **Smart Mode:** Automatically removes headers, footers, and junk data. Perfect for bank statements!")
    
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🚀 Convert Now", type="primary", use_container_width=True):
                try:
                    with st.spinner('⚡ Converting your PDF...'):
                        converter = SmartPDFConverter()
                        
                        if conversion_mode == 'Smart (Clean Transactions)':
                            if output_format == 'Excel':
                                excel_data = converter.convert_to_excel(uploaded_file)
                                
                                st.success('✅ Conversion complete!')
                                
                                st.download_button(
                                    label="⬇️ Download Excel",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                st.subheader("📋 Preview")
                                header, transactions = converter.extract_smart_transactions(uploaded_file)
                                df_preview = pd.DataFrame(transactions[:10], columns=header)
                                st.dataframe(df_preview, use_container_width=True)
                                
                                st.metric("📊 Total Transactions", len(transactions))
                                
                            else:
                                csv_content = converter.convert_to_csv(uploaded_file)
                                
                                st.success('✅ Conversion complete!')
                                
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_content,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                st.subheader("📋 Preview (First 10 rows)")
                                preview_lines = csv_content.split('\n')[:11]
                                st.text('\n'.join(preview_lines))
                                
                                row_count = len(csv_content.split('\n')) - 1
                                st.metric("📊 Total Transactions", row_count)
                        
                        else:
                            all_rows = []
                            with pdfplumber.open(uploaded_file) as pdf:
                                for page in pdf.pages:
                                    tables = page.extract_tables()
                                    for table in tables:
                                        if table:
                                            all_rows.extend(table)
                            
                            if output_format == 'Excel':
                                df = pd.DataFrame(all_rows[1:], columns=all_rows[0] if all_rows else [])
                                output = io.BytesIO()
                                df.to_excel(output, index=False)
                                excel_data = output.getvalue()
                                
                                st.success('✅ Conversion complete!')
                                st.download_button(
                                    label="⬇️ Download Excel",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_output.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                            else:
                                output = io.StringIO()
                                writer = csv.writer(output)
                                writer.writerows(all_rows)
                                csv_content = output.getvalue()
                                
                                st.success('✅ Conversion complete!')
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_content,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_output.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    st.info("💡 Try switching to Standard mode or check if your PDF is valid")

# Features section
st.markdown("---")
st.markdown("### ✨ Key Features")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    **🎯 Smart Extraction**
    - Auto-detects transactions
    - Removes junk data
    - Perfect for bank statements
    """)

with col2:
    st.markdown("""
    **⚡ Fast & Easy**
    - Upload PDF
    - Click convert
    - Download instantly
    """)

with col3:
    st.markdown("""
    **📊 Multiple Formats**
    - CSV export
    - Excel export
    - Clean data ready to use
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.8); font-size: 0.9rem;'>"
    "Built with ❤️ using Streamlit • Powered by pdfplumber"
    "</p>",
    unsafe_allow_html=True
)
