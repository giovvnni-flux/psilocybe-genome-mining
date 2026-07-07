import subprocess
from pathlib import Path
import pandas as pd
import requests


def descargar_secuencias_referencia(genes_interes, ruta_salida):
    """
    Descarga secuencias de proteína desde UniProt para un diccionario
    de genes {nombre: accession_uniprot}.
    """
    ruta_salida = Path(ruta_salida)
    ruta_salida.parent.mkdir(parents=True, exist_ok=True)

    with open(ruta_salida, "w") as out_file:
        for nombre, accession in genes_interes.items():
            url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
            response = requests.get(url)
            if response.status_code == 200:
                out_file.write(response.text)
                print(f"{nombre} ({accession}) descargado correctamente")
            else:
                print(f"Error descargando {nombre} ({accession}): status {response.status_code}")

    return ruta_salida


def construir_base_blast(ruta_proteinas, ruta_db):
    """
    Construye una base de datos BLAST a partir de un archivo de proteínas (.faa).
    """
    ruta_db = Path(ruta_db)
    ruta_db.parent.mkdir(parents=True, exist_ok=True)

    subprocess.run([
        "makeblastdb",
        "-in", str(ruta_proteinas),
        "-dbtype", "prot",
        "-out", str(ruta_db)
    ], check=True)

    return ruta_db


def correr_blast(ruta_query, ruta_db, ruta_salida, evalue="1e-10"):
    """
    Corre BLASTP y devuelve los resultados como un DataFrame de pandas.
    """
    subprocess.run([
        "blastp",
        "-query", str(ruta_query),
        "-db", str(ruta_db),
        "-out", str(ruta_salida),
        "-outfmt", "6 qseqid sseqid pident length evalue bitscore stitle",
        "-evalue", evalue,
    ], check=True)

    columnas = ["query", "hit", "identidad", "longitud", "evalue", "bitscore", "descripcion"]
    return pd.read_csv(ruta_salida, sep="\t", names=columnas)