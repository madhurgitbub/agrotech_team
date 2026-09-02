let chatLanguage = "English";


function toggleChatbot() {

    const chatbotWindow =
        document.getElementById("chatbotWindow");

    chatbotWindow.classList.toggle("active");

}


function setChatLanguage(language, button) {

    chatLanguage = language;

    document
        .querySelectorAll(".chat-lang-btn")
        .forEach(btn => {

            btn.classList.remove("active");

        });

    button.classList.add("active");


    const input =
        document.getElementById("chatbotInput");

    if (language === "Hindi") {

        input.placeholder =
            "खेती के बारे में पूछें...";

    } else {

        input.placeholder =
            "Ask about farming...";

    }

}


function handleChatKeyPress(event) {

    if (event.key === "Enter") {

        sendChatMessage();

    }

}


function sendSuggestion(button) {

    const message = button.innerText;

    document.getElementById(
        "chatbotInput"
    ).value = message;

    sendChatMessage();

}


async function sendChatMessage() {

    const input =
        document.getElementById("chatbotInput");

    const message = input.value.trim();


    if (!message) return;


    // Add user message

    addMessage(message, "user");


    input.value = "";


    // Show typing

    const typingId =
        showTypingIndicator();


   try {

    const response =
        await fetch(
            "http://127.0.0.1:8000/api/chatbot",
            {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({

                    message: message,

                    language: chatLanguage

                })

            }
        );


    if (!response.ok) {

        throw new Error(
            `Server error: ${response.status}`
        );

    }


    const data =
        await response.json();


    removeTypingIndicator(
        typingId
    );


    if (data.success && data.reply) {

        addMessage(
            data.reply,
            "bot"
        );

    }

    else {

        addMessage(
            "Sorry, I am unable to answer right now. Please try again.",
            "bot"
        );

    }

}
catch (error) {

    console.error(
        "Chatbot Error:",
        error
    );


    removeTypingIndicator(
        typingId
    );


    addMessage(
        "⚠️ Unable to connect to AgroTECH AI. Please try again.",
        "bot"
    );

}

}


function addMessage(
    message,
    sender
) {

    const messagesContainer =
        document.getElementById(
            "chatbotMessages"
        );


    const messageDiv =
        document.createElement("div");


    messageDiv.className =
        `chat-message ${sender}-message`;


    if (sender === "bot") {

        messageDiv.innerHTML = `

            <div class="message-avatar">
                🌾
            </div>

            <div class="message-content">
                ${formatMessage(message)}
            </div>

        `;

    }

    else {

        messageDiv.innerHTML = `

            <div class="message-content">
                ${escapeHTML(message)}
            </div>

        `;

    }


    messagesContainer.appendChild(
        messageDiv
    );


    scrollChatToBottom();

}


function showTypingIndicator() {

    const id =
        "typing-" + Date.now();


    const messagesContainer =
        document.getElementById(
            "chatbotMessages"
        );


    const typingDiv =
        document.createElement("div");


    typingDiv.id = id;


    typingDiv.className =
        "chat-message bot-message";


    typingDiv.innerHTML = `

        <div class="message-avatar">
            🌾
        </div>

        <div class="message-content">

            <div class="chat-typing">

                <span></span>
                <span></span>
                <span></span>

            </div>

        </div>

    `;


    messagesContainer.appendChild(
        typingDiv
    );


    scrollChatToBottom();


    return id;

}


function removeTypingIndicator(id) {

    const element =
        document.getElementById(id);


    if (element) {

        element.remove();

    }

}


function scrollChatToBottom() {

    const messagesContainer =
        document.getElementById(
            "chatbotMessages"
        );


    messagesContainer.scrollTop =
        messagesContainer.scrollHeight;

}


function escapeHTML(text) {

    const div =
        document.createElement("div");


    div.textContent = text;


    return div.innerHTML;

}


function formatMessage(text) {

    let formatted = escapeHTML(text);

    // Headings
    formatted = formatted.replace(
        /^### (.*$)/gim,
        "<h4>$1</h4>"
    );

    formatted = formatted.replace(
        /^## (.*$)/gim,
        "<h3>$1</h3>"
    );

    // Bold text
    formatted = formatted.replace(
        /\*\*(.*?)\*\*/g,
        "<strong>$1</strong>"
    );

    // Bullet points
    formatted = formatted.replace(
        /^- (.*$)/gim,
        "• $1"
    );

    // Line breaks
    formatted = formatted.replace(
        /\n/g,
        "<br>"
    );

    return formatted;

}