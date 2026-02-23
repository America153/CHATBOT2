// script.js

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const messages = document.getElementById("chat-messages");

    // Function to append a message to the chat
    function appendMessage(sender, text) {
        const msg = document.createElement("div");
        msg.className = `message ${sender}`;
        msg.textContent = `${sender}: ${text}`;
        messages.appendChild(msg);
        messages.scrollTop = messages.scrollHeight;
    }

    // Handle form submission
    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        const userMessage = input.value.trim();
        if (!userMessage) return;

        appendMessage("User", userMessage);
        input.value = "";

        try {
            const response = await fetch("/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message: userMessage }),
            });

            const data = await response.json();
            appendMessage("Bot", data.reply || "No reply received.");
        } catch (err) {
            appendMessage("Bot", "Error: Could not reach server.");
            console.error(err);
        }
    });
});