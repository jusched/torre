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
function createPersonCard(personData) {
    const card = document.createElement('div');
    card.className = 'person-card';

    // Get data from the personData
    const name = personData.name || 'N/A';
    const username = personData.username || ''
    const professionalHeadline = personData.professionalHeadline || '';
    const picture = personData.imageUrl || 'https://st3.depositphotos.com/6672868/13701/v/450/depositphotos_137014128-stock-illustration-default-avatar-profile-icon-vector.jpg'; // Placeholder image
    const completion = personData.completion || 0; // Default to 0 if not available
    // Weight of person's recommendations
    const personWeight = personData.personWeight || 0; // Default to 0 if not available


    const torreProfileURL = username ? `https://torre.ai/${username}` : '#';

    card.innerHTML = `
        <img src="${picture}" alt="${name}" class="profile-picture">
        <h2>${name}</h2>
        ${professionalHeadline ? `<p class="professional-headline">${professionalHeadline}</p>` : ''}
        <p class="completion"><strong>Profile completion: </strong> ${completion}</p>
        <p class="weight"><strong>Recommendation Weight: </strong> ${personWeight}</p>
        <p><a href="${torreProfileURL}" target="_blank" rel="noopener noreferrer">Torre.ai Profile</a></p>
    `;
    resultsContainer.appendChild(card);
}


async function searchPeople() {
    clearResults(); // Clear previous results and messages
    const query = searchInput.value.trim(); // Get input value and remove whitespace

    // Stop if query is empty
    if (!query) {
        displayMessage('Please enter a name or keyword to search.', 'info');
        return; 
    }

    displayMessage('Searching...', 'info'); // Show loading message

    try {
        // Construct the URL for the FastAPI backend
        //! IMPORTANT: Replace URL after deployment
        const backendUrl = `http://127.0.0.1:8000/search-people?query=${encodeURIComponent(query)}`;

        // Make the request to our FastAPI backend
        const response = await fetch(backendUrl);

        if (!response.ok) {
            // If not OK, parse error message from backend if available, or use status text
            const errorData = await response.json().catch(() => ({})); // Try to parse, ignore if not JSON
            const errorMessage = errorData.detail || `HTTP error! Status: ${response.status} - ${response.statusText}`;
            throw new Error(errorMessage);
        }

        const data = await response.json(); // Parse the JSON response from backend

        // Check if backend sent a 'message' indicating no results or if 'results' array is present
        if (data.message && data.results && data.results.length === 0) {
            displayMessage(data.message, 'info'); // "No people found." message from backend
        } else if (Array.isArray(data) && data.length > 0) {
            // If data is an array of results
            displayMessage(`Found ${data.length} results.`, 'success');

            // Create a card for each person
            data.forEach(person => {
                createPersonCard(person); 
            });

        } else {
            // Handle unexpected data format or no results
            displayMessage('No people found for your query or unexpected data format.', 'info');
        }

    } catch (error) {
        console.error('Search failed:', error);
        displayMessage(`Error during search: ${error.message}. Please try again.`, 'error');
    }
}


// Listen for clicks on the search button
searchButton.addEventListener('click', searchPeople);

// Listen for 'Enter' key press in the search input field
searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchPeople();
    }
});

// Initial focus on the search input when page loads
window.addEventListener('load', () => {
    searchInput.focus();
});