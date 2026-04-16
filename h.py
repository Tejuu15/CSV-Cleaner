from io import BytesIO

import pandas as pd
from flask import Flask, render_template_string, request, send_file


def clean_dataframe(df):
        df = df.drop_duplicates()
        df = df.dropna()
        df = df.apply(lambda col: col.str.strip() if col.dtype == "object" else col)
        return df


def clean_csv(input_file, output_file):
        try:
                df = pd.read_csv(input_file)
                cleaned_df = clean_dataframe(df)
                cleaned_df.to_csv(output_file, index=False)
                print("CSV cleaned successfully!")
                print(f"Saved as: {output_file}")
        except Exception as e:
                print("Error:", e)


app = Flask(__name__)

HTML_PAGE = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CSV Cleaner</title>
    <style>
        :root {
            --bg: #f5f8ff;
            --card: #ffffff;
            --text: #16324f;
            --accent: #1f7a8c;
            --accent-hover: #145b69;
            --error-bg: #ffe8e8;
            --error-text: #8f1d1d;
        }
        body {
            margin: 0;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text);
            background: radial-gradient(circle at top, #dbeafe 0%, var(--bg) 55%);
            min-height: 100vh;
            display: grid;
            place-items: center;
            padding: 20px;
        }
        .card {
            width: min(520px, 100%);
            background: var(--card);
            border-radius: 14px;
            box-shadow: 0 16px 40px rgba(19, 42, 76, 0.12);
            padding: 24px;
        }
        h1 {
            margin-top: 0;
            margin-bottom: 8px;
            font-size: 1.7rem;
        }
        p {
            margin-top: 0;
            opacity: 0.9;
        }
        label {
            display: block;
            margin-top: 16px;
            margin-bottom: 6px;
            font-weight: 600;
        }
        input {
            width: 100%;
            box-sizing: border-box;
            padding: 10px;
            border: 1px solid #c8d8e8;
            border-radius: 8px;
            font-size: 0.95rem;
        }
        button {
            width: 100%;
            margin-top: 20px;
            border: 0;
            border-radius: 10px;
            background: var(--accent);
            color: white;
            font-size: 1rem;
            font-weight: 600;
            padding: 12px;
            cursor: pointer;
        }
        button:hover {
            background: var(--accent-hover);
        }
        .error {
            margin-top: 14px;
            background: var(--error-bg);
            color: var(--error-text);
            border-radius: 8px;
            padding: 10px;
            font-size: 0.95rem;
        }
    </style>
</head>
<body>
    <main class="card">
        <h1>CSV Cleaner</h1>
        <p>Upload a CSV to remove duplicate rows, drop missing values, and trim spaces.</p>

        <form method="post" enctype="multipart/form-data">
            <label for="csv_file">CSV File</label>
            <input id="csv_file" name="csv_file" type="file" accept=".csv" required>

            <label for="output_name">Output File Name</label>
            <input id="output_name" name="output_name" type="text" value="cleaned.csv" required>

            <button type="submit">Clean and Download</button>
        </form>

        {% if error %}
            <div class="error">{{ error }}</div>
        {% endif %}
    </main>
</body>
</html>
"""


@app.route("/", methods=["GET", "POST"])
def index():
        if request.method == "GET":
                return render_template_string(HTML_PAGE)

        try:
                uploaded_file = request.files.get("csv_file")
                if uploaded_file is None or uploaded_file.filename == "":
                        return render_template_string(HTML_PAGE, error="Please choose a CSV file.")

                output_name = request.form.get("output_name", "cleaned.csv").strip() or "cleaned.csv"
                if not output_name.lower().endswith(".csv"):
                        output_name += ".csv"

                df = pd.read_csv(uploaded_file)
                cleaned_df = clean_dataframe(df)
                csv_data = cleaned_df.to_csv(index=False).encode("utf-8")

                return send_file(
                        BytesIO(csv_data),
                        mimetype="text/csv",
                        as_attachment=True,
                        download_name=output_name,
                )
        except Exception as e:
                return render_template_string(HTML_PAGE, error=f"Error: {e}")


if __name__ == "__main__":
        app.run(debug=True)