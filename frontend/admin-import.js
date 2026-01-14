// Admin Import Tool for Royal Family Tree
let csvData = [];
let isImporting = false;

function getConfig() {
    return {
        backendUrl: document.getElementById('backend-url').value.trim(),
        adminToken: document.getElementById('admin-token').value.trim()
    };
}

function log(message, type = 'info') {
    const logSection = document.getElementById('log-section');
    const entry = document.createElement('div');
    entry.className = `log-entry ${type}`;
    entry.textContent = `[${new Date().toLocaleTimeString()}] ${message}`;
    logSection.appendChild(entry);
    logSection.scrollTop = logSection.scrollHeight;
}

function updateStats(created = 0, updated = 0, relationships = 0, rejected = 0) {
    document.getElementById('stat-created').textContent = created;
    document.getElementById('stat-updated').textContent = updated;
    document.getElementById('stat-relationships').textContent = relationships;
    document.getElementById('stat-rejected').textContent = rejected;
}

function updateProgress(current, total) {
    const percentage = Math.round((current / total) * 100);
    const progressFill = document.getElementById('progress-fill');
    progressFill.style.width = `${percentage}%`;
    progressFill.textContent = `${percentage}%`;
}

// Parse CSV
function parseCSV(text) {
    const lines = text.split('\n').filter(line => line.trim());
    if (lines.length === 0) return [];
    
    const headers = lines[0].split(',').map(h => h.trim().toLowerCase());
    const data = [];
    
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',').map(v => v.trim());
        const row = {};
        headers.forEach((header, index) => {
            row[header] = values[index] || '';
        });
        if (row.english_name || row.name_original) { // Support both formats
            data.push(row);
        }
    }
    
    return data;
}

// Handle file upload
function handleFile(file) {
    if (!file || !file.name.endsWith('.csv')) {
        alert('Please select a CSV file');
        return;
    }
    
    const reader = new FileReader();
    // Read file as UTF-8 to preserve Amharic characters
    reader.readAsText(file, 'UTF-8');
    reader.onload = (e) => {
        try {
            csvData = parseCSV(e.target.result);
            document.getElementById('file-name').textContent = file.name;
            document.getElementById('row-count').textContent = csvData.length;
            document.getElementById('file-info').style.display = 'block';
            checkImportReady();
            log(`Loaded ${csvData.length} rows from ${file.name}`, 'success');
        } catch (error) {
            log(`Error parsing CSV: ${error.message}`, 'error');
        }
    };
    reader.readAsText(file);
}

// Check if ready to import
function checkImportReady() {
    const config = getConfig();
    const hasData = csvData.length > 0;
    const hasConfig = config.backendUrl && config.adminToken;
    document.getElementById('import-btn').disabled = !hasData || !hasConfig || isImporting;
}

// API request
async function apiRequest(endpoint, data, config) {
    const response = await fetch(`${config.backendUrl}${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-ADMIN-TOKEN': config.adminToken
        },
        body: JSON.stringify(data)
    });
    
    if (!response.ok) {
        const error = await response.json().catch(() => ({ error: { message: 'Request failed' } }));
        throw new Error(error.error?.message || `HTTP ${response.status}`);
    }
    
    return await response.json();
}

// Convert CSV rows to import format
function convertToImportFormat() {
    const rows = [];
    csvData.forEach(row => {
        const importRow = {
            english_name: row.english_name || row.name_original || '',
            amharic_name: row.amharic_name || row.name_amharic || '',
            english_parent_name: row.english_parent_name || row.parent_name || '',
            amharic_parent_name: row.amharic_parent_name || ''
        };
        if (importRow.english_name) {
            rows.push(importRow);
        }
    });
    return rows;
}

// Main import function
async function startImport() {
    if (isImporting) return;
    
    const config = getConfig();
    if (!config.backendUrl || !config.adminToken) {
        alert('Please configure backend URL and admin token');
        return;
    }
    
    if (csvData.length === 0) {
        alert('Please upload a CSV file');
        return;
    }
    
    isImporting = true;
    document.getElementById('import-btn').disabled = true;
    document.getElementById('progress-section').style.display = 'block';
    document.getElementById('log-section').innerHTML = '';
    updateStats(0, 0, 0, 0);
    
    try {
        log('Starting import...', 'info');
        updateProgress(0, 100);
        
        // Convert CSV to import format
        const rows = convertToImportFormat();
        log(`Processing ${rows.length} rows...`, 'info');
        
        // Import using combined endpoint
        const result = await apiRequest('/admin/import/combined', { rows: rows }, config);
        
        // Update stats
        const peopleCreated = result.people?.created || 0;
        const peopleUpdated = result.people?.updated || 0;
        const relationshipsCreated = result.relationships?.created || 0;
        const rejected = (result.people?.rejected?.length || 0) + (result.relationships?.rejected?.length || 0);
        
        updateStats(peopleCreated, peopleUpdated, relationshipsCreated, rejected);
        updateProgress(100, 100);
        
        log(`✅ Import complete!`, 'success');
        log(`Created: ${peopleCreated} people, ${relationshipsCreated} relationships`, 'success');
        log(`Updated: ${peopleUpdated} people`, 'info');
        
        if (rejected > 0) {
            log(`Rejected: ${rejected} rows (check details below)`, 'warning');
            if (result.people?.rejected?.length > 0) {
                result.people.rejected.slice(0, 5).forEach(r => {
                    log(`  People rejected: ${JSON.stringify(r)}`, 'warning');
                });
            }
            if (result.relationships?.rejected?.length > 0) {
                result.relationships.rejected.slice(0, 5).forEach(r => {
                    log(`  Relationships rejected: ${JSON.stringify(r)}`, 'warning');
                });
            }
        }
        
        log('🎉 You can now view the tree!', 'success');
        
    } catch (error) {
        let errorMsg = error.message;
        
        // Provide more helpful error messages
        if (error.message === 'Failed to fetch') {
            errorMsg = 'Failed to fetch - Check:\n1. Backend URL is correct\n2. ALLOWED_ORIGINS includes this site\n3. Backend is running (test /health endpoint)\n4. Check browser console (F12) for details';
        }
        
        log(`❌ Import failed: ${errorMsg}`, 'error');
        console.error('Import error:', error);
        
        // Log additional debugging info
        const config = getConfig();
        log(`Backend URL: ${config.backendUrl}`, 'info');
        log(`Try testing: ${config.backendUrl}/health`, 'info');
    } finally {
        isImporting = false;
        document.getElementById('import-btn').disabled = false;
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('csv-file');
    const dropzone = document.getElementById('dropzone');
    
    // File input
    fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));
    
    // Drag and drop
    dropzone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropzone.classList.add('dragover');
    });
    
    dropzone.addEventListener('dragleave', () => {
        dropzone.classList.remove('dragover');
    });
    
    dropzone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropzone.classList.remove('dragover');
        if (e.dataTransfer.files.length > 0) {
            handleFile(e.dataTransfer.files[0]);
        }
    });
    
    // Config changes
    ['backend-url', 'admin-token'].forEach(id => {
        document.getElementById(id).addEventListener('input', checkImportReady);
    });
    
    // Import button
    document.getElementById('import-btn').addEventListener('click', startImport);
    
    log('Admin import tool ready', 'success');
});

