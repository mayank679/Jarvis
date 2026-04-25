// Web adapter to bridge Eel calls to Flask API when running on web
if (typeof eel === 'undefined') {
    console.log("Running in web mode. Adapter initialized.");
    
    window.eel = {
        _exposed_functions: {},
        _initDone: false,
        
        expose: function(func, name) {
            this._exposed_functions[name || func.name] = func;
        },
        
        // Mock Eel calls to Flask API
        allCommands: function(message) {
            let query = message;
            return async function(callback) {
                try {
                    const response = await fetch('/api/allCommands', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query})
                    });
                    const data = await response.json();
                    if (data.success) {
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
                } catch(e) {
                    console.error("allCommands error:", e);
                }
            };
        },
        
        playAssistantSound: function() {
            return function() { console.log("Sound played (mock)"); };
        },
        
        get_system_stats: function() {
            return async function(callback) {
                try {
                    const res = await fetch('/api/get_system_stats');
                    const data = await res.json();
                    if (callback) callback(data);
                    return data;
                } catch(e) {
                    console.error("get_system_stats error:", e);
                    return {cpu: 0, battery: 100, plugged: true};
                }
            };
        },
        
        // This is called by main.js at startup
        init: function() {
            return function() { 
                console.log("Eel init (mock) - will auto-skip to main UI");
                window.eel._initDone = true;
                // Don't do anything here - we handle it in _autoSkip below
            };
        },

        on_auth_success: function() {
            return function() {
                // no-op in web mode
            };
        },

        password_login: function(pass) {
            return function(callback) {
                if (callback) callback({success: true});
            };
        },

        get_conversations: function() {
            return function(callback) {
                if (callback) callback({success: true, data: []});
            };
        },

        get_messages: function(id) {
            return function(callback) {
                if (callback) callback({success: true, data: []});
            };
        },

        create_conversation: function(title) {
            return function(callback) {
                if (callback) callback({success: true, conversation_id: 1});
            };
        },

        save_message: function(conv_id, user_msg, bot_msg) {
            return function() {};
        },

        delete_conversation: function(id) {
            return function(callback) {
                if (callback) callback({success: true});
            };
        },

        set_system_volume: function() { return function() {}; },
        set_system_brightness: function() { return function() {}; },
        set_voice_rate: function() { return function() {}; },
        set_voice_gender: function() { return function() {}; },
        analyze_image: function() { return function() {}; },
        face_login: function() { return function(cb) { if(cb) cb({success:false}); }; },

        // Auto-skip to main UI after all scripts have loaded
        _autoSkip: function() {
            // Wait for jQuery and controller.js to be ready
            var checkReady = setInterval(function() {
                // Check if jQuery is loaded and hideStart is registered
                if (typeof $ !== 'undefined' && window.eel._exposed_functions['hideStart']) {
                    clearInterval(checkReady);
                    console.log("All scripts loaded. Skipping to main UI...");
                    
                    // Hide the Start section directly
                    $("#Start").attr("hidden", true);
                    $("#Oval").attr("hidden", false);
                    $("#Oval").addClass("animate__animated animate__zoomIn");
                    
                    // Show welcome message
                    if (window.eel._exposed_functions['DisplayMessage']) {
                        window.eel._exposed_functions['DisplayMessage']("Welcome! Jarvis Web is online.");
                    }
                    
                    // Show HUD
                    setTimeout(function() {
                        $("#system-hud").fadeIn('slow');
                    }, 500);
                }
            }, 200); // Check every 200ms

            // Safety timeout - force skip after 5 seconds no matter what
            setTimeout(function() {
                clearInterval(checkReady);
                var startEl = document.getElementById('Start');
                var ovalEl = document.getElementById('Oval');
                if (startEl && !startEl.hidden) {
                    console.log("Force-skipping initialization (safety timeout)");
                    startEl.hidden = true;
                    if (ovalEl) ovalEl.hidden = false;
                }
            }, 5000);
        }
    };
    
    // Polyfill expose (ensure it's always available)
    window.eel.expose = function(func, name) {
        window.eel._exposed_functions[name || func.name] = func;
    };

    // Kick off auto-skip when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.eel._autoSkip();
        });
    } else {
        // DOM already loaded
        window.eel._autoSkip();
    }
}
