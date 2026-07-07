import yaml
from pathlib import Path

from genome_mining.descarga import descargar_genoma, obtener_rutas_archivos
from genome_mining.blast_utils import descargar_secuencias_referencia, construir_base_blast, correr_blast
from genome_mining.visualizacion import extraer_coordenadas, graficar_cluster


def analizar_especie(nombre_especie, config_path="config/especies.yaml", carpeta_resultados="resultados"):
    with open(config_path) as f:
        config = yaml.safe_load(f)

    if nombre_especie not in config["especies"]:
        raise ValueError(f"'{nombre_especie}' no está definida en {config_path}")

    datos = config["especies"][nombre_especie]
    carpeta_especie = Path(carpeta_resultados) / nombre_especie
    carpeta_especie.mkdir(parents=True, exist_ok=True)

    print(f"--- Analizando {datos['nombre_cientifico']} ---")

    print("Descargando genoma...")
    ruta_genoma = descargar_genoma(datos["accession"], carpeta_destino="datos")
    archivos = obtener_rutas_archivos(ruta_genoma, datos["accession"])

    if not datos.get("genes_interes"):
        print("No hay genes de referencia definidos para esta especie.")
        print("Este caso requiere un enfoque de descubrimiento (antiSMASH) en vez de BLAST dirigido.")
        return None

    print("Descargando secuencias de referencia...")
    ruta_referencias = descargar_secuencias_referencia(
        datos["genes_interes"], carpeta_especie / "referencias.fasta"
    )

    print("Construyendo base de datos BLAST...")
    ruta_db = construir_base_blast(archivos["proteinas"], carpeta_especie / "blast_db" / "proteinas")

    print("Corriendo BLAST...")
    resultados = correr_blast(ruta_referencias, ruta_db, carpeta_especie / "blast_resultados.tsv")

    matches_perfectos = resultados[resultados["identidad"] == 100.0]
    print(f"Se encontraron {len(matches_perfectos)} matches con 100% de identidad")

    # Mapear nombre de gen -> accession de proteína encontrado, usando la columna 'query'
    accesiones_encontradas = {}
    for _, fila in matches_perfectos.iterrows():
        nombre_gen = fila["query"].split("|")[1]  # extrae el accession UniProt del query
        for nombre, accession_uniprot in datos["genes_interes"].items():
            if accession_uniprot == nombre_gen:
                accesiones_encontradas[nombre] = fila["hit"]

    print("Extrayendo coordenadas del GFF3...")
    coordenadas = extraer_coordenadas(archivos["gff"], accesiones_encontradas)

    print("Generando visualización...")
    graficar_cluster(
        coordenadas,
        titulo=f"Cluster biosintético — {datos['nombre_cientifico']}",
        ruta_salida=carpeta_especie / "cluster.png"
    )

    return coordenadas