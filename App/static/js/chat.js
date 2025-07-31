// chat.js

document.addEventListener('DOMContentLoaded', () => {
    const voiceBtn = document.getElementById('voiceBtn');
    const userInput = document.getElementById('user_input');
    const chatForm = document.getElementById('chatForm');

    // Check if the browser supports speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    const recognition = new SpeechRecognition();

    recognition.continuous = true; // Keep recognition active for continuous input
    recognition.interimResults = true; // Show interim results

    recognition.onstart = () => {
        console.log('Voice recognition started. Speak into the microphone.');
    };

    recognition.onresult = (event) => {
        let transcript = '';
        for (let i = event.resultIndex; i < event.results.length; i++) {
            // Check if the result is final
            if (event.results[i].isFinal) {
                transcript += event.results[i][0].transcript;
            } else {
                // Update the input field with interim results
                userInput.value = event.results[i][0].transcript; 
            }
        }

        // Set the final transcript to the input when speaking ends
        userInput.value = transcript;
    };

    recognition.onerror = (event) => {
        console.error('Error occurred in recognition: ' + event.error);
    };

    voiceBtn.addEventListener('click', () => {
        userInput.value = ''; // Clear input field before starting recognition
        recognition.start(); // Start voice recognition on button click
    });

    recognition.onend = () => {
        console.log('Voice recognition ended.');
    };
});



let isSpeaking = false;
let utterance = null;

// Utility function to strip HTML tags
function stripHtml(html) {
    const tempDiv = document.createElement('div');
    tempDiv.innerHTML = html;
    return tempDiv.textContent || tempDiv.innerText || ""; // Return only text content
}

// Function to read or stop bot's response
function toggleReadBotResponse(responseText) {
    const plainText = stripHtml(responseText); // Strip out HTML tags before reading

    if (isSpeaking) {
        // If already speaking, stop the speech
        window.speechSynthesis.cancel();
        isSpeaking = false;
    } else {
        // Create new utterance only if not currently speaking
        utterance = new SpeechSynthesisUtterance(plainText);

        // Set optional properties (rate, pitch, language, etc.)
        utterance.rate = 1;  // Speed of speech (1 is normal)
        utterance.pitch = 1; // Pitch (1 is normal)
        utterance.lang = 'en-US'; // Set language to English (US)

        // Set the flag to true when speaking starts
        utterance.onstart = function() {
            isSpeaking = true;
        };

        // Reset the flag when speaking ends
        utterance.onend = function() {
            isSpeaking = false;
        };

        // Speak the response text
        window.speechSynthesis.speak(utterance);
    }
}

// Function to handle module button click
function handleModuleClick(moduleTitle) {
    window.speechSynthesis.cancel(); // Stop speech when clicking other buttons
    const inputField = document.querySelector('input[name="user_input"]');
    inputField.value = moduleTitle;
    inputField.form.submit();
}

// Function to clear chat and stop speech synthesis
function clearChat() {
    window.speechSynthesis.cancel(); // Stop speech when clicking "Clear Chat"
    const form = document.querySelector('form');
    const clearChatInput = document.createElement('input');
    clearChatInput.type = 'hidden';
    clearChatInput.name = 'clear_chat';
    form.appendChild(clearChatInput);
    form.submit();
}

// Function to start voice recognition
function startVoiceInput() {
    window.speechSynthesis.cancel(); // Stop speech when starting voice input
    const recognition = new (window.SpeechRecognition || window.webkitSpeechRecognition)();
    recognition.lang = 'en-US';
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        const userInput = event.results[0][0].transcript;
        const inputField = document.querySelector('input[name="user_input"]');
        inputField.value = userInput;
        inputField.form.submit();
    };

    recognition.onerror = function(event) {
        console.error("Speech recognition error: ", event.error);
    };

    recognition.start();
}