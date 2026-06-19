import { useState, useRef, useEffect } from "react";
import axios from "axios";

export default function App() {
  const [municipality, setMunicipality] = useState("");
  const [question, setQuestion] = useState("");
  const [chat, setChat] = useState([]);
  const [loading, setLoading] = useState(false);
  const [downloadLimit, setDownloadLimit] = useState(20);

  // 🆕 SCRAPER STATES
  const [scrapeUrl, setScrapeUrl] = useState("");
  const [scrapeLoading, setScrapeLoading] = useState(false);

  // 🆕 MUNICIPALITIES FETCH
  const [municipalities, setMunicipalities] = useState([]);
  const [munLoading, setMunLoading] = useState(true);
  const [munError, setMunError] = useState(null);

  const chatEndRef = useRef(null);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chat]);

  // Fetch municipalities on mount
  useEffect(() => {
    let mounted = true;
    const fetchMunicipalities = async () => {
      setMunLoading(true);
      setMunError(null);
      try {
        const res = await axios.get("http://127.0.0.1:8000/municipalities");
        if (!mounted) return;
        const list = Array.isArray(res.data) ? res.data : [];
        // sort alphabetically using Nepali locale if available
        const sorted = [...list].sort((a, b) => a.localeCompare(b, "ne"));
        setMunicipalities(sorted);
        // set default selected municipality if none selected
        if (sorted.length > 0 && !municipality) {
          setMunicipality(sorted[0]);
          setChat((prev) => [
            ...prev,
            { role: "ai", text: `🔎 Selected: ${sorted[0]}` },
          ]);
        }
      } catch (err) {
        setMunError("Failed to load municipalities");
      } finally {
        if (mounted) setMunLoading(false);
      }
    };

    fetchMunicipalities();
    return () => {
      mounted = false;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ================= CHAT =================
  const askAI = async () => {
    if (!question.trim()) return;

    setChat((prev) => [...prev, { role: "user", text: question }]);
    setLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/chat/", {
        municipality,
        question,
      });

      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text: res.data.answer,
          csvs: res.data.csv_files || [],
        },
      ]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        { role: "ai", text: "❌ Backend not reachable" },
      ]);
    }

    setQuestion("");
    setLoading(false);
  };

  // ================= SCRAPER =================
  const scrapeWebsite = async () => {
    if (!scrapeUrl.trim()) return;

    setScrapeLoading(true);

    try {
      const res = await axios.post("http://127.0.0.1:8000/scrape", {
        url: scrapeUrl,
      });

      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text: "🕷️ Scraping completed successfully",
          scrapeData: res.data.data,
        },
      ]);
    } catch (err) {
      setChat((prev) => [
        ...prev,
        {
          role: "ai",
          text: "❌ Scraping failed",
        },
      ]);
    }

    setScrapeLoading(false);
  };

  // ================= CSV DOWNLOAD =================
  const downloadCSV = () => {
    window.open(
      `http://127.0.0.1:8000/export-csv?limit=${downloadLimit}`,
      "_blank"
    );
  };

  return (
    <div style={styles.page}>
      {/* ================= SIDEBAR ================= */}
      <div style={styles.sidebar}>
        <h2 style={styles.logo}>🏛️ Municipality AI</h2>

        <p style={styles.subText}>Nepal Government Data Assistant</p>

        {/* CURRENT MUNICIPALITY (read-only display) */}
        <div style={{ fontSize: 12, color: "#94a3b8", marginBottom: 6 }}>
          Selected Municipality
        </div>
        <input
  value={municipality}
  onChange={(e) => setMunicipality(e.target.value)}
  placeholder="Select or type..."
  style={styles.input}
/>

        {/* LIMIT */}
        <input
          type="number"
          value={downloadLimit}
          onChange={(e) => setDownloadLimit(e.target.value)}
          style={styles.input}
        />

        {/* DOWNLOAD */}
        <button onClick={downloadCSV} style={styles.downloadBtn}>
          📥 Download CSV
        </button>

        {/* ================= SCRAPER ================= */}
        <div style={styles.sectionTitle}>🕷️ Scraper Tool</div>

        <input
          value={scrapeUrl}
          onChange={(e) => setScrapeUrl(e.target.value)}
          placeholder="Enter municipality URL..."
          style={styles.input}
        />

        <button onClick={scrapeWebsite} style={styles.downloadBtn}>
          {scrapeLoading ? "Scraping..." : "🚀 Scrape Website"}
        </button>

        {/* ================= MUNICIPALITY SCROLLER ================= */}
        <div style={styles.sectionTitle}>📜 Municipalities (Alphabetical)</div>

        <div style={styles.scrollBox}>
          {munLoading && (
            <div style={{ padding: 12, color: "#94a3b8" }}>Loading...</div>
          )}

          {munError && (
            <div style={{ padding: 12, color: "#f87171" }}>{munError}</div>
          )}

          {!munLoading &&
            !munError &&
            municipalities.map((item, i) => (
              <div
                key={i}
                onClick={() => {
                  setMunicipality(item);

                  setChat((prev) => [
                    ...prev,
                    {
                      role: "ai",
                      text: `🔎 Selected: ${item}`,
                    },
                  ]);
                }}
                style={{
                  ...styles.scrollItem,
                  background: municipality === item ? "#1d4ed8" : "#0f172a",
                }}
              >
                {item}
              </div>
            ))}

          {!munLoading && !munError && municipalities.length === 0 && (
            <div style={{ padding: 12, color: "#94a3b8" }}>
              No municipalities found
            </div>
          )}
        </div>
      </div>

      {/* ================= MAIN CHAT ================= */}
      <div style={styles.main}>
        <div style={styles.header}>Municipality AI Assistant</div>

        <div style={styles.chatArea}>
          {chat.length === 0 && (
            <div style={styles.empty}>Ask anything about Nepal municipalities</div>
          )}

          {chat.map((msg, i) => (
            <div
              key={i}
              style={{
                display: "flex",
                flexDirection: "column",
                alignItems: msg.role === "user" ? "flex-end" : "flex-start",
                marginBottom: 15,
              }}
            >
              <div style={styles.role}>{msg.role === "user" ? "You" : "AI"}</div>

              <div
                style={{
                  ...styles.message,
                  background:
                    msg.role === "user"
                      ? "linear-gradient(135deg,#3b82f6,#2563eb)"
                      : "#111827",
                }}
              >
                {msg.text}
              </div>

              {/* SCRAPED DATA */}
              {msg.scrapeData && (
                <div style={styles.csvBox}>
                  <div style={styles.csvTitle}>🧠 Scraped Data</div>

                  <pre style={styles.jsonBox}>
                    {JSON.stringify(msg.scrapeData, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ))}

          {loading && <div style={styles.loading}>AI thinking...</div>}

          <div ref={chatEndRef} />
        </div>

        {/* INPUT BAR */}
        <div style={styles.inputBar}>
          <input
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && askAI()}
            placeholder="Ask something..."
            style={styles.chatInput}
          />

          <button onClick={askAI} style={styles.sendBtn}>
            ➜
          </button>
        </div>
      </div>
    </div>
  );
}

/* ================= STYLES ================= */

const styles = {
  page: {
    display: "flex",
    height: "100vh",
    background: "#0a0f1c",
    color: "#fff",
    fontFamily: "Segoe UI",
  },

  sidebar: {
    width: 300,
    padding: 20,
    background: "#050816",
    borderRight: "1px solid #1f2937",
    display: "flex",
    flexDirection: "column",
    gap: 10,
  },

  logo: { marginBottom: 5 },

  subText: {
    fontSize: 12,
    color: "#94a3b8",
    marginBottom: 10,
  },

  sectionTitle: {
    marginTop: 10,
    fontSize: 12,
    color: "#94a3b8",
  },

  input: {
    padding: 10,
    borderRadius: 8,
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#fff",
  },

  downloadBtn: {
    padding: 10,
    borderRadius: 8,
    border: "none",
    background: "linear-gradient(135deg,#3b82f6,#06b6d4)",
    color: "#fff",
    cursor: "pointer",
  },

  scrollBox: {
    maxHeight: 280,
    overflowY: "auto",
    border: "1px solid #334155",
    borderRadius: 8,
    marginTop: 5,
  },

  scrollItem: {
    padding: 10,
    cursor: "pointer",
    borderBottom: "1px solid #1f2937",
    color: "#cbd5e1",
  },

  main: { flex: 1, display: "flex", flexDirection: "column" },

  header: {
    padding: 15,
    borderBottom: "1px solid #1f2937",
    background: "#0b1220",
  },

  chatArea: {
    flex: 1,
    padding: 20,
    overflowY: "auto",
  },

  empty: {
    textAlign: "center",
    marginTop: 100,
    color: "#94a3b8",
  },

  role: {
    fontSize: 11,
    marginBottom: 5,
    color: "#94a3b8",
  },

  message: {
    maxWidth: "70%",
    padding: 12,
    borderRadius: 12,
  },

  csvBox: { marginTop: 8 },

  csvTitle: {
    fontSize: 11,
    color: "#94a3b8",
    marginBottom: 5,
  },

  jsonBox: {
    background: "#0f172a",
    padding: 10,
    borderRadius: 8,
    color: "#cbd5e1",
    overflowX: "auto",
  },

  loading: {
    color: "#94a3b8",
  },

  inputBar: {
    display: "flex",
    padding: 15,
    borderTop: "1px solid #1f2937",
  },

  chatInput: {
    flex: 1,
    padding: 12,
    borderRadius: 10,
    border: "1px solid #334155",
    background: "#0f172a",
    color: "#fff",
  },

  sendBtn: {
    marginLeft: 10,
    width: 50,
    border: "none",
    borderRadius: 10,
    background: "linear-gradient(135deg,#3b82f6,#06b6d4)",
    color: "#fff",
    cursor: "pointer",
  },
};
