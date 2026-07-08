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

    # Para cada gen de referencia, tomamos el mejor hit disponible (mayor identidad)
    mejores_hits = resultados.sort_values("identidad", ascending=False).drop_duplicates(subset="query")
    print(f"Se encontraron {len(mejores_hits)} genes con al menos un match")
    print(mejores_hits[["query", "hit", "identidad"]])

    accesiones_encontradas = {}
    for _, fila in mejores_hits.iterrows():
        nombre_gen = fila["query"].split("|")[1]
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

def agregar_especie(nombre_cientifico, genes_interes=None, config_path="config/especies.yaml"):
    """
    Agrega (o actualiza) una especie en el archivo de configuración YAML.
    Busca automáticamente el mejor accession de genoma disponible en NCBI.

    nombre_cientifico: ej. 'Cordyceps militaris'
    genes_interes: diccionario {nombre_gen: accession_uniprot}, opcional
    """
    import subprocess
    import json

    # Generar la clave automáticamente a partir del nombre científico
    clave = nombre_cientifico.lower().replace(" ", "_")

    # Buscar automáticamente el mejor accession disponible
    resultado = subprocess.run(
        ["datasets", "summary", "genome", "taxon", nombre_cientifico],
        capture_output=True, text=True, check=True
    )
    data = json.loads(resultado.stdout)

    if not data.get("reports"):
        raise ValueError(f"No se encontraron genomas para '{nombre_cientifico}' en NCBI")

    # Elegir el ensamblaje con mejor N50 (más contiguo = mejor calidad)
    mejor = max(data["reports"], key=lambda r: r.get("assembly_stats", {}).get("contig_n50", 0))
    accession = mejor["current_accession"]

    print(f"Accession seleccionado automáticamente: {accession} (N50: {mejor['assembly_stats'].get('contig_n50'):,} bp)")

    config_path = Path(config_path)
    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f) or {"especies": {}}
    else:
        config = {"especies": {}}

    config["especies"][clave] = {
        "nombre_cientifico": nombre_cientifico,
        "accession": accession,
        "genes_interes": genes_interes or {},
    }

    with open(config_path, "w") as f:
        yaml.dump(config, f, allow_unicode=True, sort_keys=False)

    print(f"Especie '{clave}' agregada/actualizada en {config_path}")
    return clave