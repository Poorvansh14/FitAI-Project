async function sendToAI() {
  const instruction = document.getElementById("instruction").value;
  const input = document.getElementById("input").value;
  const responseBox = document.getElementById("responseBox");

  responseBox.textContent = "⏳ Thinking...";

  try {
    const res = await fetch("http://127.0.0.1:5000/ask", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ instruction, input })
    });

    const data = await res.json();

    if (data.response) {
      responseBox.textContent = data.response;
    } else {
      responseBox.textContent = "❌ Error: " + (data.error || "Unknown error");
    }
  } catch (error) {
    responseBox.textContent = "⚠️ Failed to connect to backend.";
    console.error(error);
  }
}
