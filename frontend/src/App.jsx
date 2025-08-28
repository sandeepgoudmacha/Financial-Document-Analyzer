import React, { useState } from "react";
import axios from "axios";

function App() {
  const [query, setQuery] = useState("");
  const [file, setFile] = useState(null);
  const [jobId, setJobId] = useState(null);
  const [result, setResult] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file || !query) return alert("Please provide both a PDF and a query");

    const formData = new FormData();
    formData.append("query", query);
    formData.append("file", file);

    const res = await axios.post("http://localhost:8000/analyze", formData);
    setJobId(res.data.job_id);
    setResult("⏳ Processing... check result in a few seconds.");
  };

 const checkResult = async () => {
  if (!jobId) return;
  const res = await axios.get(`http://localhost:8000/result/${jobId}`);
  
  // Log response to debug
  console.log("Status response:", res.data);

  if (res.data.status === "finished") {
    // depending on backend, result may be nested
    setResult(res.data.result || res.data.answer || "⚠️ No result field found");
  } else if (res.data.status === "failed") {
    setResult("❌ Job failed. Please try again.");
  } else {
    setResult("⏳ Still processing...");
  }
};


  return (
    <div className="min-h-screen bg-gray-100 flex flex-col items-center justify-center p-6">
      <h1 className="text-2xl font-bold mb-4">📊 Financial Document Analyzer</h1>
      <form onSubmit={handleSubmit} className="bg-white shadow p-6 rounded-lg w-96 space-y-4">
        <input
          type="text"
          placeholder="Enter your query"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          className="border p-2 w-full rounded"
        />
        <input
          type="file"
          accept="application/pdf"
          onChange={(e) => setFile(e.target.files[0])}
          className="w-full"
        />
        <button
          type="submit"
          className="bg-blue-500 text-white px-4 py-2 rounded w-full"
        >
          Analyze
        </button>
      </form>

      {jobId && (
        <div className="mt-6 w-96 text-center">
          <p>Job ID: {jobId}</p>
          <button
            onClick={checkResult}
            className="bg-green-500 text-white px-4 py-2 rounded mt-2"
          >
            Check Result
          </button>
        </div>
      )}

      {result && (
        <div className="bg-white mt-4 p-4 rounded shadow w-96 whitespace-pre-wrap text-sm">
          {typeof result === "string" ? result : JSON.stringify(result, null, 2)}
        </div>
      )}
    </div>
  );
}

export default App;
