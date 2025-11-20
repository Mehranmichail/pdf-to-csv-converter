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

        .bank-selector {
            margin-bottom: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            border: 2px solid #667eea;
        }

        .bank-selector label {
            display: block;
            font-size: 16px;
            font-weight: 600;
            color: #667eea;
            margin-bottom: 10px;
        }

        .bank-selector select {
            width: 100%;
            padding: 12px;
            font-size: 16px;
            border: 2px solid #667eea;
            border-radius: 8px;
            background: white;
            cursor: pointer;
            transition: all 0.3s;
        }

        .bank-selector select:focus {
            outline: none;
            border-color: #764ba2;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
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

        .upload-section.disabled {
            opacity: 0.5;
            cursor: not-allowed;
            pointer-events: none;
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

        .bank-detected {
            margin-bottom: 15px;
            padding: 10px;
            background: #e3f2fd;
            border-radius: 5px;
            color: #1976d2;
            font-weight: 600;
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

        .warning-message {
            margin-top: 10px;
            padding: 10px;
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            border-radius: 5px;
            color: #856404;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🏦 Bank Statement Converter</h1>
            <p>Convert your bank PDF statements to Excel format instantly</p>
        </div>

        <div class="content">
            <!-- Bank Selection -->
            <div class="bank-selector">
                <label for="bankSelect">Select Your Bank:</label>
                <select id="bankSelect">
                    <option value="">-- Please Select Your Bank --</option>
                    <option value="tide">Tide Bank</option>
                    <option value="barclays">Barclays</option>
                </select>
                <div class="warning-message" id="warningMessage" style="display: none;">
                    ⚠️ Please select your bank before uploading a statement
                </div>
            </div>

            <div class="upload-section disabled" id="uploadSection">
                <div class="upload-icon">📄</div>
                <h3>Drop your PDF file here</h3>
                <p>Please select a bank first</p>
                <input type="file" id="fileInput" accept=".pdf" disabled>
                <button class="btn" id="uploadBtn" onclick="document.getElementById('fileInput').click()" disabled>
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
                
                <div class="bank-detected" id="bankDetected"></div>

                <div class="stats">
                    <div class="stat-card">
                        <div class="label">Total Transactions</div>
                        <div class="value" id="totalTransactions">0</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Money In</div>
                        <div class="value" style="color: #4CAF50;" id="totalPaidIn">£0.00</div>
                    </div>
                    <div class="stat-card">
                        <div class="label">Total Money Out</div>
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
            <p>Supports Tide Bank and Barclays statements | Data processed locally in your browser</p>
        </div>
    </div>

    <script src="https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

        let extractedData = [];
        let selectedBank = '';

        const bankSelect = document.getElementById('bankSelect');
        const fileInput = document.getElementById('fileInput');
        const uploadSection = document.getElementById('uploadSection');
        const uploadBtn = document.getElementById('uploadBtn');
        const progressSection = document.getElementById('progressSection');
        const resultSection = document.getElementById('resultSection');
        const errorMessage = document.getElementById('errorMessage');
        const progressBar = document.getElementById('progressBar');
        const statusMessage = document.getElementById('statusMessage');
        const warningMessage = document.getElementById('warningMessage');

        // Bank selection handler
        bankSelect.addEventListener('change', (e) => {
            selectedBank = e.target.value;
            
            if (selectedBank) {
                uploadSection.classList.remove('disabled');
                fileInput.disabled = false;
                uploadBtn.disabled = false;
                uploadSection.querySelector('p').textContent = 'or click to browse';
                warningMessage.style.display = 'none';
            } else {
                uploadSection.classList.add('disabled');
                fileInput.disabled = true;
                uploadBtn.disabled = true;
                uploadSection.querySelector('p').textContent = 'Please select a bank first';
                warningMessage.style.display = 'block';
            }
            
            // Reset any previous results
            resultSection.style.display = 'none';
            hideError();
        });

        uploadSection.addEventListener('dragover', (e) => {
            e.preventDefault();
            if (selectedBank) {
                uploadSection.classList.add('dragover');
            }
        });

        uploadSection.addEventListener('dragleave', () => {
            uploadSection.classList.remove('dragover');
        });

        uploadSection.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadSection.classList.remove('dragover');
            
            if (!selectedBank) {
                showError('Please select your bank first');
                warningMessage.style.display = 'block';
                return;
            }
            
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
            if (!selectedBank) {
                showError('Please select your bank first');
                return;
            }

            try {
                hideError();
                resultSection.style.display = 'none';
                progressSection.style.display = 'block';
                updateProgress(10, 'Reading PDF file...');

                const arrayBuffer = await file.arrayBuffer();
                const pdf = await pdfjsLib.getDocument(arrayBuffer).promise;
                
                updateProgress(30, `Processing ${pdf.numPages} pages for ${bankSelect.options[bankSelect.selectedIndex].text}...`);

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
                    
                    // Call the appropriate extraction function based on selected bank
                    if (selectedBank === 'tide') {
                        extractTideData(lines);
                    } else if (selectedBank === 'barclays') {
                        extractBarclaysData(lines);
                    }
                    
                    const progress = 30 + (pageNum / pdf.numPages) * 60;
                    updateProgress(progress, `Processing page ${pageNum} of ${pdf.numPages}...`);
                }

                updateProgress(95, 'Finalizing...');

                if (extractedData.length === 0) {
                    throw new Error(`No transactions found. Please check if this is a valid ${bankSelect.options[bankSelect.selectedIndex].text} statement.`);
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

        // ========================================
        // TIDE BANK EXTRACTION (ORIGINAL CODE)
        // ========================================
        function extractTideData(lines) {
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

        // ========================================
        // BARCLAYS BANK EXTRACTION (NEW CODE)
        // ========================================
        function extractBarclaysData(lines) {
            for (let line of lines) {
                const lineText = line.map(item => item.text).join(' ');
                const allText = line.map(item => item.text);
                
                // Barclays date format: "1 Feb", "3 Feb", "10 Feb", etc.
                const dateMatch = lineText.match(/^(\\d{1,2}\\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec))\\b/);
                
                if (!dateMatch) continue;
                
                const date = dateMatch[1];
                
                // Skip header rows and summary rows
                if (lineText.includes('Description') || 
                    lineText.includes('Money out') || 
                    lineText.includes('Money in') ||
                    lineText.includes('Start Balance') ||
                    lineText.includes('Balance brought forward') ||
                    lineText.includes('Balance carried forward') ||
                    lineText.includes('Total Payments')) {
                    continue;
                }
                
                // Extract all numbers that look like amounts (format: 1,234.56 or 1234.56)
                const amountPattern = /\\b\\d{1,3}(?:,\\d{3})*\\.\\d{2}\\b/g;
                const amounts = [];
                let match;
                while ((match = amountPattern.exec(lineText)) !== null) {
                    amounts.push(match[0].replace(/,/g, ''));
                }
                
                // Need at least 2 amounts (one transaction amount + balance)
                // Or 3 amounts (money out + money in + balance)
                if (amounts.length < 1) continue;
                
                // Identify transaction type
                let transactionType = '';
                if (lineText.includes('Direct Debit') || allText.includes('DD')) {
                    transactionType = 'Direct Debit';
                } else if (lineText.includes('Direct Credit') || allText.includes('Giro')) {
                    transactionType = 'Direct Credit';
                } else if (lineText.includes('Card Purchase')) {
                    transactionType = 'Card Purchase';
                } else if (lineText.includes('Card Payment')) {
                    transactionType = 'Card Payment';
                } else if (lineText.includes('Cash Withdrawal') || allText.includes('ATM')) {
                    transactionType = 'Cash Withdrawal';
                } else if (lineText.includes('Internet Banking Transfer') || lineText.includes('On-Line Banking')) {
                    transactionType = 'Online Transfer';
                } else if (lineText.includes('Commission Charges')) {
                    transactionType = 'Commission';
                } else {
                    transactionType = 'Other';
                }
                
                // Extract description (text between transaction type and first amount)
                let description = '';
                const words = allText.filter(t => t && t.length > 0);
                
                // Find where transaction type ends and where numbers start
                let descStart = -1;
                let descEnd = -1;
                
                for (let i = 0; i < words.length; i++) {
                    const word = words[i];
                    
                    // Skip the date
                    if (word === date.split(' ')[0] || word === date.split(' ')[1]) continue;
                    
                    // Skip transaction type keywords
                    if (word === 'Direct' || word === 'Debit' || word === 'Credit' || 
                        word === 'Card' || word === 'Purchase' || word === 'Payment' ||
                        word === 'Cash' || word === 'Withdrawal' || word === 'Internet' ||
                        word === 'Banking' || word === 'Transfer' || word === 'On-Line' ||
                        word === 'Commission' || word === 'Charges' || word === 'DD' || 
                        word === 'Giro' || word === 'ATM' || word === ')))' || word === '—') {
                        continue;
                    }
                    
                    // Check if this is an amount
                    if (/\\d{1,3}(?:,\\d{3})*\\.\\d{2}/.test(word)) {
                        if (descStart !== -1 && descEnd === -1) {
                            descEnd = i;
                        }
                        break;
                    }
                    
                    // Start collecting description
                    if (descStart === -1) {
                        descStart = i;
                    }
                }
                
                if (descStart !== -1) {
                    if (descEnd === -1) descEnd = words.length;
                    const descWords = words.slice(descStart, descEnd);
                    description = descWords.filter(w => !/^\\d{1,3}(?:,\\d{3})*\\.\\d{2}$/.test(w)).join(' ');
                }
                
                description = description.replace(/\\s+/g, ' ').trim();
                
                // Determine money in/out/balance
                let moneyOut = '';
                let moneyIn = '';
                let balance = '';
                
                if (amounts.length >= 1) {
                    // Last amount is typically the balance
                    balance = amounts[amounts.length - 1];
                    
                    if (amounts.length === 3) {
                        // Format: Money Out, Money In, Balance
                        moneyOut = amounts[0];
                        moneyIn = amounts[1];
                    } else if (amounts.length === 2) {
                        // Format: Transaction Amount, Balance
                        const txAmount = amounts[0];
                        
                        // Determine if it's money in or money out based on transaction type
                        if (transactionType === 'Direct Credit' || 
                            transactionType.includes('Credit') ||
                            (description && (description.toLowerCase().includes('from') || 
                             description.toLowerCase().includes('youlend') ||
                             description.toLowerCase().includes('tablesnappr') ||
                             description.toLowerCase().includes('uber payments') ||
                             description.toLowerCase().includes('just eat') ||
                             description.toLowerCase().includes('roofoods')))) {
                            moneyIn = txAmount;
                        } else {
                            moneyOut = txAmount;
                        }
                    } else if (amounts.length === 1) {
                        // Only balance, might be a balance line
                        balance = amounts[0];
                    }
                }
                
                // Only add if we have meaningful data
                if (description || moneyIn || moneyOut) {
                    extractedData.push({
                        'Date': date,
                        'Transaction type': transactionType,
                        'Details': description,
                        'Money out (£)': moneyOut,
                        'Money in (£)': moneyIn,
                        'Balance (£)': balance
                    });
                }
            }
        }

        function displayResults() {
            progressSection.style.display = 'none';
            resultSection.style.display = 'block';

            // Display selected bank
            document.getElementById('bankDetected').textContent = `Bank: ${bankSelect.options[bankSelect.selectedIndex].text}`;

            let totalPaidIn = 0;
            let totalPaidOut = 0;

            // Different column names based on bank
            const moneyInCol = selectedBank === 'tide' ? 'Paid in (£)' : 'Money in (£)';
            const moneyOutCol = selectedBank === 'tide' ? 'Paid out (£)' : 'Money out (£)';

            extractedData.forEach(row => {
                if (row[moneyInCol]) {
                    totalPaidIn += parseFloat(row[moneyInCol]);
                }
                if (row[moneyOutCol]) {
                    totalPaidOut += parseFloat(row[moneyOutCol]);
                }
            });

            document.getElementById('totalTransactions').textContent = extractedData.length;
            document.getElementById('totalPaidIn').textContent = '£' + totalPaidIn.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});
            document.getElementById('totalPaidOut').textContent = '£' + totalPaidOut.toLocaleString('en-GB', {minimumFractionDigits: 2, maximumFractionDigits: 2});

            // Display preview table
            const previewTable = document.getElementById('previewTable');
            let tableHTML = '<thead><tr>';
            
            // Get headers from first row
            const headers = Object.keys(extractedData[0]);
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

            // Auto-size columns
            const headers = Object.keys(extractedData[0]);
            const colWidths = headers.map(header => {
                if (header === 'Details') return { wch: 60 };
                if (header === 'Description') return { wch: 60 };
                if (header === 'Transaction type') return { wch: 20 };
                return { wch: 15 };
            });
            ws['!cols'] = colWidths;

            const now = new Date();
            const bankName = selectedBank === 'tide' ? 'Tide' : 'Barclays';
            const filename = `${bankName}_statement_${now.getFullYear()}_${(now.getMonth()+1).toString().padStart(2,'0')}_${now.getDate().toString().padStart(2,'0')}.xlsx`;

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
components.html(html_content, height=1100, scrolling=True)
