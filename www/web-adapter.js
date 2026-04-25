// Web adapter to bridge Eel calls to Flask API when running on web
if (typeof eel === 'undefined') {
    console.log("Running in web mode. Adapter initialized.");
    
    window.eel = {
        _exposed_functions: {},
        _initDone: false,
        
        expose: function(func, name) {
            this._exposed_functions[name || func.name] = func;
        },
        
        // ─── AI Chat ────────────────────────────────────────────────
        allCommands: function(message) {
            let query = message;
            return async function(callback) {
                try {
                    // Show a "thinking…" message while waiting
                    if (window.eel._exposed_functions['DisplayMessage']) {
                        window.eel._exposed_functions['DisplayMessage']("Processing...");
                    }
                    if (window.eel._exposed_functions['senderText'] && query) {
                        window.eel._exposed_functions['senderText'](query);
                    }

                    const response = await fetch('/api/allCommands', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({query: query || ""})
                    });
                    const data = await response.json();

                    if (data.success) {
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            window.eel._exposed_functions['DisplayMessage'](data.response);
                        }
                        if (window.eel._exposed_functions['receiverText']) {
                            window.eel._exposed_functions['receiverText'](data.response);
                        }
                        // Delay returning to the idle orb based on reading speed 
                        // (~200 words per minute -> ~300ms per word)
                        let words = (data.response || "").split(/\s+/).length;
                        let delayMs = Math.max(3000, words * 300);
                        
                        setTimeout(() => {
                            if (window.eel._exposed_functions['ShowHood']) {
                                window.eel._exposed_functions['ShowHood']();
                            }
                        }, delayMs);
                        
                        if (callback) callback(data);
                    } else {
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            window.eel._exposed_functions['DisplayMessage']("Error: " + (data.error || "Unknown error"));
                        }
                    }
                } catch(e) {
                    console.error("allCommands error:", e);
                    if (window.eel._exposed_functions['DisplayMessage']) {
                        window.eel._exposed_functions['DisplayMessage']("Connection error. Please try again.");
                    }
                }
            };
        },
        
        // ─── Audio / Sound (not available on web) ───────────────────
        playAssistantSound: function() {
            return function() { /* no audio in web mode */ };
        },
        
        // ─── System Stats ────────────────────────────────────────────
        get_system_stats: function() {
            return async function(callback) {
                try {
                    const res = await fetch('/api/get_system_stats');
                    const data = await res.json();
                    if (callback) callback(data);
                    return data;
                } catch(e) {
                    const mock = {cpu: 0, battery: 100, plugged: true};
                    if (callback) callback(mock);
                    return mock;
                }
            };
        },
        
        // ─── Init: show loader → then auth screen ────────────────────
        init: function() {
            return function() { 
                console.log("Eel init (web mode)");
                window.eel._initDone = true;
            };
        },

        // ─── Auth ────────────────────────────────────────────────────
        password_login: function(pass) {
            return async function(callback) {
                try {
                    const res = await fetch('/api/password_login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({password: pass})
                    });
                    const data = await res.json();
                    if (callback) callback(data);
                } catch(e) {
                    // Fallback: accept any password for demo
                    if (callback) callback({success: true});
                }
            };
        },

        on_auth_success: function() {
            return function() {
                // Trigger hideStart in web mode
                if (window.eel._exposed_functions['hideStart']) {
                    window.eel._exposed_functions['hideStart']();
                }
            };
        },

        face_login: function(dataURL) {
            return function(callback) {
                // Face login not available on web — always return false so 
                // user falls back to password login
                if (callback) callback({success: false, message: "Face login not available on web."});
            };
        },

        // ─── Conversations ───────────────────────────────────────────
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
                if (callback) callback({success: true, conversation_id: Date.now()});
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

        // ─── Desktop-only stubs ──────────────────────────────────────
        set_system_volume:    function() { return function() {}; },
        set_system_brightness: function() { return function() {}; },
        set_voice_rate:       function() { return function() {}; },
        set_voice_gender:     function() { return function() {}; },
        analyze_image:        function() { return function() {}; },

        // ─── Auto-skip to auth screen after scripts load ─────────────
        _startAuthFlow: function() {
            var checkReady = setInterval(function() {
                if (typeof $ !== 'undefined' && window.eel._exposed_functions['hideLoader']) {
                    clearInterval(checkReady);
                    console.log("Scripts ready. Waiting 3 seconds before showing auth screen...");
                    setTimeout(function() {
                        // Show the auth/password screen (hideLoader hides the spinner and shows FaceAuth card)
                        window.eel._exposed_functions['hideLoader']();
                    }, 3000);
                }
            }, 200);

            // Safety: force show auth after 4s no matter what
            setTimeout(function() {
                clearInterval(checkReady);
                // If we still haven't moved past loader, force it
                var loader = document.getElementById('Loader');
                var faceAuth = document.getElementById('FaceAuth');
                if (loader && !loader.hidden) {
                    if (loader) loader.hidden = true;
                    if (faceAuth) faceAuth.hidden = false;
                }
            }, 4000);
        }
    };
    
    // Polyfill expose
    window.eel.expose = function(func, name) {
        window.eel._exposed_functions[name || func.name] = func;
    };

    // Kick off auth flow when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            window.eel._startAuthFlow();
        });
    } else {
        window.eel._startAuthFlow();
    }
}
