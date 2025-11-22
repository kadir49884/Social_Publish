// SocialPublish - Frontend JavaScript

// API Base URL
const API_URL = '';

// State
let platforms = {};
let selectedPlatforms = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initApp();
});

async function initApp() {
    // Load platforms
    await loadPlatforms();
    
    // Setup event listeners
    setupEventListeners();
}

// Load available platforms
async function loadPlatforms() {
    try {
        const response = await fetch(`${API_URL}/api/platforms`);
        platforms = await response.json();
        
        renderPlatforms();
    } catch (error) {
        console.error('Platform yükleme hatası:', error);
        showError('Platformlar yüklenirken hata oluştu');
    }
}

// Render platforms
function renderPlatforms() {
    const container = document.getElementById('platformsContainer');
    container.innerHTML = '';
    
    Object.entries(platforms).forEach(([key, platform]) => {
        const platformEl = document.createElement('div');
        platformEl.className = `platform-item ${platform.enabled ? '' : 'disabled'}`;
        
        // Checkbox element
        const checkbox = document.createElement('input');
        checkbox.type = 'checkbox';
        checkbox.id = `platform_${key}`;
        checkbox.value = key;
        checkbox.checked = platform.enabled; // Hazır olanlar varsayılan seçili
        checkbox.disabled = !platform.enabled; // Hazır olmayanlar disabled
        
        // Info element
        const infoDiv = document.createElement('div');
        infoDiv.className = 'platform-info';
        infoDiv.innerHTML = `
            <div class="platform-name">
                <span>${platform.icon}</span>
                <span>${platform.name}</span>
            </div>
            <div class="platform-status ${platform.enabled ? 'enabled' : 'disabled'}">
                ${platform.enabled ? '✅ Hazır' : '❌ API anahtarı eksik'}
            </div>
        `;
        
        // Append elements
        platformEl.appendChild(checkbox);
        platformEl.appendChild(infoDiv);
        container.appendChild(platformEl);
        
        // Click handler for the whole platform item
        if (platform.enabled) {
            platformEl.style.cursor = 'pointer';
            platformEl.addEventListener('click', (e) => {
                // Eğer checkbox'a direkt tıklanmadıysa
                if (e.target !== checkbox) {
                    checkbox.checked = !checkbox.checked;
                    // Active class toggle
                    if (checkbox.checked) {
                        platformEl.classList.add('active');
                    } else {
                        platformEl.classList.remove('active');
                    }
                    updateSelectedPlatforms();
                }
            });
            
            // Checkbox change handler
            checkbox.addEventListener('change', () => {
                if (checkbox.checked) {
                    platformEl.classList.add('active');
                } else {
                    platformEl.classList.remove('active');
                }
                updateSelectedPlatforms();
            });
        }
    });
    
    // Update selected platforms
    updateSelectedPlatforms();
}

// Setup event listeners
function setupEventListeners() {
    // Form submit
    const form = document.getElementById('publishForm');
    form.addEventListener('submit', handleSubmit);
    
    // Character counter
    const messageInput = document.getElementById('message');
    messageInput.addEventListener('input', updateCharCounter);
    
    // Image upload
    const imageInput = document.getElementById('image');
    imageInput.addEventListener('change', handleImageUpload);
    
    // Platform selection
    document.addEventListener('change', (e) => {
        if (e.target.type === 'checkbox' && e.target.id.startsWith('platform_')) {
            updateSelectedPlatforms();
        }
    });
}

// Update character counter
function updateCharCounter() {
    const message = document.getElementById('message').value;
    const counter = document.getElementById('charCount');
    counter.textContent = message.length;
    
    // Color based on length
    if (message.length > 280) {
        counter.style.color = 'var(--error)';
    } else if (message.length > 240) {
        counter.style.color = 'var(--warning)';
    } else {
        counter.style.color = 'var(--text-secondary)';
    }
}

// Handle image upload
function handleImageUpload(e) {
    const file = e.target.files[0];
    const fileNameEl = document.getElementById('fileName');
    const previewEl = document.getElementById('imagePreview');
    
    if (file) {
        fileNameEl.textContent = file.name;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            previewEl.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
        };
        reader.readAsDataURL(file);
    } else {
        fileNameEl.textContent = 'Dosya seçilmedi';
        previewEl.innerHTML = '';
    }
}

// Update selected platforms
function updateSelectedPlatforms() {
    const checkboxes = document.querySelectorAll('input[type="checkbox"][id^="platform_"]');
    selectedPlatforms = Array.from(checkboxes)
        .filter(cb => cb.checked)
        .map(cb => cb.value);
    
    console.log('Seçili platformlar:', selectedPlatforms);
}

// Handle form submit
async function handleSubmit(e) {
    e.preventDefault();
    
    // Validation
    const message = document.getElementById('message').value.trim();
    if (!message) {
        showError('Lütfen bir mesaj girin');
        return;
    }
    
    if (selectedPlatforms.length === 0) {
        showError('Lütfen en az bir platform seçin');
        return;
    }
    
    // Prepare form data
    const formData = new FormData();
    formData.append('message', message);
    formData.append('platforms', selectedPlatforms.join(','));
    
    const imageInput = document.getElementById('image');
    if (imageInput.files[0]) {
        formData.append('image', imageInput.files[0]);
    }
    
    // Show loading
    setLoading(true);
    hideResults();
    
    try {
        const response = await fetch(`${API_URL}/api/publish`, {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        // Show results
        showResults(data);
        
    } catch (error) {
        console.error('Paylaşım hatası:', error);
        showError('Paylaşım sırasında hata oluştu: ' + error.message);
    } finally {
        setLoading(false);
    }
}

// Set loading state
function setLoading(loading) {
    const submitBtn = document.getElementById('submitBtn');
    const btnText = document.getElementById('btnText');
    const btnLoading = document.getElementById('btnLoading');
    
    submitBtn.disabled = loading;
    btnText.style.display = loading ? 'none' : 'inline';
    btnLoading.style.display = loading ? 'inline-flex' : 'none';
}

// Show results
function showResults(data) {
    const resultsEl = document.getElementById('results');
    resultsEl.style.display = 'block';
    
    let html = '<h3>📊 Paylaşım Sonuçları</h3>';
    
    // Success message
    if (data.success) {
        html += '<div class="alert alert-success">✅ Başarıyla paylaşıldı!</div>';
    } else {
        html += '<div class="alert alert-error">⚠️ Bazı paylaşımlarda hata oluştu</div>';
    }
    
    // Individual results
    if (data.results) {
        Object.entries(data.results).forEach(([platform, result]) => {
            const platformData = platforms[platform];
            const statusClass = result.status === 'success' ? 'success' : 
                               result.status === 'error' ? 'error' : 'info';
            
            const icon = result.status === 'success' ? '✅' : 
                        result.status === 'error' ? '❌' : 'ℹ️';
            
            html += `
                <div class="result-item ${statusClass}">
                    <div class="result-icon">${platformData?.icon || '📱'}</div>
                    <div class="result-content">
                        <div class="result-platform">${platformData?.name || platform}</div>
                        <div class="result-message">
                            ${result.message || (result.status === 'success' ? 'Başarıyla paylaşıldı' : 'Hata oluştu')}
                        </div>
                    </div>
                </div>
            `;
        });
    }
    
    resultsEl.innerHTML = html;
    
    // Scroll to results
    resultsEl.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

// Hide results
function hideResults() {
    const resultsEl = document.getElementById('results');
    resultsEl.style.display = 'none';
}

// Show error
function showError(message) {
    const resultsEl = document.getElementById('results');
    resultsEl.style.display = 'block';
    resultsEl.innerHTML = `
        <div class="alert alert-error">
            ❌ ${message}
        </div>
    `;
}

// Utility: Format date
function formatDate(date) {
    return new Date(date).toLocaleString('tr-TR');
}

