const chatInput = document.getElementById('chat-input');
const sendButton = document.getElementById('send-button');
const chatContent = document.getElementById('chat-content');

// Helper to scroll to the bottom of the chat window
function scrollToBottom() {
    chatContent.scrollTop = chatContent.scrollHeight;
}

// Enable/disable send button based on input
chatInput.addEventListener('input', () => {
    sendButton.disabled = chatInput.value.trim() === '';
    adjustTextareaHeight();
});

// Adjust textarea height dynamically
function adjustTextareaHeight() {
    chatInput.style.height = 'auto';
    const newHeight = chatInput.scrollHeight;
    
    if (newHeight <= 150) {
        chatInput.style.height = newHeight + 'px';
    }
}

// *** NEW: Asynchronous function to handle streaming API response ***
// async function sendToFastAPIAndStream(userQuery) {
//     console.log(userQuery);
    
//     const aiBubble = appendMessage("Thinking...", 'ai');
    
//     try {
//         // Function to update the message after a delay
//         const updateStatusWithDelay = (text, delay) => {
//             return new Promise(resolve => setTimeout(() => {
//                 aiBubble.textContent = text;
//                 scrollToBottom();
//                 resolve();
//             }, delay));
//         };

//         // 1. Show "Thinking..."
//         await updateStatusWithDelay("Thinking...", 100); 

//         // 2. Wait and show "More thinking..."
//         await updateStatusWithDelay("More thinking...", 1000); 

//         // 3. Wait and show "Generating answer..."
//         await updateStatusWithDelay("Generating answer...", 1500); 

//         // Start the fetch request after the status messages have run
//         const response = await fetch('/generate_response', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json'
//             },
//             body: JSON.stringify({ message: userQuery })
//         });

//         if (!response.body) {
//             aiBubble.textContent = "Error: Stream not supported or connection failed.";
//             return;
//         }

//         // 4. Stream the real answer
//         aiBubble.textContent = ''; // Clear "Generating answer..." for the streamed response
//         const reader = response.body.getReader();
//         const decoder = new TextDecoder();
        
//         while (true) {
//             const { value, done } = await reader.read();
//             if (done) break;

//             const chunk = decoder.decode(value, { stream: true });
//             aiBubble.textContent += chunk;
//             scrollToBottom();
//         }

//     } catch (error) {
//         console.error('Error during streaming:', error);
//         aiBubble.textContent = `Error: ${error.message}`;
//     }
// }

async function sendToFastAPIAndStream(userQuery) {
    
    // Create an initial message bubble to stream into
    const aiBubble = appendMessage("Thinking...", 'ai');
    
    try {
        // Function to update the message after a delay
        const updateStatusWithDelay = (text, delay) => {
            return new Promise(resolve => setTimeout(() => {
                aiBubble.textContent = text;
                scrollToBottom();
                resolve();
            }, delay));
        };

        // 1. Show "Thinking..."
        await updateStatusWithDelay("Thinking...", 1000); 

        // 2. Wait and show "More thinking..."
        await updateStatusWithDelay("Searching web...", 2000); 

        // 3. Wait and show "Generating answer..."
        await updateStatusWithDelay("Generating answer...", 3000); 

        const response = await fetch('/generate_response', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message: userQuery })
        });

        if (!response.body) {
            aiBubble.textContent = "Error: Stream not supported or connection failed.";
            return;
        }

        // Clear the status message
        aiBubble.textContent = ''; 

        // Get a reader to process the stream
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        
        // This variable will accumulate the streamed chunks
        let fullText = ''; 

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            // Decode the chunk and append it
            const chunk = decoder.decode(value, { stream: true });
            fullText += chunk;
            
            // Format and display the text as it is received
            typeMessage(aiBubble, formatTextForUI(fullText))
            scrollToBottom();
        }

    } catch (error) {
        console.error('Error during streaming:', error);
        aiBubble.textContent = `Error: ${error.message}`;
    }
}


function typeMessage(element, processedText) {
    // Get the plain text (without HTML tags) to measure typing speed,
    // but we'll insert the HTML tags when needed.
    let i = 0;
    const typingSpeed = 25; // Milliseconds per character

    // We use a temporary container to access the characters correctly,
    // while preserving the HTML structure needed for links/breaks.
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = processedText;
    
    // Get the list of nodes (text nodes and anchor tags)
    const nodes = Array.from(tempDiv.childNodes);
    
    // Start the typing animation
    function typeNextCharacter() {
        if (i >= nodes.length) return; // Stop condition

        const currentNode = nodes[i];

        if (currentNode.nodeType === 3) { // Text Node
            // Type one character of the text node
            const text = currentNode.textContent;
            const char = text.charAt(0);
            
            if (char) {
                element.innerHTML += char;
                // Move to the next character in the text node
                currentNode.textContent = text.substring(1);
            } else {
                // Text node is finished, move to the next node/element
                i++;
                typeNextCharacter(); // Immediately call next node
                return;
            }
        } else if (currentNode.nodeType === 1) { // Element Node (like <br> or <a>)
            // Insert the entire element (e.g., an anchor tag or line break) at once
            element.appendChild(currentNode.cloneNode(true));
            i++; // Move to the next node
        }

        // If we are still typing a text node, wait for the typing speed
        if (i < nodes.length) {
            setTimeout(typeNextCharacter, typingSpeed);
        }
    }

    // Start the animation
    typeNextCharacter();
}
/**
 * Replaces newline characters with HTML <br> tags and converts URLs into clickable links.
 * @param {string} text - The raw text content from the API.
 * @returns {string} The formatted HTML string.
 */
function formatTextForUI(text) {
    // 1. Replace newlines with <br> tags
    let processedText = text.replace(/\\n/g, '\n');
    let formattedText = processedText.replace(/\r?\n/g, '<br>'); // Handles both \n and \r\n

    // 2. Convert URLs into clickable links
    // This regex looks for URLs starting with http/https or www.
    const urlRegex = /(https?:\/\/[^\s]+|www\.[^\s]+)/g;
    formattedText = formattedText.replace(urlRegex, function(url) {
        // Ensure the URL has a protocol for the anchor tag to work correctly
        const href = url.startsWith('http') ? url : `http://${url}`;
        return `<a href="${href}" target="_blank">${url}</a>`;
    });

    return formattedText;
}

// Example of what your appendMessage function might look like
function appendMessage(text, sender) {
    const chatbox = document.getElementById('chatbox'); // Assuming you have a chatbox container
    const messageElement = document.createElement('div');
    messageElement.classList.add('message', sender);
    chatbox.appendChild(messageElement);
    return messageElement;
}

// Handle sending message
sendButton.addEventListener('click', () => {
    const messageText = chatInput.value.trim();
    if (messageText) {
        // 1. Append user message
        appendMessage(messageText, 'user');
        
        // 2. Clear input and disable button
        chatInput.value = '';
        sendButton.disabled = true;
        adjustTextareaHeight();
        
        // 3. START REAL STREAMING CALL
        sendToFastAPIAndStream(messageText); 
    }
});

// Allow sending with Enter key
chatInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter' && !event.shiftKey && !sendButton.disabled) {
        event.preventDefault();
        sendButton.click();
    }
});

function appendMessage(text, sender) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message', sender);

    const avatarDiv = document.createElement('div');
    avatarDiv.classList.add('avatar');
    avatarDiv.textContent = sender === 'user' ? 'You' : 'AI';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.classList.add('bubble');
    // bubbleDiv.textContent = text; 
    bubbleDiv.innerHTML = formatTextForUI(text); 

    if (sender === 'user') {
        messageDiv.appendChild(bubbleDiv);
        messageDiv.appendChild(avatarDiv);
    } else {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(bubbleDiv);
    }
    chatContent.appendChild(messageDiv);
    scrollToBottom();
    return bubbleDiv;
}

// Initial height adjustment for textarea on load
window.addEventListener('load', adjustTextareaHeight);

window.onload = () => {
    const outputElement = document.getElementById('initial-message');
    const demoText = "Hello! I'm your CloudWalk assistant. How can I help you today?";

    // Call the function to begin the typing animation
    typeMessage(outputElement, demoText);
};