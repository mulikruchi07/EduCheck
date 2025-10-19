from flask import Flask, request, render_template, send_from_directory
import os
import zipfile
import shutil
from detect_similarities import collect_documents
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# ------------------- CONFIG -------------------
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
# --------------------------------------------

@app.route("/", methods=["GET", "POST"])
def index():
    csv_url = None
    message = None

    if request.method == "POST":
        zip_file = request.files.get("zipfile")
        if zip_file:
            zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
            zip_file.save(zip_path)

            # Extract ZIP
            extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
            if os.path.exists(extract_path):
                shutil.rmtree(extract_path)
            os.makedirs(extract_path)

            try:
                with zipfile.ZipFile(zip_path, "r") as zip_ref:
                    zip_ref.extractall(extract_path)
            except Exception as e:
                message = f"Error extracting ZIP: {e}"
                return render_template("index.html", csv_url=None, message=message)

            # Collect documents
            paths, docs = collect_documents(extract_path)

            if len(docs) < 2:
                message = "Need at least 2 documents in the ZIP."
            else:
                # Compute TF-IDF similarity
                vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
                X = vectorizer.fit_transform(docs)
                sim = cosine_similarity(X)

                results = []
                n = len(paths)
                for i in range(n):
                    for j in range(i + 1, n):
                        score = float(sim[i, j])
                        if score >= 0.60:  # threshold
                            results.append((str(paths[i]), str(paths[j]), round(score, 3)))

                if results:
                    df = pd.DataFrame(results, columns=["file_a", "file_b", "score"])
                    df = df.sort_values("score", ascending=False)
                    csv_path = os.path.join(UPLOAD_FOLDER, "suspicious_pairs.csv")
                    df.to_csv(csv_path, index=False)
                    csv_url = "/uploads/suspicious_pairs.csv"
                else:
                    message = "No suspicious pairs found (threshold 0.60)."

    return render_template("index.html", csv_url=csv_url, message=message)


@app.route("/uploads/<filename>")
def download_file(filename):
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


if __name__ == "__main__":
    app.run(debug=True)
