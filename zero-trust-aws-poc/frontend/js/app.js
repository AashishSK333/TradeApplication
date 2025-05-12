document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already signed in
    const cognitoUser = userPool.getCurrentUser();
    
    if (cognitoUser != null) {
        cognitoUser.getSession((err, session) => {
            if (err) {
                console.error(err);
                return;
            }
            
            if (session.isValid()) {
                currentUser = cognitoUser;
                idToken = session.getIdToken().getJwtToken();
                accessToken = session.getAccessToken().getJwtToken();
                
                cognitoUser.getUserAttributes((err, attributes) => {
                    if (err) {
                        console.error(err);
                        return;
                    }
                    
                    const emailAttribute = attributes.find(attr => attr.Name === 'email');
                    if (emailAttribute) {
                        document.getElementById('username').textContent = emailAttribute.Value;
                    }
                    
                    document.getElementById('login-form').style.display = 'none';
                    document.getElementById('app').style.display = 'block';
                });
            }
        });
    }
});