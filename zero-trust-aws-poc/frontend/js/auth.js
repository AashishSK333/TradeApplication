// Configuration - will be updated during deployment
const cognitoConfig = {
    region: '${aws_region}',
    userPoolId: '${user_pool_id}',
    clientId: '${client_id}'
};

// Amazon Cognito Identity SDK
const poolData = {
    UserPoolId: cognitoConfig.userPoolId,
    ClientId: cognitoConfig.clientId
};

// Create new credentials object
function initAWSCredentials() {
    if (!AWS.config.credentials || AWS.config.credentials.expired) {
        AWS.config.region = cognitoConfig.region;
        AWS.config.credentials = new AWS.CognitoIdentityCredentials({
            IdentityPoolId: cognitoConfig.identityPoolId
        });
    }
}

// Initialize Amazon Cognito
const userPool = new AmazonCognitoIdentity.CognitoUserPool(poolData);
let currentUser = null;
let idToken = null;
let accessToken = null;

function showSignup() {
    document.getElementById('login-form').style.display = 'none';
    document.getElementById('signup-form').style.display = 'block';
}

function showLogin() {
    document.getElementById('signup-form').style.display = 'none';
    document.getElementById('login-form').style.display = 'block';
}

function signup() {
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    
    const attributeList = [
        new AmazonCognitoIdentity.CognitoUserAttribute({ 
            Name: 'email',
            Value: email 
        })
    ];
    
    userPool.signUp(email, password, attributeList, null, (err, result) => {
        if (err) {
            alert(err.message);
            return;
        }
        alert('User registered successfully! Please check your email for verification.');
        showLogin();
    });
}

function login() {
    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;
    
    const authenticationData = {
        Username: email,
        Password: password
    };
    
    const authenticationDetails = new AmazonCognitoIdentity.AuthenticationDetails(authenticationData);
    const userData = {
        Username: email,
        Pool: userPool
    };
    
    currentUser = new AmazonCognitoIdentity.CognitoUser(userData);
    
    currentUser.authenticateUser(authenticationDetails, {
        onSuccess: function(result) {
            idToken = result.getIdToken().getJwtToken();
            accessToken = result.getAccessToken().getJwtToken();
            
            document.getElementById('username').textContent = email;
            document.getElementById('login-form').style.display = 'none';
            document.getElementById('app').style.display = 'block';
            
            // Store the tokens in localStorage
            localStorage.setItem('idToken', idToken);
            localStorage.setItem('accessToken', accessToken);
        },
        onFailure: function(err) {
            alert(err.message || JSON.stringify(err));
        }
    });
}

function logout() {
    if (currentUser) {
        currentUser.signOut();
        currentUser = null;
        idToken = null;
        accessToken = null;
        localStorage.removeItem('idToken');
        localStorage.removeItem('accessToken');
        document.getElementById('app').style.display = 'none';
        document.getElementById('login-form').style.display = 'block';
    }
}

function isAuthenticated() {
    return currentUser !== null && idToken !== null;
}

function getAuthToken() {
    return idToken || localStorage.getItem('idToken');
}