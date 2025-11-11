// WebAuthn and Device Fingerprinting JavaScript
// Handles Face ID, Touch ID, Windows Hello, and device fingerprinting

// Device Fingerprinting - Collect device characteristics
function collectDeviceFingerprint() {
    const fingerprint = {
        // Screen information
        screen: {
            width: screen.width,
            height: screen.height,
            colorDepth: screen.colorDepth,
            pixelDepth: screen.pixelDepth,
            availWidth: screen.availWidth,
            availHeight: screen.availHeight
        },
        // Browser information
        browser: {
            userAgent: navigator.userAgent,
            language: navigator.language,
            languages: navigator.languages,
            platform: navigator.platform,
            cookieEnabled: navigator.cookieEnabled,
            doNotTrack: navigator.doNotTrack,
            hardwareConcurrency: navigator.hardwareConcurrency || 'unknown',
            maxTouchPoints: navigator.maxTouchPoints || 0
        },
        // Timezone
        timezone: {
            timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
            timezoneOffset: new Date().getTimezoneOffset()
        },
        // Canvas fingerprint (basic)
        canvas: {
            supported: typeof document.createElement('canvas').getContext === 'function'
        },
        // WebGL fingerprint (basic)
        webgl: {
            supported: (function() {
                try {
                    const canvas = document.createElement('canvas');
                    return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
                } catch (e) {
                    return false;
                }
            })()
        },
        // Touch support
        touch: {
            supported: 'ontouchstart' in window || navigator.maxTouchPoints > 0
        },
        // Device orientation
        orientation: {
            angle: screen.orientation ? screen.orientation.angle : 'unknown',
            type: screen.orientation ? screen.orientation.type : 'unknown'
        },
        // Timestamp
        timestamp: new Date().toISOString()
    };
    
    return fingerprint;
}

// Convert ArrayBuffer to base64
function arrayBufferToBase64(buffer) {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
}

// Convert base64 to ArrayBuffer
function base64ToArrayBuffer(base64) {
    const binary = atob(base64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) {
        bytes[i] = binary.charCodeAt(i);
    }
    return bytes.buffer;
}

// WebAuthn Registration - Start
async function startWebAuthnRegistration(deviceName = null) {
    try {
        // Check if WebAuthn is supported
        if (!window.PublicKeyCredential) {
            throw new Error('WebAuthn is not supported in this browser. Please use a modern browser with biometric support.');
        }
        
        // Check if platform authenticator is available
        const available = await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
        if (!available) {
            throw new Error('Biometric authentication (Face ID/Touch ID) is not available on this device. Make sure you are using HTTPS or a browser that supports platform authenticators on localhost.');
        }
        
        // Get registration options from server
        const response = await fetch('/api/webauthn/register/begin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include'  // Include cookies for session
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to start registration');
        }
        
        const options = data.options;
        
        // Verify authenticatorSelection is requesting platform authenticators
        if (!options.authenticatorSelection || options.authenticatorSelection.authenticatorAttachment !== 'platform') {
            console.warn('Warning: Platform authenticator not explicitly requested. Browser may show QR code options.');
            console.log('Received authenticatorSelection:', options.authenticatorSelection);
        }
        
        // Convert options to WebAuthn format
        const publicKeyCredentialCreationOptions = {
            challenge: base64ToArrayBuffer(options.challenge),
            rp: options.rp,
            user: {
                id: base64ToArrayBuffer(options.user.id),
                name: options.user.name,
                displayName: options.user.displayName
            },
            pubKeyCredParams: options.pubKeyCredParams,
            authenticatorSelection: options.authenticatorSelection,
            timeout: options.timeout,
            excludeCredentials: options.excludeCredentials ? options.excludeCredentials.map(cred => ({
                id: base64ToArrayBuffer(cred.id),
                type: cred.type,
                transports: cred.transports
            })) : []
        };
        
        // Create credential using WebAuthn API
        const credential = await navigator.credentials.create({
            publicKey: publicKeyCredentialCreationOptions
        });
        
        // Convert credential to format expected by server
        const credentialForServer = {
            id: credential.id,
            rawId: arrayBufferToBase64(credential.rawId),
            response: {
                clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
                attestationObject: arrayBufferToBase64(credential.response.attestationObject)
            },
            type: credential.type
        };
        
        // Send credential to server
        const completeResponse = await fetch('/api/webauthn/register/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                credential: credentialForServer,
                device_name: deviceName || getDeviceName()
            })
        });
        
        const completeData = await completeResponse.json();
        
        if (completeData.success) {
            return { success: true, message: 'Biometric credential registered successfully!' };
        } else {
            throw new Error(completeData.error || 'Registration failed');
        }
    } catch (error) {
        console.error('WebAuthn registration error:', error);
        return { success: false, error: error.message };
    }
}

// WebAuthn Authentication - Start
async function startWebAuthnAuthentication(username) {
    try {
        // Check if WebAuthn is supported
        if (!window.PublicKeyCredential) {
            throw new Error('WebAuthn is not supported in this browser.');
        }
        
        // Get authentication options from server
        const response = await fetch('/api/webauthn/authenticate/begin', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({ username: username })
        });
        
        const data = await response.json();
        
        if (!data.success) {
            throw new Error(data.error || 'Failed to start authentication');
        }
        
        const options = data.options;
        
        // Convert options to WebAuthn format
        // Ensure we explicitly request platform authenticators (Face ID/Touch ID)
        const publicKeyCredentialRequestOptions = {
            challenge: base64ToArrayBuffer(options.challenge),
            allowCredentials: options.allowCredentials ? options.allowCredentials.map(cred => ({
                id: base64ToArrayBuffer(cred.id),
                type: cred.type || 'public-key',
                transports: cred.transports || ['internal']  // Force internal/platform transport
            })) : [],
            timeout: options.timeout || 60000,  // 60 second timeout
            userVerification: 'required',  // Force required - must use biometric
            rpId: options.rpId
        };
        
        // Log for debugging
        console.log('WebAuthn authentication options:', {
            allowCredentials: publicKeyCredentialRequestOptions.allowCredentials.length,
            userVerification: publicKeyCredentialRequestOptions.userVerification,
            rpId: publicKeyCredentialRequestOptions.rpId
        });
        
        // Get credential using WebAuthn API (triggers Face ID/Touch ID)
        // This will prompt the user for biometric confirmation
        const credential = await navigator.credentials.get({
            publicKey: publicKeyCredentialRequestOptions
        });
        
        // Convert credential to format expected by server
        const credentialForServer = {
            id: credential.id,
            rawId: arrayBufferToBase64(credential.rawId),
            response: {
                clientDataJSON: arrayBufferToBase64(credential.response.clientDataJSON),
                authenticatorData: arrayBufferToBase64(credential.response.authenticatorData),
                signature: arrayBufferToBase64(credential.response.signature),
                userHandle: credential.response.userHandle ? arrayBufferToBase64(credential.response.userHandle) : null
            },
            type: credential.type
        };
        
        // Collect device fingerprint
        const deviceInfo = collectDeviceFingerprint();
        
        // Send credential to server
        const completeResponse = await fetch('/api/webauthn/authenticate/complete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                credential: credentialForServer,
                device_info: deviceInfo
            })
        });
        
        const completeData = await completeResponse.json();
        
        console.log('Authentication complete response:', completeData);
        
        if (completeData.success) {
            console.log('Authentication successful, redirecting to:', completeData.redirect);
            return { success: true, redirect: completeData.redirect };
        } else {
            console.error('Authentication failed:', completeData.error);
            throw new Error(completeData.error || 'Authentication failed');
        }
    } catch (error) {
        console.error('WebAuthn authentication error:', error);
        return { success: false, error: error.message };
    }
}

// Get device name for display
function getDeviceName() {
    const ua = navigator.userAgent;
    if (/iPhone|iPad|iPod/.test(ua)) {
        return 'iOS Device';
    } else if (/Android/.test(ua)) {
        return 'Android Device';
    } else if (/Mac/.test(ua)) {
        return 'Mac';
    } else if (/Windows/.test(ua)) {
        return 'Windows PC';
    } else if (/Linux/.test(ua)) {
        return 'Linux PC';
    }
    return 'Unknown Device';
}

// Store device fingerprint (called after login)
async function storeDeviceFingerprint() {
    try {
        const deviceInfo = collectDeviceFingerprint();
        
        const response = await fetch('/api/device-fingerprint', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            credentials: 'include',
            body: JSON.stringify({
                device_info: deviceInfo
            })
        });
        
        const data = await response.json();
        return data;
    } catch (error) {
        console.error('Device fingerprint error:', error);
        return { success: false, error: error.message };
    }
}

// Check if WebAuthn is available
function isWebAuthnAvailable() {
    return typeof window.PublicKeyCredential !== 'undefined';
}

// Check if platform authenticator is available (async)
async function isPlatformAuthenticatorAvailable() {
    if (!isWebAuthnAvailable()) {
        return false;
    }
    try {
        return await PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable();
    } catch (e) {
        return false;
    }
}

