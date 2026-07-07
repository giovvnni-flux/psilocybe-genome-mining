import subprocess
import os
from pathlib import Path


def descargar_genoma(accession, carpeta_destino="datos"):
    """
    Descarga un genoma desde NCBI usando el accession (ej. 'GCF_017499595.1').
    Devuelve la ruta a la carpeta donde quedaron los archivos.
    """
    ruta_especie = Path(carpeta_destino) / accession
    ruta_especie.mkdir(parents=True, exist_ok=True)

    zip_path = ruta_especie / "ncbi_dataset.zip"

    if not zip_path.exists():
        subprocess.run([
            "datasets", "download", "genome", "accession", accession,
            "--include", "genome,gff3,protein",
            "--filename", str(zip_path),
        ], check=True)

        subprocess.run([
            "unzip", "-o", str(zip_path), "-d", str(ruta_especie)
        ], check=True)
    else:
        print(f"El genoma {accession} ya fue descargado previamente, se reutiliza.")

    return ruta_especie / "ncbi_dataset" / "data" / accession


def obtener_rutas_archivos(ruta_datos, accession):
    """
    Dado el directorio de datos de un genoma, encuentra las rutas exactas
    de los archivos FASTA, GFF3 y proteínas (los nombres varían según el ensamblaje).
    """
    archivos = list(ruta_datos.glob("*"))

    fasta = next((f for f in archivos if f.suffix == ".fna"), None)
    gff = next((f for f in archivos if f.name == "genomic.gff"), None)
    proteinas = next((f for f in archivos if f.name == "protein.faa"), None)

    return {"fasta": fasta, "gff": gff, "proteinas": proteinas}