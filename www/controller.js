$(document).ready(function () {
    let lastUserMessage = "";



    // Display Speak Message
    eel.expose(DisplayMessage)
    function DisplayMessage(message) {
        // Direct text update works best for dynamically changing text 
        // without breaking the DOM structure needed for the wave.
        $("#SiriWave .siri-message").text(message);
    }

    // Display hood
    eel.expose(ShowHood)
    function ShowHood() {
        $("#Oval").attr("hidden", false);
        $("#SiriWave").attr("hidden", true);
    }

    window.current_conversation_id = null;

    window.loadConversations = function() {
        eel.get_conversations()(function(response) {
            if (response && response.success) {
                let listContainer = document.getElementById("conversations-list");
                listContainer.innerHTML = "";
                
                response.data.forEach(function(conv) {
                    let isActive = (conv.id === current_conversation_id) ? "active bg-secondary" : "text-light";
                    let title = conv.title;
                    if (title.length > 25) title = title.substring(0, 25) + "...";
                    
                    listContainer.innerHTML += `
                        <button class="list-group-item list-group-item-action ${isActive} border-0 bg-transparent" onclick="loadMessages(${conv.id})">
                            <i class="bi bi-chat-left-text me-2"></i> ${title}
                        </button>
                    `;
                });
            }
        });
    }

    window.loadMessages = function(conv_id, show_canvas = true) {
        current_conversation_id = conv_id;
        window.loadConversations(); // refresh active state
        
        // Hide conversations sidebar and open chat canvas
        let convElement = document.getElementById('offcanvasConversations');
        let convOffcanvas = bootstrap.Offcanvas.getInstance(convElement);
        if (convOffcanvas && show_canvas) convOffcanvas.hide();
        
        if (show_canvas) {
            let chatElement = document.getElementById('offcanvasScrolling');
            let chatOffcanvas = bootstrap.Offcanvas.getInstance(chatElement);
            if (!chatOffcanvas) chatOffcanvas = new bootstrap.Offcanvas(chatElement);
            chatOffcanvas.show();
        }
        
        eel.get_messages(conv_id)(function(response) {
            if (response && response.success) {
                var chatBox = document.getElementById("chat-canvas-body");
                chatBox.innerHTML = ""; 
                
                response.data.forEach(function(chat) {
                    if (chat.user_message) {
                        chatBox.innerHTML += `<div class="row justify-content-end mb-4">
                            <div class="width-size">
                            <div class="sender_message">${chat.user_message}</div>
                        </div></div>`;
                    }
                    if (chat.bot_response) {
                        chatBox.innerHTML += `<div class="row justify-content-start mb-4">
                            <div class="width-size">
                            <div class="receiver_message">${chat.bot_response}</div>
                        </div></div>`;
                    }
                });
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        });
    }

    let newChatBtn = document.getElementById("newChatBtn");
    if (newChatBtn) {
        newChatBtn.addEventListener("click", function() {
            current_conversation_id = null;
            document.getElementById("chat-canvas-body").innerHTML = "";
            window.loadConversations();
            
            // Hide conversations sidebar and open chat canvas
            let convElement = document.getElementById('offcanvasConversations');
            let convOffcanvas = bootstrap.Offcanvas.getInstance(convElement);
            if (convOffcanvas) convOffcanvas.hide();
            
            let chatElement = document.getElementById('offcanvasScrolling');
            let chatOffcanvas = bootstrap.Offcanvas.getInstance(chatElement);
            if (!chatOffcanvas) chatOffcanvas = new bootstrap.Offcanvas(chatElement);
            chatOffcanvas.show();
        });
    }

    eel.expose(senderText)
    function senderText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            lastUserMessage = message;
            chatBox.innerHTML += `<div class="row justify-content-end mb-4">
            <div class = "width-size">
            <div class="sender_message">${message}</div>
        </div></div>`; 
    
            chatBox.scrollTop = chatBox.scrollHeight;
        }
    }

    eel.expose(receiverText)
    function receiverText(message) {
        var chatBox = document.getElementById("chat-canvas-body");
        if (message.trim() !== "") {
            chatBox.innerHTML += `<div class="row justify-content-start mb-4">
            <div class = "width-size">
            <div class="receiver_message">${message}</div>
            </div>
        </div>`; 
    
            chatBox.scrollTop = chatBox.scrollHeight;
            
            // Save logic
            if (current_conversation_id === null) {
                // Create a new conversation using the first 5-7 words of user message
                let titleParts = lastUserMessage.split(" ").slice(0, 6);
                let title = titleParts.join(" ");
                if (title.trim() === "") title = "New Chat";
                else title += "...";
                
                eel.create_conversation(title)(function(res) {
                    if (res && res.success) {
                        current_conversation_id = res.conversation_id;
                        eel.save_message(current_conversation_id, lastUserMessage, message)();
                        lastUserMessage = "";
                        window.loadConversations();
                    }
                });
            } else {
                eel.save_message(current_conversation_id, lastUserMessage, message)();
                lastUserMessage = "";
            }
        }
    }

    // Hide Loader and display Face Auth animation
    eel.expose(hideLoader)
    function hideLoader() {
        $("#Loader").attr("hidden", true);
        $("#FaceAuth").attr("hidden", false);
    }
    // Hide Face auth and display Face Auth success animation
    eel.expose(hideFaceAuth)
    function hideFaceAuth() {
        $("#FaceAuth").attr("hidden", true);
        $("#FaceAuthSuccess").attr("hidden", false);
    }
    // Hide success and display 
    eel.expose(hideFaceAuthSuccess)
    function hideFaceAuthSuccess() {
        $("#FaceAuthSuccess").attr("hidden", true);
        $("#HelloGreet").attr("hidden", false);
    }

    // Hide Start Page and display blob
    eel.expose(hideStart)
    function hideStart() {
        $("#Start").attr("hidden", true);
        
        // Load conversations once authenticated
        window.loadConversations();
        
        // Optionally load the most recent conversation if it exists
        eel.get_conversations()(function(response) {
            if (response && response.success && response.data.length > 0) {
                window.loadMessages(response.data[0].id, false);
            }
        });

        setTimeout(function () {
            $("#Oval").addClass("animate__animated animate__zoomIn");

        }, 1000)
        setTimeout(function () {
            $("#Oval").attr("hidden", false);
        }, 1000)
    }


});