<h1>EduCheck</h1>

  <p class="muted">EduCheck is a tool that allows faculty to upload student ZIP submissions, automatically extract files, detect duplicate or similar work, and generate an instant CSV report. It eliminates manual checking, saves time, and supports large-scale academic evaluation.</p>

  <section class="section">
    <h2>Live Demo</h2>
    <p><a href="https://educheck-scanner-onrender-com.onrender.com" target="_blank" rel="noopener noreferrer">https://educheck-scanner-onrender-com.onrender.com</a></p>
  </section>

  <section class="section">
    <h2>What it does</h2>
    <ul>
      <li>Upload a ZIP file containing student submissions.</li>
      <li>Automatically extract and analyze the contents.</li>
      <li>Detect similar or duplicate files using text comparison.</li>
      <li>Generate a ready-to-download CSV report.</li>
    </ul>
  </section>

  <section class="section">
    <h2>Problem solved</h2>
    <p class="small">Faculty often spend hours manually checking assignments and identifying copied work. EduCheck automates this process by extracting submissions, comparing their contents, and producing a similarity report instantly.</p>
  </section>

  <section class="section">
    <h2>Project structure</h2>
    <pre><code>EduCheck/
├── templates/               # Frontend HTML templates
├── app.py                   # Flask backend
├── detect_similarities.py   # Script for detecting similar submissions
├── requirements.txt         # Dependencies
├── render.yaml              # Render deployment configuration
└── README.html
</code></pre>
  </section>

  <section class="section">
    <h2>Tech stack</h2>
    <ul>
      <li>Backend: Python Flask</li>
      <li>Similarity detection: Jaccard similarity algorithm</li>
      <li>PDF handling: PyPDF2 (lightweight alternative to pdfplumber)</li>
      <li>Deployment: Render</li>
    </ul>
  </section>

  <section class="section">
    <h2>How it works (high level)</h2>
    <ol>
      <li>Faculty uploads a ZIP file containing student submissions.</li>
      <li>Each file is extracted and read for content comparison.</li>
      <li>Jaccard similarity checks identify copied or near-duplicate work.</li>
      <li>Results are compiled into a CSV report for download.</li>
    </ol>
  </section>

  <section class="section">
    <h2>Usage</h2>
    <p class="small">Basic steps to run locally:</p>
    <pre><code># Install dependencies
pip install -r requirements.txt

# Run the Flask server
python app.py

# Open the interface in your browser
http://localhost:5000
</code></pre>
  </section>

  <section class="section">
    <h2>Deployment</h2>
    <p class="small">The project is deployed using <strong>Render</strong>. It runs the Flask server automatically from <code>app.py</code> and serves the web interface at the live link above. Render handles build, environment, and hosting configuration without additional setup.</p>
  </section>

  <section class="section">
    <h2>Notes</h2>
    <ul>
      <li>Jaccard similarity efficiently compares text-based submissions without heavy ML dependencies.</li>
      <li>Designed for low memory usage to handle large ZIP uploads.</li>
      <li>Generates a clean CSV summary file ready for academic review.</li>
    </ul>
  </section>
