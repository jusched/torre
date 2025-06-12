// Reference for HTML elements
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const resultsContainer = document.getElementById('resultsContainer');
const messageArea = document.getElementById('messageArea');


// Displays the {message} and the {type} of message
function displayMessage(message, type = 'info') {
    messageArea.textContent = message;
    messageArea.className = 'message ' + type;
}

// Clear results container and message area
function clearResults() {
    resultsContainer.innerHTML = '';
    messageArea.textContent = '';
    messageArea.className = 'message';
}

// Creates and appends a person card to the results container
function createPersonCard(person) {
    
}