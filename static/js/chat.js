document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('chat-form');
    const input = document.getElementById('chat-input');
    const messagContainer = document.getElementById('messages');

    form.addEventListener('submit', async function(event) {
        event.preventDefault();
        const messageText = input.value.trim();
        
        if (messageText) {
            // const messageElement = document.createElement('p');
            // messageElement.textContent = messageText;
            // messagContainer.appendChild(messageElement);
            // input.value = '';
            try {
                const response = await fetch('/analyze', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ message: messageText })
                });

                if (response.ok) {
                    const data = await response.json();
                    
                    // Display the original input text
                    const userMessageElement = document.createElement('p');
                    userMessageElement.textContent = "You entered: " + messageText;
                    userMessageElement.style.fontWeight = 'bold';
                    messagContainer.appendChild(userMessageElement);

                    // Display the response
                    const messageElement = document.createElement('p');
                    messageElement.textContent = data.response;
                    messagContainer.appendChild(messageElement);

                    // Display the analysis result
                    const analysisElement = document.createElement('p');
                    analysisElement.textContent = "Analysis: " + data.analysis; 
                    analysisElement.style.fontStyle = 'italic';
                    messagContainer.appendChild(analysisElement);
                } else {
                    console.error('Error:', response.statusText);
                }
            }
            catch (error) {
                console.error('Error:', error);
            }
            input.value = '';
        };
    });

});