$(document).ready(function () {

    eel.init()()

    try {
        $('.text').textillate({
            loop: true,
            sync: true,
            in: {
                effect: "bounceIn",
            },
            out: {
                effect: "bounceOut",
            },
        });
    } catch(e) { console.warn('textillate not available:', e); }

    // Siri configuration
    var siriWave = new SiriWave({
        container: document.getElementById("siri-container"),
        width: 800,
        height: 200,
        style: "ios9",
        amplitude: "1",
        speed: "0.30",
        autostart: true
      });

    // Siri message animation
    try {
        $('.siri-message').textillate({
            loop: true,
            sync: true,
            in: {
                effect: "fadeInUp",
                sync: true,
            },
            out: {
                effect: "fadeOutUp",
                sync: true,
            },
        });
    } catch(e) { console.warn('textillate siri-message not available:', e); }

    function openChatBox() {
        try {
            let chatElement = document.getElementById('offcanvasScrolling');
            if (chatElement) {
                let chatOffcanvas = bootstrap.Offcanvas.getInstance(chatElement);
                if (!chatOffcanvas) chatOffcanvas = new bootstrap.Offcanvas(chatElement);
                chatOffcanvas.show();
            }
        } catch(e) {}
    }

    // mic button click event

    $("#MicBtn").click(function () { 
        eel.playAssistantSound()
        $("#Oval").attr("hidden", true);
        $("#SiriWave").attr("hidden", false);
        eel.allCommands()()
    });


    function doc_keyUp(e) {
        // this would test for whichever key is 40 (down arrow) and the ctrl key at the same time

        if (e.key === 'j' && e.metaKey) {
            eel.playAssistantSound()
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            eel.allCommands()()
        }
    }
    document.addEventListener('keyup', doc_keyUp, false);

    // to play assistant 
    function PlayAssistant(message) {

        if (message != "") {
            // Show the SiriWave while processing
            $("#Oval").attr("hidden", true);
            $("#SiriWave").attr("hidden", false);
            
            // FIX: must call allCommands(message)() — the second () invokes the async fetch
            eel.allCommands(message)()
            $("#chatbox").val("")
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }

    }

    // toogle fucntion to hide and display mic and send button 
    function ShowHideButton(message) {
        if (message.length == 0) {
            $("#MicBtn").attr('hidden', false);
            $("#SendBtn").attr('hidden', true);
        }
        else {
            $("#MicBtn").attr('hidden', true);
            $("#SendBtn").attr('hidden', false);
        }
    }

    // key up event handler on text box
    $("#chatbox").keyup(function () {

        let message = $("#chatbox").val();
        ShowHideButton(message)
    
    });
    
    // send button event handler
    $("#SendBtn").click(function () {
    
        let message = $("#chatbox").val()
        PlayAssistant(message)
    
    });
    

    // enter press event handler on chat box
    $("#chatbox").keypress(function (e) {
        key = e.which;
        if (key == 13) {
            let message = $("#chatbox").val()
            PlayAssistant(message)
        }
    });

    // Settings controls bindings
    $("#volumeSlider").on("input", function() {
        let val = $(this).val();
        $("#volumeLabel").text(val + "%");
        eel.set_system_volume(val);
    });

    $("#brightnessSlider").on("input", function() {
        let val = $(this).val();
        $("#brightnessLabel").text(val + "%");
        eel.set_system_brightness(val);
    });

    $("#speechRateSlider").on("input", function() {
        let val = $(this).val();
        $("#speechRateLabel").text(val);
        eel.set_voice_rate(val);
    });

    $("#voiceGenderSelect").change(function() {
        let val = $(this).val();
        eel.set_voice_gender(val);
    });

    $("#saveSettingsBtn").click(function() {
        // Optional: Save names to backend if needed later, for now we close and alert
        // A placeholder for saving the assistant/user name
        // let userName = $("#userName").val();
        // let jarvisName = $("#jarvisName").val();
        // eel.update_profile(userName, jarvisName);
    });

    // Dark/Light Theme Toggle
    $("#themeToggleBtn").click(function() {
        $("body").toggleClass("light-mode");
        let isLight = $("body").hasClass("light-mode");
        
        // toggle icon
        if (isLight) {
            $(this).html('<i class="bi bi-brightness-high-fill"></i>');
        } else {
            $(this).html('<i class="bi bi-moon-stars"></i>');
        }
    });

    // Start Live System HUD Logic
    function updateHUDClock() {
        const now = new Date();
        let timeEl = document.getElementById('hud-time');
        let dateEl = document.getElementById('hud-date');
        if (timeEl) timeEl.innerText = now.toLocaleTimeString('en-US', { hour12: false });
        const options = { weekday: 'short', year: 'numeric', month: 'short', day: 'numeric' };
        if (dateEl) dateEl.innerText = now.toLocaleDateString('en-US', options);
    }
    
    // Call telemetry via eel
    async function updateTelemetry() {
        try {
            let stats = await eel.get_system_stats()();
            
            // Update CPU
            $('#hud-cpu-bar').css('width', stats.cpu + '%');
            $('#hud-cpu-text').text(stats.cpu.toFixed(0) + '%');
            
            // Update Battery
            $('#hud-battery-bar').css('width', stats.battery + '%');
            $('#hud-battery-text').text(stats.battery.toFixed(0) + '%');
            
            if(stats.plugged) {
                $('#hud-battery-icon').removeClass('bi-battery-half').addClass('bi-battery-charging');
            } else {
                $('#hud-battery-icon').removeClass('bi-battery-charging').addClass('bi-battery-half');
            }
        } catch(e) {
            console.error(e);
        }
    }

    // Unhide HUD gracefully (only after python connects properly or directly)
    setTimeout(() => {
        $("#system-hud").fadeIn('slow');
    }, 2000);

    // Loops
    setInterval(updateHUDClock, 1000);
    setInterval(updateTelemetry, 5000);
    updateHUDClock();
    // Handle Media Upload
    $("#UploadBtn").click(function () {
        $("#mediaUpload").click();
    });

    $("#mediaUpload").change(function () {
        const file = this.files[0];
        if (file) {
            const reader = new FileReader();
            reader.onload = function(e) {
                const base64data = e.target.result;
                
                // Determine how to display it in the chat
                let mediaPreview = "";
                if (file.type.startsWith('image/')) {
                    mediaPreview = `<img src="${base64data}" alt="Uploaded Image" style="max-width: 200px; max-height: 200px; border-radius: 10px; margin-bottom: 5px; display: block;">`;
                } else if (file.type === 'application/pdf') {
                    mediaPreview = `<div style="font-size: 30px;"><i class="bi bi-file-earmark-pdf text-danger"></i></div>`;
                }
                
                // Add message to chat box
                $("#chat-canvas-body").append(`<div class="row justify-content-end mb-4">
                    <div class="width-size">
                    <div class="sender_message">
                        ${mediaPreview}
                        <strong>${file.name}</strong>
                    </div>
                </div></div>`);
                
                // Switch to SiriWave to show the display message
                $("#Oval").attr("hidden", true);
                $("#SiriWave").attr("hidden", false);
                
                // Send to backend
                eel.analyze_image(base64data)();
            };
            reader.readAsDataURL(file);
        }
    });

    // --- Authentication Logic ---
    let stream = null;
    let authTimeout = null;
    let isCapturing = false;

    // Show/Hide Password
    $("#togglePasswordBtn").click(function() {
        const passInput = $("#passwordInput");
        if (passInput.attr("type") === "password") {
            passInput.attr("type", "text");
            $(this).html('<i class="bi bi-eye-slash"></i>');
        } else {
            passInput.attr("type", "password");
            $(this).html('<i class="bi bi-eye"></i>');
        }
    });

    // Password Login Flow
    $("#PasswordLoginBtn").click(function() {
        let password = $("#passwordInput").val();
        if(!password) {
            $("#AuthError").text("Please enter a password").attr("hidden", false);
            return;
        }
        
        eel.password_login(password)(function(response) {
            if(response.success) {
                $("#AuthError").attr("hidden", true);
                stopCamera();
                eel.on_auth_success()(); // Trigger python success flow
            } else {
                $("#AuthError").text(response.message).attr("hidden", false);
            }
        });
    });

    // Face Login Flow
    function captureAndSendFrame() {
        if (!isCapturing) return;
        const video = document.getElementById('CameraPreview');
        const canvas = document.createElement('canvas');
        canvas.width = video.videoWidth || 320;
        canvas.height = video.videoHeight || 240;
        canvas.getContext('2d').drawImage(video, 0, 0);
        const dataURL = canvas.toDataURL('image/jpeg');
        
        eel.face_login(dataURL)(function(response) {
            if (response.success) {
                isCapturing = false;
                clearTimeout(authTimeout);
                stopCamera();
                $("#AuthError").attr("hidden", true);
                eel.on_auth_success()();
            } else {
                if (isCapturing) {
                    setTimeout(captureAndSendFrame, 500); // retry every 500ms
                }
            }
        });
    }

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
    }

    $("#FaceLoginBtn").click(async function() {
        try {
            $("#AuthError").attr("hidden", true);
            $("#FaceLoginBtn").attr("hidden", true);
            $("#CameraPreviewContainer").attr("hidden", false);
            
            stream = await navigator.mediaDevices.getUserMedia({ video: true });
            const video = document.getElementById('CameraPreview');
            video.srcObject = stream;
            
            isCapturing = true;
            video.onplay = function() {
                setTimeout(captureAndSendFrame, 1000); // Give camera time to adjust light
            };

            // Timeout after 15 seconds
            authTimeout = setTimeout(() => {
                isCapturing = false;
                stopCamera();
                $("#AuthError").text("Face not recognized. Try again or use password.").attr("hidden", false);
                $("#FaceLoginBtn").attr("hidden", false);
                $("#CameraPreviewContainer").attr("hidden", true);
            }, 15000);
            
        } catch (err) {
            $("#AuthError").text("Camera access denied or unavailable.").attr("hidden", false);
            $("#FaceLoginBtn").attr("hidden", false);
            $("#CameraPreviewContainer").attr("hidden", true);
        }
    });

    // Clear Current Chat / Conversation
    $("#clearChatBtn").click(function() {
        if (window.current_conversation_id === null) {
            document.getElementById("chat-canvas-body").innerHTML = "";
            return;
        }
        if (confirm("Are you sure you want to delete this conversation?")) {
            eel.delete_conversation(window.current_conversation_id)(function(response) {
                if (response.success) {
                    window.current_conversation_id = null;
                    document.getElementById("chat-canvas-body").innerHTML = `<div class="text-center text-secondary small my-3">Conversation deleted</div>`;
                    if (typeof window.loadConversations === "function") {
                        window.loadConversations();
                    }
                } else {
                    alert("Failed to delete conversation: " + response.error);
                }
            });
        }
    });

});