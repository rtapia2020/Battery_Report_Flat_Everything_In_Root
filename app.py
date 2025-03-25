
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

    info = {
        "design_capacity": "",
        "full_charge_capacity": "",
        "cycle_count": "",
        "computer_name": "",
        "system_product": "",
        "bios": "",
        "os_build": "",
        "platform_role": "",
        "connected_standby": "",
        "report_time": "",
        "battery_name": "",
        "battery_manufacturer": "",
        "battery_serial": "",
        "battery_chemistry": ""
    }

    # Info general
    tables = soup.find_all("table")
    if len(tables) > 0:
        rows = tables[0].find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                if "computer name" in label:
                    info["computer_name"] = value
                elif "system product name" in label:
                    info["system_product"] = value
                elif "bios" in label:
                    info["bios"] = value
                elif "os build" in label:
                    info["os_build"] = value
                elif "platform role" in label:
                    info["platform_role"] = value
                elif "connected standby" in label:
                    info["connected_standby"] = value
                elif "report time" in label:
                    info["report_time"] = value

    # Installed battery info
    if len(tables) > 1:
        rows = tables[1].find_all("tr")
        for row in rows:
            cells = row.find_all("td")
            if len(cells) == 2:
                label = cells[0].text.strip().lower()
                value = cells[1].text.strip()
                if "name" == label:
                    info["battery_name"] = value
                elif "manufacturer" == label:
                    info["battery_manufacturer"] = value
                elif "serial number" in label:
                    info["battery_serial"] = value
                elif "chemistry" in label:
                    info["battery_chemistry"] = value
                elif "design capacity" in label:
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
