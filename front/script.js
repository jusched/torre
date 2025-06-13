// DOM element references
const searchInput = document.getElementById('searchInput');
const searchButton = document.getElementById('searchButton');
const resultsContainer = document.getElementById('resultsContainer');
const messageArea = document.getElementById('messageArea');
const profileDetail = document.getElementById('profileDetail');


// Deployed backend URL
const BACKEND_BASE_URL = "https://torre-y6y2.onrender.com";


// Function to display messages in the message area for user feedback
function displayMessage(message, type = 'info') {
    messageArea.textContent = message;
    messageArea.className = `message ${type}`;
}


// Clear previous results and messages
function clearResults() {
    resultsContainer.innerHTML = '';
    messageArea.textContent = '';
    messageArea.className = 'message';
    profileDetail.innerHTML = '';
    profileDetail.style.display = 'none';
    resultsContainer.style.display = 'grid';
}


// Function to create a person card and append it to the results
function createPersonCard(personData) {
    const card = document.createElement('div');
    card.className = 'person-card';

    // Save the username for later ID on the profile detail view
    const profileIdentifier = personData.publicId || personData.username || '';
    card.dataset.profileId = profileIdentifier;

    const name = personData.name || 'N/A';
    const professionalHeadline = personData.professionalHeadline || '';
    const imageUrl = personData.imageUrl || 'https://st3.depositphotos.com/6672868/13701/v/450/depositphotos_137014128-stock-illustration-default-avatar-profile-icon-vector.jpg';

    const torreProfileLink = profileIdentifier ? `https://torre.ai/${profileIdentifier}` : '#';

    const isDetailsAvailable = !!profileIdentifier;
    const buttonClass = isDetailsAvailable ? "view-details-button" : "view-details-button disabled";
    const buttonDisabled = isDetailsAvailable ? "" : "disabled";

    // Create the card content for all names we find
    card.innerHTML = `
        <img src="${imageUrl}" alt="${name}" class="profile-picture">
        <h2>${name}</h2>
        ${professionalHeadline ? `<p class="professional-headline">${professionalHeadline}</p>` : ''}
        <p><a href="${torreProfileLink}" target="_blank" rel="noopener noreferrer">View Torre.ai Profile</a></p>
        <button class="${buttonClass}" data-profile-id="${profileIdentifier}" ${buttonDisabled}>View Details</button>
    `;
    resultsContainer.appendChild(card);
}


// Function to display profile details based on the profile identifier
async function displayProfileDetails(profileIdentifier) {
    profileDetail.innerHTML = '';
    profileDetail.style.display = 'none';
    displayMessage(`Loading profile for ${profileIdentifier}...`, 'info');

    resultsContainer.style.display = 'none';

    try {
        // const backendUrl = `http://127.0.0.1:8000/profile/${encodeURIComponent(profileIdentifier)}`;
        const backendUrl = `${BACKEND_BASE_URL}/profile/${encodeURIComponent(profileIdentifier)}`;
        const response = await fetch(backendUrl);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || `HTTP error! Status: ${response.status} - ${response.statusText}`;
            throw new Error(errorMessage);
        }

        const profileData = await response.json();

        if (!profileData || !profileData.person || !profileData.person.publicId) {
            displayMessage(`Profile for '${profileIdentifier}' not found or no details available.`, 'error');
            resultsContainer.style.display = 'grid';
            return;
        }

        profileDetail.style.display = 'flex';
        profileDetail.innerHTML = `
            <h2>${profileData.person.name || 'Profile'} Details</h2>

            ${profileData.person.picture || profileData.person.pictureThumbnail ? `
                <img src="${profileData.person.picture || profileData.person.pictureThumbnail}"
                     alt="${profileData.person.name || 'Profile Picture'}"
                     class="profile-detail-picture">
            ` : `<img src="https://st3.depositphotos.com/6672868/13701/v/450/depositphotos_137014128-stock-illustration-default-avatar-profile-icon-vector.jpg"
                        alt="Placeholder Picture"
                        class="profile-detail-picture">`}

            <p><strong>Professional Headline:</strong> ${profileData.person.professionalHeadline || 'N/A'}</p>
            <p><strong>Bio:</strong> ${profileData.person.summaryOfBio || 'No summary available.'}</p>

            ${profileData.jobs && profileData.jobs.length > 0 ? `
                <div class="section-title">Jobs:</div>
                ${profileData.jobs.map(job => {
            return `
                        <div class="experience-item">
                            <h3>${job.name || 'N/A'}</h3>
                            <p>${job.organizations && job.organizations[0] ? job.organizations[0].name : 'N/A Organization'}</p>
                        </div>
                    `;
        }).join('')}
            ` : '<p class="section-title">No jobs listed.</p>'}

            <p><a href="https://torre.ai/${profileIdentifier}" target="_blank" rel="noopener noreferrer">View Full Torre.ai Profile</a></p>
        `;
        displayMessage('');


    } catch (error) {
        console.error('Failed to load profile:', error);
        displayMessage(`Error loading profile: ${error.message}. Please try again.`, 'error');
        profileDetail.style.display = 'none';
        resultsContainer.style.display = 'grid';
    }
}


// Main search function to handle user input and fetch results from the backend
async function searchPeople() {
    clearResults();
    const query = searchInput.value.trim();

    if (!query) {
        displayMessage('Please enter a name or keyword to search.', 'info');
        return;
    }

    displayMessage('Searching...', 'info');

    try {
        // const backendUrl = `http://127.0.0.1:8000/search-people?query=${encodeURIComponent(query)}`;
        const backendUrl = `${BACKEND_BASE_URL}/search-people?query=${encodeURIComponent(query)}`;
        const response = await fetch(backendUrl);

        if (!response.ok) {
            const errorData = await response.json().catch(() => ({}));
            const errorMessage = errorData.detail || `HTTP error! Status: ${response.status} - ${response.statusText}`;
            throw new Error(errorMessage);
        }

        const data = await response.json();

        if (data.message && data.results && data.results.length === 0) {
            displayMessage(data.message, 'info');
        } 
        else if (Array.isArray(data) && data.length > 0) {
            displayMessage(`Found ${data.length} results.`, 'success');
            data.forEach(person => {
                createPersonCard(person);
            });
        } 
        else {
            displayMessage('No people found for your query or unexpected data format.', 'info');
        }

    } catch (error) {
        console.error('Search failed:', error);
        displayMessage(`Error during search: ${error.message}. Please try again.`, 'error');
    }
}


// Event listeners for search button and input field to trigger search
searchButton.addEventListener('click', searchPeople);
searchInput.addEventListener('keypress', (event) => {
    if (event.key === 'Enter') {
        searchPeople();
    }
});

window.addEventListener('load', () => {
    searchInput.focus();
});


// Event listener for clicking on a person card to view profile details
resultsContainer.addEventListener('click', (event) => {

    if (event.target.classList.contains('view-details-button')) {
        const profileIdentifier = event.target.dataset.profileId;

        if (profileIdentifier) {
            displayProfileDetails(profileIdentifier);
            profileDetail.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
        else {
            console.warn("No profile identifier found for this card, cannot view details.");
            displayMessage('Cannot view details: identifier missing.', 'error');
        }
    }
});