import { useEffect, useRef, useState } from "react";
import axios from "axios";

export default function App() {
  const [municipality, setMunicipality] = useState("सुर्योदय नगरपालिका");
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({
      behavior: "smooth",
    });
  }, [chat]);

  const askAI = async () => {
    if (!question.trim()) return;

    const userMsg = {
      role: "user",
      text: question,
    };

    setChat((prev) => [...prev, userMsg]);
    setLoading(true);

    try {
      const res = await axios.post(
        "http://127.0.0.1:8000/chat/",
        {
          municipality,
          question,
        }
      );

      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text: res.data.answer,
        },
      ]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text:
            "❌ Unable to connect to Municipality AI Server",
        },
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  return (
    <div style={styles.page}>
      {/* HEADER */}

      <div style={styles.header}>
        <div>
          <h1 style={styles.title}>
            🏛️ Municipality AI Assistant
          </h1>

          <p style={styles.subtitle}>
            Nepal Local Government Information System
          </p>
        </div>

        <div style={styles.badge}>
          AI Powered
        </div>
      </div>

      {/* DASHBOARD CARDS */}

      <div style={styles.cards}>
        <div style={styles.card}>
          <div style={styles.cardIcon}>👨‍💼</div>
          <div>
            <div style={styles.cardTitle}>
              Mayor Information
            </div>
            <div style={styles.cardText}>
              Contact details & leadership
            </div>
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>📞</div>
          <div>
            <div style={styles.cardTitle}>
              Municipality Contacts
            </div>
            <div style={styles.cardText}>
              Official phone & email
            </div>
          </div>
        </div>

        <div style={styles.card}>
          <div style={styles.cardIcon}>🌐</div>
          <div>
            <div style={styles.cardTitle}>
              Government Services
            </div>
            <div style={styles.cardText}>
              Websites & information
            </div>
          </div>
        </div>
      </div>

      {/* CHAT AREA */}

      <div style={styles.chatContainer}>
        <div style={styles.chatHeader}>
          💬 Municipality Chat Assistant
        </div>

        <div style={styles.chatBox}>
          {chat.length === 0 && (
            <div style={styles.welcome}>
              <h2>
                Welcome to Municipality AI
              </h2>

              <p>
                Ask about mayors, deputy mayors,
                municipality contacts, websites,
                districts and official information.
              </p>

              <div style={styles.examples}>
                <div style={styles.exampleCard}>
                  Who is the mayor?
                </div>

                <div style={styles.exampleCard}>
                  Give municipality contact
                </div>

                <div style={styles.exampleCard}>
                  What is the official website?
                </div>
              </div>
            </div>
          )}

          {chat.map((msg, index) => (
            <div
              key={index}
              style={{
                display: "flex",
                justifyContent:
                  msg.role === "user"
                    ? "flex-end"
                    : "flex-start",
              }}
            >
              <div
                style={{
                  ...styles.message,

                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg,#2563eb,#0891b2)"
                      : "#ffffff",

                  color:
                    msg.role === "user"
                      ? "#fff"
                      : "#111827",
                }}
              >
                {msg.text}
              </div>
            </div>
          ))}

          {loading && (
            <div style={styles.typing}>
              🤖 AI is generating response...
            </div>
          )}

          <div ref={chatEndRef} />
        </div>
      </div>

      {/* INPUT SECTION */}

      <div style={styles.inputContainer}>
        <input
          value={municipality}
          onChange={(e) =>
            setMunicipality(e.target.value)
          }
          placeholder="Municipality Name"
          style={styles.municipalityInput}
        />

        <div style={styles.inputRow}>
          <input
            value={question}
            onChange={(e) =>
              setQuestion(e.target.value)
            }
            onKeyDown={(e) =>
              e.key === "Enter" && askAI()
            }
            placeholder="Ask anything about municipality..."
            style={styles.questionInput}
          />

          <button
            onClick={askAI}
            disabled={loading}
            style={styles.button}
          >
            {loading ? "..." : "Send"}
          </button>
        </div>
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    padding: "20px",
    fontFamily: "Segoe UI, sans-serif",

    background:
      "linear-gradient(135deg,#0f172a 0%,#0b4f6c 45%,#0f766e 100%)",
  },

  header: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",

    background: "rgba(255,255,255,0.12)",
    backdropFilter: "blur(15px)",

    border: "1px solid rgba(255,255,255,0.15)",

    borderRadius: "22px",
    padding: "25px",

    color: "white",

    boxShadow:
      "0 8px 32px rgba(0,0,0,0.2)",
  },

  title: {
    margin: 0,
    fontSize: "30px",
    fontWeight: "700",
  },

  subtitle: {
    marginTop: "6px",
    color: "#dbeafe",
  },

  badge: {
    background:
      "linear-gradient(135deg,#10b981,#06b6d4)",

    color: "white",

    padding: "10px 18px",

    borderRadius: "999px",

    fontWeight: "bold",
  },

  cards: {
    marginTop: "20px",

    display: "grid",

    gridTemplateColumns:
      "repeat(auto-fit,minmax(250px,1fr))",

    gap: "15px",
  },

  card: {
    background: "rgba(255,255,255,0.12)",

    backdropFilter: "blur(15px)",

    border: "1px solid rgba(255,255,255,0.15)",

    borderRadius: "18px",

    padding: "20px",

    color: "white",

    display: "flex",

    gap: "15px",

    alignItems: "center",
  },

  cardIcon: {
    fontSize: "32px",
  },

  cardTitle: {
    fontWeight: "bold",
  },

  cardText: {
    color: "#cbd5e1",
    fontSize: "13px",
  },

  chatContainer: {
    marginTop: "20px",

    background: "rgba(255,255,255,0.12)",

    backdropFilter: "blur(20px)",

    border: "1px solid rgba(255,255,255,0.15)",

    borderRadius: "22px",

    overflow: "hidden",

    boxShadow:
      "0 8px 32px rgba(0,0,0,0.2)",
  },

  chatHeader: {
    padding: "15px 20px",

    background:
      "linear-gradient(135deg,#2563eb,#059669)",

    color: "white",

    fontWeight: "bold",
  },

  chatBox: {
    height: "450px",

    overflowY: "auto",

    padding: "20px",

    display: "flex",

    flexDirection: "column",

    gap: "12px",
  },

  welcome: {
    textAlign: "center",

    color: "white",

    marginTop: "80px",
  },

  examples: {
    display: "flex",

    justifyContent: "center",

    flexWrap: "wrap",

    gap: "10px",

    marginTop: "25px",
  },

  exampleCard: {
    background: "rgba(255,255,255,0.15)",

    padding: "12px 18px",

    borderRadius: "12px",

    color: "white",
  },

  message: {
    maxWidth: "75%",

    padding: "14px 18px",

    borderRadius: "18px",

    lineHeight: "1.6",

    boxShadow:
      "0 6px 20px rgba(0,0,0,0.08)",
  },

  typing: {
    color: "white",

    fontSize: "14px",
  },

  inputContainer: {
    marginTop: "20px",

    background: "rgba(255,255,255,0.12)",

    backdropFilter: "blur(15px)",

    border: "1px solid rgba(255,255,255,0.15)",

    borderRadius: "22px",

    padding: "20px",
  },

  municipalityInput: {
    width: "100%",

    padding: "14px",

    borderRadius: "12px",

    border: "none",

    marginBottom: "12px",

    fontSize: "15px",

    outline: "none",
  },

  inputRow: {
    display: "flex",

    gap: "10px",
  },

  questionInput: {
    flex: 1,

    padding: "14px",

    borderRadius: "12px",

    border: "none",

    outline: "none",

    fontSize: "15px",
  },

  button: {
    padding: "14px 28px",

    borderRadius: "12px",

    border: "none",

    fontWeight: "bold",

    color: "white",

    background:
      "linear-gradient(135deg,#2563eb,#06b6d4,#059669)",

    cursor: "pointer",

    boxShadow:
      "0 8px 25px rgba(37,99,235,0.35)",
  },
};