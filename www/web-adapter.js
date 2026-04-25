// Web adapter to bridge Eel calls to Flask API when running on web
if (typeof eel === 'undefined') {
    console.log("Running in web mode. Adapter initialized.");
    
    window.eel = {
        _exposed_functions: {},
        _initDone: false,
        
        expose: function(func, name) {
            this._exposed_functions[name || func.name] = func;
        },
        
        // ─── Voice Pre-loading ───────────────────────────────────────
        _synthVoices: [],
        
        // ─── AI Chat ────────────────────────────────────────────────
        allCommands: function(message) {
            return async function(callback) {
                let query = message;
                
                // If message is empty or 1 (default from python), trigger microphone
                if (!query || query === 1) {
                    if (window.location.protocol !== 'https:' && window.location.hostname !== 'localhost' && window.location.hostname !== '127.0.0.1') {
                        console.error("Microphone access requires HTTPS.");
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            window.eel._exposed_functions['DisplayMessage']("Microphone requires HTTPS.");
                            setTimeout(() => { if (window.eel._exposed_functions['ShowHood']) window.eel._exposed_functions['ShowHood'](); }, 3000);
                        }
                        return;
                    }
                    
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    if (!SpeechRecognition) {
                        console.error("Speech Recognition API not supported in this browser.");
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            window.eel._exposed_functions['DisplayMessage']("Speech Recognition not supported in this browser.");
                            setTimeout(() => { if (window.eel._exposed_functions['ShowHood']) window.eel._exposed_functions['ShowHood'](); }, 3000);
                        }
                        return;
                    }
                    
                    try {
                        const recognition = new SpeechRecognition();
                        recognition.lang = 'en-US';
                        recognition.interimResults = false;
                        recognition.maxAlternatives = 1;
                        
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            window.eel._exposed_functions['DisplayMessage']("Listening...");
                        }
                        
                        console.log("Starting speech recognition...");
                        let recognizedText = await new Promise((resolve, reject) => {
                            recognition.onresult = (event) => resolve(event.results[0][0].transcript);
                            recognition.onerror = (event) => reject(event.error);
                            recognition.onnomatch = () => reject('no-match');
                            recognition.start();
                        });
                        
                        console.log("Recognized:", recognizedText);
                        query = recognizedText;
                    } catch (err) {
                        console.error("Microphone error:", err);
                        if (window.eel._exposed_functions['DisplayMessage']) {
                            let errMsg = err === 'not-allowed' ? "Microphone permission denied." : "Could not hear you. Please try again.";
                            window.eel._exposed_functions['DisplayMessage'](errMsg);
                            setTimeout(() => { if (window.eel._exposed_functions['ShowHood']) window.eel._exposed_functions['ShowHood'](); }, 3000);
                        }
                        return;
                    }
                }

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
                        
                        // Web Speech API for TTS (Text-to-Speech)
                        if ('speechSynthesis' in window) {
                            // Ensure voices are loaded
                            if (window.eel._synthVoices.length === 0) {
                                window.eel._synthVoices = window.speechSynthesis.getVoices();
                            }
                            
                            const utterance = new SpeechSynthesisUtterance(data.response);
                            utterance.lang = 'en-US';
                            
                            // Calculate a fallback delay just in case speech fails to fire
                            let words = (data.response || "").split(/\s+/).length;
                            let delayMs = Math.max(3000, words * 300);
                            let fallbackTimer = setTimeout(() => {
                                if (window.eel._exposed_functions['ShowHood']) window.eel._exposed_functions['ShowHood']();
                            }, delayMs + 2000);
                            
                            utterance.onend = function() {
                                clearTimeout(fallbackTimer);
                                if (window.eel._exposed_functions['ShowHood']) window.eel._exposed_functions['ShowHood']();
                            };
                            
                            utterance.onerror = function(e) {
                                console.error("Speech synthesis error", e);
                            };
                            
                            window.speechSynthesis.speak(utterance);
                        } else {
                            // Fallback to time-based delay if TTS not supported
                            let words = (data.response || "").split(/\s+/).length;
                            let delayMs = Math.max(3000, words * 300);
                            setTimeout(() => {
                                if (window.eel._exposed_functions['ShowHood']) {
                                    window.eel._exposed_functions['ShowHood']();
                                }
                            }, delayMs);
                        }
                        
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

        password_login: function(pass) {
            return async function(callback) {
                try {
                    const res = await fetch('/api/password_login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({password: pass})
                    });
                    const data = await res.json();
                    if ('speechSynthesis' in window && data.message) {
                        window.speechSynthesis.speak(new SpeechSynthesisUtterance(data.message));
                    } else if ('speechSynthesis' in window && data.success) {
                        window.speechSynthesis.speak(new SpeechSynthesisUtterance("Login successful"));
                    }
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
            return async function(callback) {
                try {
                    const res = await fetch('/api/face_login', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({image: dataURL})
                    });
                    const data = await res.json();
                    if ('speechSynthesis' in window && data.message) {
                        window.speechSynthesis.speak(new SpeechSynthesisUtterance(data.message));
                    }
                    if (callback) callback(data);
                } catch(e) {
                    if ('speechSynthesis' in window) {
                        window.speechSynthesis.speak(new SpeechSynthesisUtterance("Face login not available."));
                    }
                    if (callback) callback({success: false, message: "Face login not available or error occurred."});
                }
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
                    
                    var startBtn = document.getElementById('WebStartBtn');
                    var wishMsg = document.getElementById('WishMessage');
                    var loader = document.getElementById('Loader');
                    
                    if (startBtn && wishMsg && loader) {
                        wishMsg.hidden = true;
                        loader.hidden = true;
                        startBtn.style.display = 'block';
                        
                        startBtn.addEventListener('click', function() {
                            startBtn.style.display = 'none';
                            wishMsg.hidden = false;
                            loader.hidden = false;
                            
                            // Speak initial greeting to unlock audio context
                            if ('speechSynthesis' in window) {
                                const initSpeech = new SpeechSynthesisUtterance("Initializing System.");
                                window.speechSynthesis.speak(initSpeech);
                            }
                            
                            setTimeout(function() {
                                window.eel._exposed_functions['hideLoader']();
                                if ('speechSynthesis' in window) {
                                    const authSpeech = new SpeechSynthesisUtterance("Authentication Required.");
                                    window.speechSynthesis.speak(authSpeech);
                                }
                            }, 6000);
                        });
                    } else {
                        // Fallback if elements not found
                        setTimeout(function() {
                            window.eel._exposed_functions['hideLoader']();
                        }, 6000);
                    }
                }
            }, 200);
        }
    };
    
    // Inject the mock eel into the global scope
    window.eel = Object.assign(window.eel, window.eel._exposed_functions);
    
    // Attempt to preload voices
    if ('speechSynthesis' in window) {
        window.eel._synthVoices = window.speechSynthesis.getVoices();
        if (window.speechSynthesis.onvoiceschanged !== undefined) {
            window.speechSynthesis.onvoiceschanged = function() {
                window.eel._synthVoices = window.speechSynthesis.getVoices();
            };
        }
    }
    
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
