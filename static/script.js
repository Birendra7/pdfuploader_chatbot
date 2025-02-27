document.addEventListener("DOMContentLoaded", function () {
    const chatForm = document.getElementById("chat-form");
    const userInput = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    chatForm.addEventListener("submit", async function (e) {
        e.preventDefault();
        const userText = userInput.value.trim();
        if (userText === "") return;

        appendMessage("You", userText);
        userInput.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                body: JSON.stringify({ message: userText }),
                headers: {
                    "Content-Type": "application/json"
                }
            });

            const data = await response.json();
            appendMessage("Bot", data.reply);
        } catch (error) {
            console.error("Error:", error);
            appendMessage("Bot", "Oops! Something went wrong.");
        }
    });

    function appendMessage(sender, message) {
        const messageElement = document.createElement("p");
        messageElement.innerHTML = `<strong>${sender}:</strong> ${message}`;
        chatBox.appendChild(messageElement);
        chatBox.scrollTop = chatBox.scrollHeight;
    }
});
