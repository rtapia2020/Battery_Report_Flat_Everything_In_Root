
from flask import Flask, render_template, request, send_file
from bs4 import BeautifulSoup
from datetime import datetime
import os
import pdfkit

app = Flask(__name__, template_folder=".")
UPLOAD_FOLDER = "."
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

def analizar_reporte(ruta_archivo):
    with open(ruta_archivo, "r", encoding="utf-8") as file:
        soup = BeautifulSoup(file, "html.parser")

    battery_info = soup.find_all("table")[1]
    rows = battery_info.find_all("tr")

    info = {}
    for row in rows:
        cells = row.find_all("td")
        if len(cells) == 2:
            label = cells[0].text.strip().lower()
            value = cells[1].text.strip()
            if "design capacity" in label:
                info["design_capacity"] = value
            elif "full charge capacity" in label:
                info["full_charge_capacity"] = value
            elif "cycle count" in label:
                info["cycle_count"] = value

    return info

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["batteryfile"]
        export_pdf = "export_pdf" in request.form
        if file and file.filename.endswith(".html"):
            filepath = os.path.join(app.config["UPLOAD_FOLDER"], file.filename)
            file.save(filepath)
            data = analizar_reporte(filepath)

            if export_pdf:
                rendered = render_template("report.html", info=data, fecha=datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                pdf_path = os.path.join(app.config["UPLOAD_FOLDER"], "reporte_bateria.pdf")
                pdfkit.from_string(rendered, pdf_path)
                return send_file(pdf_path, as_attachment=True)

            output_path = os.path.join(app.config["UPLOAD_FOLDER"], "reporte_generado.html")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(render_template("report.html", info=data, fecha=datetime.now().strftime("%d/%m/%Y %H:%M:%S")))
            return send_file(output_path, as_attachment=True)

    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
