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

  // ================= SCRAPER (FULLY RESTORED) =================
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

  // Modern structured renderer for scraped JSON metadata
  const renderScrapedData = (data) => {
    if (!data) return null;
    if (typeof data === "object" && !Array.isArray(data)) {
      return (
        <div style={styles.dataCard}>
          <div style={styles.dataCardHeader}>📊 Extracted Parameters</div>
          <div style={styles.dataGrid}>
            {Object.entries(data).map(([key, val]) => (
              <div key={key} style={styles.dataRow}>
                <span style={styles.dataKey}>{key.replace(/_/g, " ")}</span>
                <span style={styles.dataValue}>
                  {typeof val === "object" ? JSON.stringify(val) : String(val)}
                </span>
              </div>
            ))}
          </div>
        </div>
      );
    }
    return (
      <pre style={styles.jsonBox}>
        {JSON.stringify(data, null, 2)}
      </pre>
    );
  };

  return (
    <div style={styles.page}>
      {/* ================= SIDEBAR ================= */}
      <div style={styles.sidebar}>
        <div>
          <div style={styles.logoContainer}>
            <span style={{ fontSize: "24px" }}>🏛️</span>
            <h2 style={styles.logo}>GovData AI</h2>
          </div>
          <p style={styles.subText}>Nepal Government Intelligence Site</p>
        </div>

        {/* WORKSPACE SECTIONS */}
        <div style={styles.controlGroup}>
          <label style={styles.fieldLabel}>Active Scope</label>
          <input
            value={municipality}
            onChange={(e) => setMunicipality(e.target.value)}
            placeholder="Select or enter region..."
            style={styles.input}
          />
        </div>

        <div style={styles.controlGroup}>
          <label style={styles.fieldLabel}>Data Reporting Limit</label>
          <div style={{ display: "flex", gap: "8px" }}>
            <input
              type="number"
              value={downloadLimit}
              onChange={(e) => setDownloadLimit(e.target.value)}
              style={{ ...styles.input, width: "70px", textAlign: "center" }}
            />
            <button onClick={downloadCSV} style={styles.downloadBtn}>
              📥 Export CSV
            </button>
          </div>
        </div>

        <div style={styles.divider} />

        {/* SCRAPER TOOL */}
        <div style={styles.controlGroup}>
          <label style={styles.fieldLabel}>Intelligence Scraper</label>
          <input
            value={scrapeUrl}
            onChange={(e) => setScrapeUrl(e.target.value)}
            placeholder="https://municipality.gov.np"
            style={styles.input}
          />
          <button onClick={scrapeWebsite} style={styles.secondaryBtn}>
            {scrapeLoading ? "Extracting Assets..." : "🚀 Run Crawler"}
          </button>
        </div>

        <div style={styles.divider} />

        {/* MUNICIPALITY SCROLLER */}
        <div style={{ display: "flex", flexDirection: "column", flex: 1, minHeight: 0 }}>
          <label style={{ ...styles.fieldLabel, marginBottom: "8px" }}>
            📜 Index Directory
          </label>

          <div style={styles.scrollBox}>
            {munLoading && (
              <div style={styles.statusMessage}>Syncing regional registries...</div>
            )}

            {munError && (
              <div style={{ ...styles.statusMessage, color: "#f87171" }}>{munError}</div>
            )}

            {!munLoading &&
              !munError &&
              municipalities.map((item, i) => {
                const isSelected = municipality === item;
                return (
                  <div
                    key={i}
                    onClick={() => {
                      setMunicipality(item);
                      setChat((prev) => [
                        ...prev,
                        {
                          role: "ai",
                          text: `🔎 Focus switched to: ${item}`,
                        },
                      ]);
                    }}
                    style={{
                      ...styles.scrollItem,
                      background: isSelected ? "rgba(59, 130, 246, 0.15)" : "transparent",
                      color: isSelected ? "#60a5fa" : "#94a3b8",
                      borderLeft: isSelected ? "3px solid #3b82f6" : "3px solid transparent",
                      fontWeight: isSelected ? "600" : "400",
                    }}
                  >
                    {item}
                  </div>
                );
              })}

            {!munLoading && !munError && municipalities.length === 0 && (
              <div style={styles.statusMessage}>No matching indexes found</div>
            )}
          </div>
        </div>
      </div>

      {/* ================= MAIN INTERFACE ================= */}
      <div style={styles.main}>
        <div style={styles.header}>
          <div>
            <div style={styles.headerTitle}>Analytical Workspace</div>
            <div style={styles.headerSubtitle}>
              Target Scope: <span style={{ color: "#3b82f6", fontWeight: 500 }}>{municipality || "None Selected"}</span>
            </div>
          </div>
        </div>

        <div style={styles.chatArea}>
          {chat.length === 0 && (
            <div style={styles.emptyContainer}>
              <div style={{ fontSize: "48px", marginBottom: "16px" }}>📊</div>
              <h3 style={{ margin: "0 0 8px 0", color: "#f1f5f9" }}>Ready for Query Engine</h3>
              <p style={{ margin: 0, color: "#64748b", maxWidth: "360px" }}>
                Ask complex local governance questions, monitor budgets, or audit parsed documents.
              </p>
            </div>
          )}

          {chat.map((msg, i) => {
            const isUser = msg.role === "user";
            return (
              <div
                key={i}
                style={{
                  display: "flex",
                  flexDirection: "column",
                  alignItems: isUser ? "flex-end" : "flex-start",
                  marginBottom: 20,
                }}
              >
                <div style={{ ...styles.roleLabel, alignSelf: isUser ? "flex-end" : "flex-start" }}>
                  {isUser ? "Authorized User" : "System Core Intelligence"}
                </div>

                <div
                  style={{
                    ...styles.messageBubble,
                    background: isUser ? "#1e3a8a" : "#0f172a",
                    border: isUser ? "1px solid #2563eb" : "1px solid #1e293b",
                    color: isUser ? "#f8fafc" : "#cbd5e1",
                    borderRadius: isUser ? "16px 16px 2px 16px" : "16px 16px 16px 2px",
                  }}
                >
                  {msg.text}
                </div>

                {msg.scrapeData && (
                  <div
  style={{
    width: "100%",
    maxWidth: "100%",
    marginTop: "4px",
  }}
>
                    {renderScrapedData(msg.scrapeData)}
                  </div>
                )}
              </div>
            );
          })}

          {loading && (
            <div style={styles.loadingWrapper}>
              <div style={styles.pulseDot} />
              <span style={{ color: "#64748b", fontSize: "13px" }}>Processing contextual data arrays...</span>
            </div>
          )}

          <div ref={chatEndRef} />
        </div>

        {/* TERMINAL INPUT PANEL */}
        <div style={styles.inputBar}>
          <div style={styles.inputContainer}>
            <input
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && askAI()}
              placeholder="Query structural assets, laws, or regional reports..."
              style={styles.chatInput}
            />
            <button onClick={askAI} style={styles.sendBtn}>
              <span style={{ transform: "rotate(-45deg)", display: "inline-block" }}>➔</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ================= THEMED DESIGN SYSTEM STYLES ================= */
const styles = {
page: {
  display: "flex",
  width: "100vw",
  height: "100vh",
  minWidth: "100vw",
  height: "100vh",
  background: "#030712",
  color: "#f3f4f6",
  fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Inter", sans-serif',
  overflow: "hidden",
},

  sidebar: {
      width: "22%",
  minWidth: "300px",
  maxWidth: "360px",
    padding: "24px",
    background: "#0b0f19",
    borderRight: "1px solid #1f2937",
    display: "flex",
    flexDirection: "column",
    gap: "20px",
  },

  logoContainer: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    marginBottom: "4px",
  },

  logo: { 
    fontSize: "20px", 
    fontWeight: "700", 
    letterSpacing: "-0.025em", 
    margin: 0,
    background: "linear-gradient(135deg, #f3f4f6, #9ca3af)",
    WebkitBackgroundClip: "text",
    WebkitTextFillColor: "transparent",
  },

  subText: {
    fontSize: "12px",
    color: "#64748b",
    margin: 0,
  },

  divider: {
    height: "1px",
    background: "#1e293b",
    margin: "4px 0",
  },

  controlGroup: {
    display: "flex",
    flexDirection: "column",
    gap: "6px",
  },

  fieldLabel: {
    fontSize: "11px",
    color: "#475569",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.05em",
  },

  input: {
    padding: "10px 14px",
    borderRadius: "8px",
    border: "1px solid #1e293b",
    background: "#030712",
    color: "#f3f4f6",
    fontSize: "14px",
    outline: "none",
    transition: "border-color 0.2s ease",
  },

  downloadBtn: {
    flex: 1,
    padding: "10px",
    borderRadius: "8px",
    border: "none",
    background: "linear-gradient(135deg, #2563eb, #1d4ed8)",
    color: "#fff",
    fontWeight: "500",
    fontSize: "13px",
    cursor: "pointer",
    transition: "opacity 0.2s ease",
  },

  secondaryBtn: {
    padding: "10px",
    borderRadius: "8px",
    border: "1px solid #334155",
    background: "transparent",
    color: "#cbd5e1",
    fontWeight: "500",
    fontSize: "13px",
    cursor: "pointer",
    transition: "background 0.2s ease",
  },

  scrollBox: {
    flex: 1,
    overflowY: "auto",
    border: "1px solid #1e293b",
    borderRadius: "8px",
    background: "#030712",
    padding: "4px",
  },

  scrollItem: {
    padding: "10px 12px",
    cursor: "pointer",
    borderRadius: "6px",
    fontSize: "13px",
    transition: "all 0.15s ease",
    marginBottom: "2px",
  },

  statusMessage: {
    padding: "16px",
    color: "#475569",
    fontSize: "12px",
    textAlign: "center",
  },

  main: {
  flex: "1 1 auto",
  width: "100%",
  minWidth: 0,
  display: "flex",
  flexDirection: "column",
  background: "#030712",
},

  header: {
    padding: "20px 32px",
    borderBottom: "1px solid #1e293b",
    background: "#0b0f19",
    display: "flex",
    alignItems: "center",
    justifyContent: "between",
  },

  headerTitle: {
    fontSize: "16px",
    fontWeight: "600",
    color: "#f1f5f9",
  },

  headerSubtitle: {
    fontSize: "12px",
    color: "#64748b",
    marginTop: "2px",
  },

chatArea: {
  flex: 1,
  width: "100%",
  padding: "32px",
  overflowY: "auto",
  display: "flex",
  flexDirection: "column",
},

  emptyContainer: {
    textAlign: "center",
    margin: "auto",
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
  },

  roleLabel: {
    fontSize: "11px",
    fontWeight: "600",
    textTransform: "uppercase",
    letterSpacing: "0.025em",
    color: "#475569",
    marginBottom: "4px",
  },

  messageBubble: {
      width: "fit-content",
  maxWidth: "92%",
  minWidth: "120px",
    padding: "14px 18px",
    lineHeight: "1.6",
    fontSize: "14px",
    whiteSpace: "pre-wrap",
    wordBreak: "break-word",
    boxShadow: "0 4px 6px -1px rgba(0,0,0,0.1)",
  },

  loadingWrapper: {
    display: "flex",
    alignItems: "center",
    gap: "10px",
    padding: "8px 0",
  },

  pulseDot: {
    width: "8px",
    height: "8px",
    background: "#3b82f6",
    borderRadius: "50%",
    animation: "pulse 1.5s infinite ease-in-out",
  },

  dataCard: {
    background: "#0b0f19",
    border: "1px solid #1e293b",
    borderRadius: "10px",
    overflow: "hidden",
    marginTop: "8px",
    boxShadow: "0 10px 15px -3px rgba(0,0,0,0.3)",
  },

  dataCardHeader: {
    background: "#111827",
    padding: "10px 14px",
    fontSize: "12px",
    fontWeight: "600",
    color: "#9ca3af",
    borderBottom: "1px solid #1e293b",
  },

  dataGrid: {
    padding: "8px 14px",
  },

  dataRow: {
    display: "flex",
    justifyContent: "space-between",
    padding: "8px 0",
    borderBottom: "1px solid rgba(30,41,59,0.5)",
    fontSize: "13px",
  },

  dataKey: {
    color: "#64748b",
    textTransform: "capitalize",
  },

  dataValue: {
    color: "#e2e8f0",
    fontWeight: "500",
  },

  jsonBox: {
    background: "#0b0f19",
    padding: "16px",
    borderRadius: "8px",
    border: "1px solid #1e293b",
    color: "#38bdf8",
    fontSize: "12px",
    fontFamily: "Fira Code, monospace",
    overflowX: "auto",
    maxHeight: "300px",
  },

 inputBar: {
  width: "100%",
  padding: "20px 32px",
  background: "linear-gradient(to top, #030712 70%, transparent)",
},

  inputContainer: {
     width: "100%",
  display: "flex",
    alignItems: "center",
    background: "#0b0f19",
    border: "1px solid #1e293b",
    borderRadius: "12px",
    padding: "6px 8px 6px 16px",
    boxShadow: "0 20px 25px -5px rgba(0,0,0,0.4)",
  },

  chatInput: {
    flex: 1,
    padding: "10px 0",
    fontSize: "14px",
    background: "transparent",
    color: "#fff",
    border: "none",
    outline: "none",
  },

  sendBtn: {
    width: "36px",
    height: "36px",
    borderRadius: "8px",
    border: "none",
    background: "#2563eb",
    color: "#fff",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    fontSize: "14px",
    fontWeight: "bold",
    transition: "background 0.2s ease",
  },
};