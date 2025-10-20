from flask import Flask, request, render_template, Response
import os
import zipfile
import shutil
from detect_similarities import collect_documents
import re
from io import StringIO
import csv

UPLOAD_FOLDER = "/tmp/educheck_uploads" 
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def get_ngrams(text, n=3):
    """Generates a set of n-grams (3-word shingles) from text."""
    text = re.sub(r'[^a-zA-Z\s]', '', text.lower())
    words = text.split()
    shingles = set()
    if len(words) < n:
        shingles.add(" ".join(words))
    else:
        for i in range(len(words) - n + 1):
            shingles.add(" ".join(words[i:i+n]))
    return shingles

def jaccard_similarity(set_a, set_b):
    """Calculates the Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 0.0
    intersection = set_a.intersection(set_b)
    union = set_a.union(set_b)
    return len(intersection) / len(union)

@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        zip_file = request.files.get("zipfile")
        if not zip_file:
            message = "No file uploaded."
            return render_template("index.html", message=message)

        zip_path = os.path.join(UPLOAD_FOLDER, zip_file.filename)
        zip_file.save(zip_path)

        extract_path = os.path.join(UPLOAD_FOLDER, "extracted")
        if os.path.exists(extract_path):
            shutil.rmtree(extract_path)
        os.makedirs(extract_path)

        try:
            with zipfile.ZipFile(zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_path)
        except Exception as e:
            message = f"Error extracting ZIP: {e}"
            return render_template("index.html", message=message)

        paths, docs = collect_documents(extract_path)

        if len(docs) < 2:
            message = "Need at least 2 documents in the ZIP."
        else:
            doc_shingles = [get_ngrams(doc) for doc in docs]
            
            results = []
            n = len(paths)
            for i in range(n):
                for j in range(i + 1, n):
                    score = jaccard_similarity(doc_shingles[i], doc_shingles[j])
                    
                    if score >= 0.20:
                        results.append((str(paths[i].name), str(paths[j].name), round(score, 3)))

            if results:
                results.sort(key=lambda x: x[2], reverse=True)
                
                output = StringIO()
                writer = csv.writer(output)
                writer.writerow(["file_a", "file_b", "score"])
                writer.writerows(results)
                
                csv_data = output.getvalue()
                
                shutil.rmtree(extract_path)
                os.remove(zip_path)

                return Response(
                    csv_data,
                    mimetype="text/csv",
                    headers={"Content-disposition": "attachment; filename=suspicious_pairs.csv"}
                )
            else:
                message = "No suspicious pairs found (threshold 0.20)."

        shutil.rmtree(extract_path)
        if os.path.exists(zip_path):
            os.remove(zip_path)

    return render_template("index.html", message=message)


if __name__ == "__main__":
    app.run(debug=True)