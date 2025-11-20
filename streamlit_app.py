import streamlit as st
import streamlit.components.v1 as components

# Set page config
st.set_page_config(page_title="Bank Statement Converter", page_icon="🏦", layout="wide")

# HTML content
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bank Statement PDF to Excel Converter</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }

        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }

        .header h1 {
            font-size: 28px;
            margin-bottom: 10px;
        }

        .header p {
            opacity: 0.9;
            font-size: 14px;
        }

        .content {
            padding: 40px;
        }

        .upload-section {
            border: 3px dashed #667eea;
            border-radius: 15px;
            padding: 40px;
            text-align: center;
            background: #f8f9ff;
            transition: all 0.3s;
            cursor: pointer;
        }

        .upload-section:hover {
            border-color: #764ba2;
            background: #f0f1ff;
        }

        .upload-section.dragover {
            border-color: #4CAF50;
            background: #e8f5e9;
        }

        .upload-icon {
            font-size: 48px;
            margin-bottom: 20px;
        }

        .upload-section h3 {
            color: #667eea;
            margin-bottom: 10px;
        }

        .upload-section p {
            color: #666;
            margin-bottom: 20px;
        }

        input[type="file"] {
            display: none;
        }

        .btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            border-radius: 25px;
            font-size: 16px;
            cursor: pointer;
            transition: transform 0.2s;
            font-weight: 600;
        }

        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }

        .btn:disabled {
            background: #ccc;
            cursor: not-allowed;
            transform: none;
        }

        .progress-section {
            display: none;
            margin-top: 30px;
        }

        .progress-bar-container {
            background: #e0e0e0;
            border-radius: 10px;
            overflow: hidden;
            height: 30px;
            margin-bottom: 15px;
        }

        .progress-bar {
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            height: 100%;
            width: 0%;
            transition: width 0.3s;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: 600;
            font-size: 14px;
        }

        .status-message {
            text-align: center;
            color: #666;
            font-size: 14px;
        }

        .result-section {
            display: none;
            margin-top: 30px;
            padding: 20px;
            background: #f0f8ff;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }

        .result-section h3 {
            color: #667eea;
            margin-bottom: 15px;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .stat-card {
            background: white;
            padding: 15px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .stat-card .label {
            font-size: 12px;
            color: #666;
            margin-bottom: 5px;
        }

        .stat-card .value {
            font-size: 24px;
            font-weight: 700;
            color: #667eea;
        }

        .error-message {
            display: none;
            margin-top: 20px;
            padding: 15px;
            background: #ffebee;
            border-left: 4px solid #f44336;
            border-radius: 5px;
            color: #c62828;
        }

        .preview-table {
            margin-top: 20px;
            overflow-x: auto;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 13px;
        }

        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #e0e0e0;
        }

        th {
            background: #667eea;
            color: white;
            font-weight: 600;
        }

        tr:hover {
            background: #f5f5f5;
        }

        .download-btn {
            margin-top: 20px;
            width: 100%;
        }

        .footer {
            text-align: center;
            padding: 20px;
            color: #666;
            font-size: 12px;
            background: #f8f9fa;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Bank Statement Converter</h1>
            <p>Convert your Tide Bank PDF statements to Excel format instantly</p>
        </div>

        <div class="content">
            <div class="upload-section" id="uploadSection">
                <div class="upload-icon">📄</div>
                <h3>Drop your PDF file here</h3>
                <p>or click to browse</p>
                <input type="file" id="fileInput" accept=".pdf">
                <button class="btn" onclick="document.getElementById('fileInput').click()">
                    Select PDF File
                </button>
            </div>

            <div class="progress-section" id="progressSection">
                <div class="progress-bar-container">
                    <div class="progress-bar" id="progressBar">0%</div>
                </div>
                <div class="status-message" id="statusMessage">Processing...</div>
            </div>

            <div class="error-message" id="errorMessage"></div>

            <div class="result-section" id="resultSection">
                <h3>✅ Conversion Successful!</h3>
                
                <div class="stats">
                    <div class="stat-card">
                        <div class="label">Total Transactions</div>
                        <div class="value" id="totalTransactions">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Paid In</div>
                        <div class="value" style="color: #4CAF50;" id="totalPaidIn">£0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Paid Out</div>
                        <div class="value" style="color: #f44336;" id="totalPaidOut">£0.00</div>
                    </div>
                </div>

                <button class="btn download-btn" id="downloadBtn">
                    📥 Download Excel File
                </button>

                <div class="preview-table">
                    <h4 style="margin-bottom: 10px; color: #667eea;">Preview (First 10 rows)</h4>
                    <table id="previewTable"></table>
                </div>
            </div>
        </div>

        <div class="footer">
            <p>Supports Tide Bank statement PDFs | Data processed locally in your browser</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        let extractedData = [];

        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');
        const progressSection = document.getElementById('progressSection');
        const resultSection = document.getElementById('resultSection');
        const errorMessage = document.getElementById('errorMessage');
        const progressBar = document.getElementById('progressBar');
        const statusMessage = document.getElementById('statusMessage');

        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadSection.classList.add('dragover');
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('dragover');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            const file = e.dataTransfer.files[0];
            if (file && file.type === 'application/pdf') {
                processPDF(file);
            } else {
                showError('Please upload a valid PDF file');
            }
        });

        fileInput.addEventListener('change', (e) => {
            const file = e.target.files[0];
            if (file) {
                processPDF(file);
            }
        });

        async function processPDF(file) {
            try {
                hideError();
                resultSection.style.display = 'none';
                progressSection.style.display = 'block';
                updateProgress(10, 'Reading PDF file...');

                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                
                updateProgress(30, `Processing ${pdf.numPages} pages...`);

                extractedData = [];

                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    const page = await pdf.getPage(pageNum);
                    const textContent = await page.getTextContent();
                    
                    const items = textContent.items.map(item => ({
                        text: item.str.trim(),
                        x: Math.round(item.transform[4]),
                        y: Math.round(item.transform[5]),
                        height: Math.round(item.height)
                    }));

                    const lines = groupIntoLines(items);
                    extractTableData(lines);
                    
                    const progress = 30 + (pageNum / pdf.numPages) * 60;
                    updateProgress(progress, `Processing page ${pageNum} of ${pdf.numPages}...`);
                }

                updateProgress(95, 'Finalizing...');

                if (extractedData.length === 0) {
                    throw new Error('No transactions found. Please check if this is a valid Tide Bank statement.');
                }

                updateProgress(100, 'Complete!');
                displayResults();

            } catch (error) {
                console.error('Error:', error);
                showError('Error processing PDF: ' + error.message);
                progressSection.style.display = 'none';
            }
        }

        function groupIntoLines(items) {
            items.sort((a, b) => b.y - a.y);
            
            const lines = [];
            let currentLine = [];
            let currentY = null;
            const yThreshold = 5;
            
            items.forEach(item => {
                if (item.text === '') return;
                
                if (currentY === null || Math.abs(item.y - currentY) <= yThreshold) {
                    currentLine.push(item);
                    currentY = item.y;
                } else {
                    if (currentLine.length > 0) {
                        currentLine.sort((a, b) => a.x - b.x);
                        lines.push(currentLine);
                    }
                    currentLine = [item];
                    currentY = item.y;
                }
            });
            
            if (currentLine.length > 0) {
                currentLine.sort((a, b) => a.x - b.x);
                lines.push(currentLine);
            }
            
            return lines;
        }

        function extractTableData(lines) {
            for (let line of lines) {
                const lineText = line.map(item => item.text).join(' ');
                
                const dateMatch = lineText.match(/^(\\d{1,2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\\s+\\d{4})/);
                
                if (dateMatch) {
                    const date = dateMatch[1];
                    const allText = line.map(item => item.text);
                    
                    let transType = '';
                    let transTypeIndex = -1;
                    const types = ['Card Transaction Refund', 'Card Transaction', 'Domestic Transfer', 'Direct Debit', 'Fee'];
                    
                    for (let type of types) {
                        const idx = allText.findIndex(t => t.includes(type.split(' ')[0]));
                        if (idx !== -1) {
                            const checkText = allText.slice(idx, idx + type.split(' ').length).join(' ');
                            if (checkText.includes(type)) {
                                transType = type;
                                transTypeIndex = idx;
                                break;
                            }
                        }
                    }
                    
                    if (!transType) continue;
                    
                    const numbers = [];
                    for (let i = 0; i < allText.length; i++) {
                        const text = allText[i].replace(/,/g, '');
                        if (/^\\d+\\.\\d{2}$/.test(text)) {
                            numbers.push({ value: text, index: i });
                        }
                    }
                    
                    if (numbers.length < 2) continue;
                    
                    const balance = numbers[numbers.length - 1].value;
                    
                    let paidIn = '';
                    let paidOut = '';
                    
                    if (numbers.length === 3) {
                        paidIn = numbers[0].value;
                        paidOut = numbers[1].value;
                    } else if (numbers.length === 2) {
                        const amount = numbers[0].value;
                        
                        const detailsText = allText.join(' ').toLowerCase();
                        const isIncome = transType === 'Card Transaction Refund' || 
                                       (transType === 'Domestic Transfer' && (
                                           detailsText.includes('sumup') ||
                                           detailsText.includes('paymentsense') ||
                                           detailsText.includes('evo payments') ||
                                           detailsText.includes('dojo') ||
                                           detailsText.includes('american express')
                                       ));
                        
                        if (isIncome) {
                            paidIn = amount;
                        } else {
                            paidOut = amount;
                        }
                    }
                    
                    let details = [];
                    for (let i = transTypeIndex + 1; i < numbers[0].index; i++) {
                        if (allText[i] && !allText[i].includes('Tide Card') && allText[i] !== '****') {
                            details.push(allText[i]);
                        }
                    }
                    const detailsStr = details.join(' ').replace(/\\s+/g, ' ').trim();
                    
                    extractedData.push({
                        'Date': date,
                        'Transaction type': transType,
                        'Details': detailsStr,
                        'Paid in (£)': paidIn,
                        'Paid out (£)': paidOut,
                        'Balance (£)': balance
                    });
                }
            }
        }

        function displayResults() {
            progressSection.style.display = 'none';
            resultSection.style.display = 'block';

            let totalPaidIn = 0;
            let totalPaidOut = 0;

            extractedData.forEach(row => {
                if (row['Paid in (£)']) {
                    totalPaidIn += parseFloat(row['Paid in (£)']);
                }
                if (row['Paid out (£)']) {
                    totalPaidOut += parseFloat(row['Paid out (£)']);
                }
            });

            document.getElementById('totalTransactions').textContent = extractedData.length;
            document.getElementById('totalPaidIn').textContent = '£' + totalPaidIn.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('totalPaidOut').textContent = '£' + totalPaidOut.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            const previewTable = document.getElementById('previewTable');
            let tableHTML = '<thead><tr>';
            const headers = ['Date', 'Transaction type', 'Details', 'Paid in (£)', 'Paid out (£)', 'Balance (£)'];
            headers.forEach(header => {
                tableHTML += `<th>${header}</th>`;
            });
            tableHTML += '</tr></thead><tbody>';

            extractedData.slice(0, 10).forEach(row => {
                tableHTML += '<tr>';
                headers.forEach(header => {
                    const value = row[header] || '';
                    tableHTML += `<td>${value}</td>`;
                });
                tableHTML += '</tr>';
            });
            tableHTML += '</tbody>';
            previewTable.innerHTML = tableHTML;
        }

        document.getElementById('downloadBtn').addEventListener('click', () => {
            const ws = XLSX.utils.json_to_sheet(extractedData);
            const wb = XLSX.utils.book_new();
            XLSX.utils.book_append_sheet(wb, ws, 'Transactions');

            const colWidths = [
                { wch: 15 },
                { wch: 20 },
                { wch: 60 },
                { wch: 15 },
                { wch: 15 },
                { wch: 15 }
            ];
            ws['!cols'] = colWidths;

            const now = new Date();
            const filename = `bank_statement_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;

            XLSX.writeFile(wb, filename);
        });

        function updateProgress(percent, message) {
            progressBar.style.width = percent + '%';
            progressBar.textContent = Math.round(percent) + '%';
            statusMessage.textContent = message;
        }

        function showError(message) {
            errorMessage.textContent = message;
            errorMessage.style.display = 'block';
        }

        function hideError() {
            errorMessage.style.display = 'none';
        }
    </script>
</body>
</html>
"""

# Display the HTML component
components.html(html_content, height=1000, scrolling=True)

