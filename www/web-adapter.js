// Web adapter to bridge Eel calls to Flask API when running on web
if (typeof eel === 'undefined') {
    console.log("Running in web mode. Adapter initialized.");
    
    window.eel = {
        _exposed_functions: {},
        
        expose: function(func, name) {
            this._exposed_functions[name || func.name] = func;
        },
        
        // Mock Eel calls to Flask API
        allCommands: function(message) {
            let query = message;
            return async function(callback) {
                const response = await fetch('/api/allCommands', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query})
                });
                const data = await response.json();
                if (data.success) {
                    // Call exposed functions like a real Eel server would
                    if (window.eel._exposed_functions['senderText']) {
                        window.eel._exposed_functions['senderText'](query);
                    }
                    if (window.eel._exposed_functions['DisplayMessage']) {
                        window.eel._exposed_functions['DisplayMessage'](data.response);
                    }
                    if (window.eel._exposed_functions['receiverText']) {
                        window.eel._exposed_functions['receiverText'](data.response);
                    }
                    if (window.eel._exposed_functions['ShowHood']) {
                        window.eel._exposed_functions['ShowHood']();
                    }
                    if (callback) callback(data);
                }
            };
        },
        
        playAssistantSound: function() {
            return function() { console.log("Sound played (mock)"); };
        },
        
        get_system_stats: function() {
            return async function(callback) {
                const res = await fetch('/api/get_system_stats');
                const data = await res.json();
                if (callback) callback(data);
                return data;
            };
        },
        
        init: function() {
            return function() { 
                console.log("Eel init (mock)");
                // Auto-skip loader for web demo
                setTimeout(() => {
                    if (window.eel._exposed_functions['hideLoader']) {
                        window.eel._exposed_functions['hideLoader']();
                    }
                }, 1000);
            };
        },

        on_auth_success: function() {
            return function() {
                if (window.eel._exposed_functions['hideFaceAuth']) window.eel._exposed_functions['hideFaceAuth']();
                if (window.eel._exposed_functions['hideFaceAuthSuccess']) window.eel._exposed_functions['hideFaceAuthSuccess']();
                if (window.eel._exposed_functions['hideStart']) window.eel._exposed_functions['hideStart']();
            };
        },

        password_login: function(pass) {
            return function(callback) {
                // Mock login for demo
                callback({success: true});
            };
        },

        get_conversations: function() {
            return function(callback) {
                callback({success: true, data: []});
            };
        }
    };
    
    // Polyfill expose
    window.eel.expose = function(func, name) {
        window.eel._exposed_functions[name || func.name] = func;
    };
}
