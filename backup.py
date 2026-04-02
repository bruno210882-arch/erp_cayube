@app.route("/backup")
def backup():
    uri = os.getenv("DATABASE_URL")

    if uri.startswith("postgres://"):
        uri = uri.replace("postgres://", "postgresql://", 1)

    filename = "backup.sql"

    comando = f'pg_dump "{uri}" > {filename}'
    os.system(comando)

    return send_file(filename, as_attachment=True)