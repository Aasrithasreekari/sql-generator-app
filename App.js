import React, { useState } from "react";
import axios from "axios";
import "./App.css";

export default function App() {
  const [input, setInput] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);

  const handleUpload = (e) => {
    const files = Array.from(e.target.files);
    const fileNames = files.map((file) => file.name);
    setUploadedFiles((prev) => [...prev, ...fileNames]);
  };

  const handleSend = async () => {
    if (input.trim()) {
      const updatedHistory = [...chatHistory, { sender: "User", message: input }];
      setChatHistory(updatedHistory);
      setInput("");

      try {
        const response = await axios.post(
          "http://127.0.0.1:8000/generate-sql",
          {
            schema_files: uploadedFiles,
            user_prompt: input
          },
          {
            headers: {
              "Content-Type": "application/json"
            }
          }
        );

        const botMessage = response.data.sql_query || "No SQL generated.";
        setChatHistory([
          ...updatedHistory,
          { sender: "Bot", message: botMessage }
        ]);
      } catch (error) {
        console.error("Error:", error);
        setChatHistory([
          ...updatedHistory,
          { sender: "Bot", message: "Failed to fetch SQL query." }
        ]);
      }
    }
  };

  return (
    <div className="container">
      <div className="upload-bar">
        <input type="file" accept=".json" multiple onChange={handleUpload} />
        <div className="uploaded-files">
          <h4>Uploaded Files:</h4>
          <ul>
            {uploadedFiles.map((fileName, idx) => (
              <li key={idx}>{fileName}</li>
            ))}
          </ul>
        </div>
      </div>

      <div className="main">
        <div className="chat-section">
          <div className="chat-history">
            <h3>Response/chat history view</h3>
            <div className="messages">
              {chatHistory.map((msg, idx) => (
                <div key={idx} className="message">
                  {msg.sender === "Bot" ? (
                    <pre className="bot-sql">{msg.message}</pre>
                  ) : (
                    <div><strong>{msg.sender}:</strong> {msg.message}</div>
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="chat-input-area">
            <input
              type="text"
              placeholder="Question/chat input"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleSend()}
            />
            <button onClick={handleSend}>Send</button>
          </div>
        </div>
      </div>
    </div>
  );
}
