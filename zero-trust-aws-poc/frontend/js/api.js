const API_URL = '${api_url}';

async function callSecureAPI(endpoint, method = 'GET', data = null) {
    const token = getAuthToken();
    if (!token) {
        throw new Error('User is not authenticated');
    }
    
    const headers = {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json'
    };
    
    const options = {
        method,
        headers
    };
    
    if (data) {
        options.body = JSON.stringify(data);
    }
    
    try {
        const response = await fetch(`${API_URL}${endpoint}`, options);
        
        if (!response.ok) {
            throw new Error(`API error: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('API call failed:', error);
        throw error;
    }
}

async function fetchUserData() {
    try {
        const data = await callSecureAPI('/users/me');
        document.getElementById('user-data').innerHTML = 
            `<pre>${JSON.stringify(data, null, 2)}</pre>`;
    } catch (error) {
        document.getElementById('user-data').innerHTML = 
            `<p class="error">Error: ${error.message}</p>`;
    }
}