from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as patches


def extraer_coordenadas(ruta_gff, accesiones_genes):
    """
    Busca en un archivo GFF3 las coordenadas completas (considerando todos
    los exones) de un diccionario de genes {nombre: accession_proteina}.
    """
    posiciones_por_gen = {nombre: [] for nombre in accesiones_genes}

    with open(ruta_gff) as f:
        for linea in f:
            if linea.startswith("#"):
                continue
            campos = linea.strip().split("\t")
            if len(campos) < 9 or campos[2] != "CDS":
                continue

            for nombre, accession in accesiones_genes.items():
                if accession in campos[8]:
                    inicio = int(campos[3])
                    fin = int(campos[4])
                    hebra = campos[6]
                    posiciones_por_gen[nombre].append((inicio, fin, hebra))

    coordenadas = {}
    for nombre, posiciones in posiciones_por_gen.items():
        if not posiciones:
            print(f"Advertencia: no se encontraron coordenadas para {nombre}")
            continue
        inicios = [p[0] for p in posiciones]
        fines = [p[1] for p in posiciones]
        hebra = posiciones[0][2]
        coordenadas[nombre] = {"inicio": min(inicios), "fin": max(fines), "hebra": hebra}

    return coordenadas


def graficar_cluster(coordenadas, titulo, productos=None, ruta_salida=None):
    """
    Genera un diagrama de flechas representando un cluster de genes.
    'productos' es un diccionario opcional {nombre: descripción} para las etiquetas.
    """
    productos = productos or {}
    paleta = ["#4C72B0", "#55A868", "#DD8452", "#C44E52", "#8172B2", "#937860", "#DA8BC3"]
    colores = {nombre: paleta[i % len(paleta)] for i, nombre in enumerate(coordenadas)}

    fig, ax = plt.subplots(figsize=(12, 3))

    inicio_min = min(c["inicio"] for c in coordenadas.values()) - 500
    fin_max = max(c["fin"] for c in coordenadas.values()) + 500
    ax.plot([inicio_min, fin_max], [0, 0], color="gray", linewidth=1, zorder=1)

    for nombre, datos in coordenadas.items():
        ancho = datos["fin"] - datos["inicio"]
        direccion = 1 if datos["hebra"] == "+" else -1
        rect = patches.FancyArrow(
            datos["inicio"] if direccion == 1 else datos["fin"],
            0, ancho * direccion, 0,
            width=0.3, head_width=0.6, head_length=max(ancho * 0.15, 1),
            length_includes_head=True, color=colores[nombre], zorder=2,
        )
        ax.add_patch(rect)
        centro = (datos["inicio"] + datos["fin"]) / 2
        ax.text(centro, 0.9, nombre, ha="center", fontsize=11, fontweight="bold")
        if nombre in productos:
            ax.text(centro, -0.9, productos[nombre], ha="center", fontsize=8, style="italic")

    ax.set_xlim(inicio_min, fin_max)
    ax.set_ylim(-1.5, 1.5)
    ax.set_yticks([])
    ax.set_xlabel("Posición genómica (pb)")
    ax.set_title(titulo)
    plt.tight_layout()

    if ruta_salida:
        plt.savefig(ruta_salida, dpi=150)
        print(f"Gráfico guardado en: {ruta_salida}")

    plt.show()