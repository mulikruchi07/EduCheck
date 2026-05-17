<h1>EduCheck</h1>

<p class="muted">
EduCheck is a lightweight academic submission analysis and similarity detection platform that allows faculty to upload structured student ZIP submissions, automatically extract files, detect duplicate or highly similar work, and generate detailed CSV reports with real-time progress tracking and processing controls.
</p>

<section class="section">
  <h2>Live Demo</h2>
  <p>
    <a href="https://educheck.ruchitechs.me" target="_blank" rel="noopener noreferrer">
      https://educheck.ruchitechs.me
    </a>
  </p>
</section>

<section class="section">
  <h2>What it does</h2>
  <ul>
    <li>Upload a ZIP file containing structured student submissions.</li>
    <li>Automatically extract and analyze all files recursively.</li>
    <li>Detect duplicate or highly similar practical submissions.</li>
    <li>Generate detailed CSV reports with full file paths.</li>
    <li>Preview CSV results directly inside the browser.</li>
    <li>Track real-time processing progress.</li>
    <li>Pause, resume, or cancel analysis anytime.</li>
  </ul>
</section>

<section class="section">
  <h2>Problem solved</h2>
  <p class="small">
Faculty often spend hours manually checking practical files and identifying copied submissions. Students commonly rename files or modify roll numbers before resubmitting duplicated work. EduCheck automates this workflow by extracting submissions, analyzing document similarities, and generating structured reports instantly.
  </p>
</section>

<section class="section">
  <h2>Project structure</h2>
  <pre><code>EduCheck/
│
├── static/
│   ├── favicon.ico
│   ├── style.css
│   └── script.js
│
├── templates/
│   └── index.html
│
├── uploads/
├── extracted/
├── reports/
│
├── app.py
├── detect_similarities.py
├── progress_manager.py
├── requirements.txt
├── README.md
└── LICENSE
</code></pre>
</section>

<section class="section">
  <h2>Tech stack</h2>
  <ul>
    <li>Backend: FastAPI + Python</li>
    <li>Frontend: HTML, CSS, Vanilla JavaScript</li>
    <li>Similarity detection: Jaccard similarity algorithm</li>
    <li>PDF handling: PyPDF2</li>
    <li>CSV generation: Pandas</li>
    <li>Processing: Lightweight threaded background execution</li>
  </ul>
</section>

<section class="section">
  <h2>How it works (high level)</h2>
  <ol>
    <li>User uploads a ZIP file containing student submission folders.</li>
    <li>EduCheck extracts and scans all documents recursively.</li>
    <li>Document contents are read and compared for similarities.</li>
    <li>Duplicate or highly similar files are identified.</li>
    <li>A detailed CSV report is generated and previewed in-browser.</li>
  </ol>
</section>

<section class="section">
  <h2>Usage</h2>
  <p class="small">Basic steps to run locally:</p>
  <pre><code># Install dependencies
pip install -r requirements.txt
# Run the FastAPI server
python -m uvicorn app:app --host 0.0.0.0 --port 8000
# Open the interface in your browser
http://localhost:8000
</code></pre>
</section>

<section class="section">
  <h2>Features</h2>
  <ul>
    <li>Real-time progress tracking</li>
    <li>ZIP validation & upload protection</li>
    <li>Pause / Resume / Cancel processing</li>
    <li>Browser completion notifications</li>
    <li>CSV preview before download</li>
    <li>Full file path preservation</li>
    <li>Lightweight and optimized architecture</li>
  </ul>
</section>

<section class="section">
  <h2>Notes</h2>
  <ul>
    <li>Designed to remain lightweight without heavy frontend frameworks.</li>
    <li>Optimized for structured academic submission folders.</li>
    <li>Similarity results should be manually reviewed before academic decisions.</li>
  </ul>
</section>

<section class="section">
  <h2>License</h2>
  <p class="small">
    Licensed under the Apache License 2.0.
  </p>
</section>