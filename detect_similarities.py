from flask import Flask, request, render_template, send_from_directory
import os, zipfile, shutil
from detect_similarities import main as detect_main

UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=["GET", "POST"])
def index():
    csv_url = None
    if request.method == "POST":
        zip_file = request.files.get("zipfile")
        if zip_file:
            zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
            zip_file.save(zip_path)
            extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
            
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path)
            
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)

            # Run your script
            from detect_similarities import collect_documents
            import pandas as pd
            paths, docs = collect_documents(extract_path)
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity

            if len(docs) >= 2:
                vectorizer = TfidfVectorizer(ngram_range=(1,2), min_df=1)
                X = vectorizer.fit_transform(docs)
                sim = cosine_similarity(X)
                n = len(paths)
                results = []
                for i in range(n):
                    for j in range(i+1, n):
                        score = float(sim[i,j])
                        if score >= 0.60:
                            results.append((str(paths[i]), str(paths[j]), round(score,3)))
                if results:
                    df = pd.DataFrame(results, columns=["file_a","file_b","score"])
                    df = df.sort_values("score", ascending=False)
                    csv_path = os.path.join(UPLOAD_FOLDER, "suspicious_pairs.csv")
                    df.to_csv(csv_path, index=False)
                    csv_url = "/uploads/suspicious_pairs.csv"
    return render_template("index.html", csv_url=csv_url)

@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == "__main__":
    app.run(debug=True)
