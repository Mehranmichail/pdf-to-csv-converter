import streamlit as st
import pdfplumber
import pandas as pd
import csv
import io
import re
from typing import List, Tuple
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="PDF to CSV Converter",
    page_icon="📄",
    layout="centered"
)

# Custom CSS
st.markdown("""
    <style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
    }
    .stApp {
        max-width: 800px;
        margin: 0 auto;
    }
    h1 {
        color: white;
        text-align: center;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: rgba(255,255,255,0.9);
        text-align: center;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }
    </style>
    """, unsafe_allow_html=True)

class SmartPDFConverter:
    """Smart PDF to CSV converter with automatic transaction detection and cleaning."""
    
    def is_date(self, text: str) -> bool:
        """Check if text looks like a date."""
        if not text or not str(text).strip():
            return False
        
        text = str(text).strip()
        
        # Common date patterns
        date_patterns = [
            r'^\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}$',  # 29 Apr 2025
            r'^\d{1,2}/\d{1,2}/\d{2,4}$',  # 29/04/2025
            r'^\d{4}-\d{2}-\d{2}$',  # 2025-04-29
            r'^\d{1,2}-\d{1,2}-\d{2,4}$',  # 29-04-2025
        ]
        
        return any(re.match(pattern, text) for pattern in date_patterns)
    
    def has_amount(self, text: str) -> bool:
        """Check if text looks like a monetary amount."""
        if not text:
            return False
        text = str(text).strip()
        # Match numbers with optional commas and decimals
        return bool(re.match(r'^[\d,]+\.?\d{0,2}$', text))
    
    def is_transaction_row(self, row: List[str]) -> bool:
        """Determine if a row is a transaction."""
        if not row or len(row) < 4:
            return False
        
        # Remove empty cells
        clean_row = [cell for cell in row if cell and str(cell).strip()]
        
        if len(clean_row) < 4:
            return False
        
        # First cell should be a date
        if not self.is_date(clean_row[0]):
            return False
        
        # Should have at least one amount
        has_money = any(self.has_amount(cell) for cell in clean_row[2:])
        
        return has_money
    
    def is_junk_row(self, row: List[str]) -> bool:
        """Determine if a row is junk (headers, footers, etc.)."""
        if not row:
            return True
        
        row_text = ' '.join(str(cell).lower() for cell in row if cell).strip()
        
        if not row_text or len(row_text) < 5:
            return True
        
        # Junk patterns to exclude
        junk_keywords = [
            'page', 'business owner', 'account number', 'sort code', 
            'statement for', 'balance', 'total paid', 'transactions',
            'bank account legal', 'clearbank', 'tide', 'fscs',
            'to be billed', 'transaction fee', 'regulation',
            'your tide account', 'registered', 'authorised',
        ]
        
        return any(keyword in row_text for keyword in junk_keywords)
    
    def detect_header_row(self, all_rows: List[List[str]]) -> List[str]:
        """Find the header row with column names."""
        header_keywords = ['date', 'transaction', 'details', 'paid', 'balance', 'debit', 'credit', 'amount']
        
        for row in all_rows[:20]:  # Check first 20 rows
            if not row:
                continue
            
            row_text = ' '.join(str(cell).lower() for cell in row if cell)
            
            # Count how many header keywords are present
            keyword_count = sum(1 for keyword in header_keywords if keyword in row_text)
            
            if keyword_count >= 3:  # If at least 3 header keywords found
                # Clean up the header
                clean_header = []
                for cell in row:
                    if cell and str(cell).strip():
                        clean_header.append(str(cell).strip())
                return clean_header if clean_header else None
        
        # Default header if none found
        return ['Date', 'Transaction Type', 'Details', 'Paid In', 'Paid Out', 'Balance']
    
    def clean_cell(self, cell) -> str:
        """Clean individual cell content."""
        if cell is None:
            return ''
        
        text = str(cell).strip()
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        return text
    
    def extract_smart_transactions(self, pdf_file) -> Tuple[List[str], List[List[str]]]:
        """Extract only transaction rows from PDF."""
        all_rows = []
        header = None
        
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                # Extract tables
                tables = page.extract_tables()
                
                for table in tables:
                    if not table:
                        continue
                    
                    for row in table:
                        if not row:
                            continue
                        
                        # Clean the row
                        clean_row = [self.clean_cell(cell) for cell in row]
                        
                        # Skip junk rows
                        if self.is_junk_row(clean_row):
                            continue
                        
                        # Check if it's a transaction
                        if self.is_transaction_row(clean_row):
                            all_rows.append(clean_row)
        
        # Detect header from all extracted rows
        if all_rows:
            # Try to find header in the first few rows before actual transactions
            with pdfplumber.open(pdf_file) as pdf:
                all_table_rows = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            all_table_rows.extend(table)
                
                header = self.detect_header_row(all_table_rows)
        
        if not header:
            # Create header based on the number of columns
            if all_rows:
                num_cols = len(all_rows[0])
                header = [f'Column {i+1}' for i in range(num_cols)]
            else:
                header = ['Date', 'Transaction Type', 'Details', 'Paid In', 'Paid Out', 'Balance']
        
        return header, all_rows
    
    def convert_to_csv(self, pdf_file) -> str:
        """Convert PDF to clean CSV with only transactions."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        # Create CSV in memory
        output = io.StringIO()
        writer = csv.writer(output, quoting=csv.QUOTE_MINIMAL)
        
        # Write header
        writer.writerow(header)
        
        # Write transactions
        writer.writerows(transactions)
        
        return output.getvalue()
    
    def convert_to_excel(self, pdf_file) -> bytes:
        """Convert PDF to clean Excel with only transactions."""
        header, transactions = self.extract_smart_transactions(pdf_file)
        
        # Create DataFrame
        df = pd.DataFrame(transactions, columns=header)
        
        # Clean up amounts (remove commas from numbers)
        for col in df.columns:
            if 'paid' in col.lower() or 'balance' in col.lower() or 'amount' in col.lower():
                df[col] = df[col].str.replace(',', '')
        
        # Create Excel file in memory
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Transactions')
            
            # Auto-adjust column widths
            worksheet = writer.sheets['Transactions']
            for idx, col in enumerate(df.columns):
                max_length = max(
                    df[col].astype(str).apply(len).max(),
                    len(col)
                )
                worksheet.column_dimensions[chr(65 + idx)].width = min(max_length + 2, 50)
        
        return output.getvalue()

# Title and description
st.markdown("<h1>📄 PDF to CSV Converter</h1>", unsafe_allow_html=True)
st.markdown("<p class='subtitle'>Upload your PDF and get clean, ready-to-use data instantly</p>", unsafe_allow_html=True)

# Main container
with st.container():
    # File uploader
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type=['pdf'],
        help="Upload a PDF file to convert (bank statements, invoices, etc.)"
    )
    
    # Conversion mode
    col1, col2 = st.columns(2)
    
    with col1:
        conversion_mode = st.selectbox(
            "Conversion Mode",
            options=['Smart (Transactions Only)', 'Standard (All Data)'],
            index=0,
            help="Smart mode extracts only transaction rows and removes junk"
        )
    
    with col2:
        output_format = st.selectbox(
            "Output Format",
            options=['CSV', 'Excel'],
            index=0,
            help="Choose your preferred output format"
        )
    
    # Info about smart mode
    if conversion_mode == 'Smart (Transactions Only)':
        st.info("🧠 **Smart Mode:** Automatically detects and extracts only transaction rows. Perfect for bank statements!")
    else:
        st.info("📋 **Standard Mode:** Extracts all tables and text from the PDF")
    
    # Convert button
    if uploaded_file is not None:
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            if st.button("🔄 Convert Now", type="primary", use_container_width=True):
                try:
                    with st.spinner('Converting your PDF...'):
                        converter = SmartPDFConverter()
                        
                        if conversion_mode == 'Smart (Transactions Only)':
                            if output_format == 'Excel':
                                # Convert to Excel
                                excel_data = converter.convert_to_excel(uploaded_file)
                                
                                # Success message
                                st.success('✅ Conversion complete!')
                                
                                # Download button
                                st.download_button(
                                    label="⬇️ Download Excel",
                                    data=excel_data,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.xlsx",
                                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                # Preview
                                st.subheader("Preview")
                                header, transactions = converter.extract_smart_transactions(uploaded_file)
                                df_preview = pd.DataFrame(transactions[:10], columns=header)
                                st.dataframe(df_preview, use_container_width=True)
                                
                                st.metric("Total Transactions", len(transactions))
                                
                            else:  # CSV
                                # Convert to CSV
                                csv_content = converter.convert_to_csv(uploaded_file)
                                
                                # Success message
                                st.success('✅ Conversion complete!')
                                
                                # Download button
                                st.download_button(
                                    label="⬇️ Download CSV",
                                    data=csv_content,
                                    file_name=f"{uploaded_file.name.replace('.pdf', '')}_transactions.csv",
                                    mime="text/csv",
                                    type="primary",
                                    use_container_width=True
                                )
                                
                                # Preview
                                st.subheader("Preview (First 10 rows)")
                                preview_lines = csv_content.split('\n')[:11]
                                st.text('\n'.join(preview_lines))
                                
                                row_count = len(csv_content.split('\n')) - 1
                                st.metric("Total Transactions", row_count)
                        
                        else:  # Standard mode
                            # Use basic extraction
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
st.markdown("### ✨ Features")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    - ✅ Smart transaction detection
    - ✅ Auto-remove junk rows
    - ✅ Excel & CSV output
    - ✅ Ready-to-use data
    """)

with col2:
    st.markdown("""
    - ✅ Bank statement friendly
    - ✅ No manual cleanup needed
    - ✅ Column auto-detection
    - ✅ Instant download
    """)

# Footer
st.markdown("---")
st.markdown(
    "<p style='text-align: center; color: rgba(255,255,255,0.7); font-size: 0.9rem;'>"
    "Built with Streamlit • Smart extraction powered by pdfplumber"
    "</p>",
    unsafe_allow_html=True
)
