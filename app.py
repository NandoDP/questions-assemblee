from flask import Flask, render_template_string

app = Flask(__name__)

@app.route("/")
def home():
    superset_url = "http://localhost:8088/superset/dashboard/1/?standalone=true"
    return render_template_string("""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <title>Dashboard Superset intégré</title>
        <style>
            body { margin: 0; }
            iframe { width: 100vw; height: 100vh; border: none; }
        </style>
    </head>
    <body>
        <iframe src="{{ superset_url }}"></iframe>
    </body>
    </html>
    """, superset_url=superset_url)

if __name__ == "__main__":
    app.run(debug=True, port=5000)
