// Keep these existing functions unchanged
function navigateTo(page) {
    document.querySelectorAll('.container').forEach(el => el.classList.add('hidden'));
    document.getElementById(`${page}-page`).classList.remove('hidden');
    
    if(page === 'symptoms') {
        // Add any specific logic for symptoms page
    }
}

function goBack() {
    document.querySelectorAll('.container').forEach(el => el.classList.add('hidden'));
    document.getElementById('home-page').classList.remove('hidden');
}

function selectDisease(element) {
    document.querySelectorAll('.disease-option').forEach(el => el.style.background = 'white');
    element.style.background = '#e3f2fd';
    // Add disease selection logic here
}

// Replace JUST the viewResults function with the new version
async function viewResults() {
    const textInput = document.querySelector('textarea').value;
    const fileInput = document.querySelector('input[type="file"]').files[0];
    
    const formData = new FormData();
    formData.append('text', textInput);
    if(fileInput) formData.append('file', fileInput);

    try {
        const response = await fetch('http://localhost:5000/analyze', {
            method: 'POST',
            body: formData
        });

        const result = await response.json();
        
        if(result.success) {
            const analysis = result.analysis.replace(/\n/g, '<br>');
            showResultsModal(analysis);
        } else {
            alert(`Error: ${result.error}`);
        }
    } catch (error) {
        alert(`Request failed: ${error}`);
    }
}

// Add this new function at the bottom
function showResultsModal(content) {
    const modal = document.createElement('div');
    modal.className = 'modal';
    modal.innerHTML = `
        <div class="modal-content">
            <h2>Analysis Results</h2>
            <div class="analysis-output">${content}</div>
            <button onclick="this.parentElement.parentElement.remove()">Close</button>
        </div>
    `;
    document.body.appendChild(modal);
}