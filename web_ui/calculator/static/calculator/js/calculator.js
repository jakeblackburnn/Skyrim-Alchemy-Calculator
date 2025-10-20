// Helper function to get selected ingredients
function getSelectedIngredients() {
    return Array.from(document.querySelectorAll('.ingredient-check:checked'))
        .map(checkbox => checkbox.value);
}

// Helper function to show error message
function showError(message) {
    const container = document.getElementById('results-container');
    container.innerHTML = `
        <div class="error-message">
            <strong>Error:</strong> ${message}
        </div>
    `;
}

// Helper function to show loading state
function showLoadingSpinner() {
    const container = document.getElementById('results-container');
    const button = document.getElementById('calculate-btn');

    container.innerHTML = `
        <div class="loading-spinner">
            <div class="spinner"></div>
            <p>Calculating potions...</p>
        </div>
    `;

    button.classList.add('disabled');
    button.style.color = '#ccc9bf';
    button.style.cursor = 'not-allowed';
}

// Helper function to hide loading state
function hideLoadingSpinner() {
    const button = document.getElementById('calculate-btn');
    button.classList.remove('disabled');
    button.style.color = '#50c9a5';
    button.style.cursor = 'pointer';
}

// Render potions to the results container
function renderPotions(potions) {
    const container = document.getElementById('results-container');

    if (potions.length === 0) {
        container.innerHTML = `
            <div style="color: #666666; text-align: center; padding: 40px;">
                <p>No valid potions found with the selected ingredients.</p>
            </div>
        `;
        return;
    }

    let html = '';

    potions.forEach(potion => {
        html += `
            <div class="potion-card">
                <h3>${potion.name}</h3>
                <p class="potion-value">${potion.total_value} gold</p>
                <p class="ingredients">${potion.ingredients.join(' + ')}</p>
                <div class="effects-list">
                    ${potion.effects.map(effect => `
                        <div class="effect ${effect.is_poison ? 'poison' : 'beneficial'}">
                            ${effect.description}
                        </div>
                    `).join('')}
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

// Helper function to get CSRF token from cookie
function getCsrfToken() {
    const name = 'csrftoken';
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Main calculation function
async function calculatePotions() {
    const ingredients = getSelectedIngredients();

    // Validate minimum 2 ingredients
    if (ingredients.length < 2) {
        showError('Please select at least 2 ingredients');
        return;
    }

    // Build payload
    const payload = {
        skill: parseInt(document.getElementById('skill-level').value),
        fortify: parseInt(document.getElementById('fortify-alchemy').value),
        alchemist_rank: parseInt(document.getElementById('alchemist-rank').value),
        physician: document.getElementById('perk-physician').checked,
        benefactor: document.getElementById('perk-benefactor').checked,
        poisoner: document.getElementById('perk-poisoner').checked,
        purity: document.getElementById('perk-purity').checked,
        seeker: document.getElementById('perk-seeker').checked,
        ingredients: ingredients
    };

    // Show loading state
    showLoadingSpinner();

    try {
        const response = await fetch('/api/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCsrfToken(),
            },
            body: JSON.stringify(payload)
        });

        const data = await response.json();

        if (response.ok) {
            renderPotions(data.potions);
        } else {
            showError(data.error || 'An error occurred while calculating potions');
        }
    } catch (error) {
        showError('Network error: ' + error.message);
    } finally {
        hideLoadingSpinner();
    }
}

// Match results section height to input section
function matchSectionHeights() {
    const inputSection = document.querySelector('.input-section');
    const resultsSection = document.querySelector('.results-section');
    const resultsContent = document.getElementById('results-container');

    if (inputSection && resultsSection && resultsContent) {
        const inputHeight = inputSection.offsetHeight;
        resultsSection.style.height = `${inputHeight}px`;

        // Calculate available height for scrollable content
        const titleHeight = resultsSection.querySelector('.section-title').offsetHeight;
        const padding = 40; // Account for padding and margins
        resultsContent.style.height = `${inputHeight - titleHeight - padding}px`;
    }
}

// Attach event listener to calculate button
document.addEventListener('DOMContentLoaded', function() {
    document.getElementById('calculate-btn').addEventListener('click', calculatePotions);

    // Match heights on load
    matchSectionHeights();

    // Re-match heights on window resize
    window.addEventListener('resize', matchSectionHeights);
});
