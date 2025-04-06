// frontend/tracing.js
(function() {
    // Generate a valid X-Ray trace ID format
    function generateXRayTraceId() {
        const timestamp = Math.floor(Date.now() / 1000).toString(16).padStart(8, '0');
        const random = Array.from({length: 24}, () => 
            Math.floor(Math.random() * 16).toString(16)).join('');
        return `1-${timestamp}-${random}`;
    }

    // Generate a random span ID
    function generateSpanId() {
        return Array.from({length: 16}, () => 
            Math.floor(Math.random() * 16).toString(16)).join('');
    }

    // Patch fetch API to add trace headers
    const originalFetch = window.fetch;
    window.fetch = function(resource, options) {
        options = options || {};
        options.headers = options.headers || {};
        
        // Generate or reuse trace ID
        const traceId = window.currentTraceId || generateXRayTraceId();
        window.currentTraceId = traceId;
        
        const spanId = generateSpanId();
        
        // Add X-Ray trace header
        options.headers['X-Amzn-Trace-Id'] = `Root=${traceId}`;
        
        console.log(`Adding trace ID ${traceId} to request`);
        
        return originalFetch.call(this, resource, options);
    };
    
    // Patch XMLHttpRequest for completeness
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function() {
        this._url = arguments[1];
        return originalOpen.apply(this, arguments);
    };
    
    const originalSend = XMLHttpRequest.prototype.send;
    XMLHttpRequest.prototype.send = function() {
        const traceId = window.currentTraceId || generateXRayTraceId();
        window.currentTraceId = traceId;
        
        this.setRequestHeader('X-Amzn-Trace-Id', `Root=${traceId}`);
        console.log(`Adding trace ID ${traceId} to XHR request`);
        
        return originalSend.apply(this, arguments);
    };
    
    console.log("X-Ray tracing initialized in browser");
})();