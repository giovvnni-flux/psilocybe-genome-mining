import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Datos reales obtenidos por BLAST + GFF3 (ver resultados_blast.tsv)
genes = [
    {"nombre": "PsiK", "inicio": 1663425, "fin": 1667194, "hebra": "+", "producto": "Kinasa"},
    {"nombre": "PsiH", "inicio": 1667511, "fin": 1669282, "hebra": "+", "producto": "P450 monooxigenasa"},
    {"nombre": "psiT2", "inicio": 1671937, "fin": 1672379, "hebra": "-", "producto": "Transportador MFS"},
    {"nombre": "PsiM", "inicio": 1673493, "fin": 1675081, "hebra": "-", "producto": "Metiltransferasa"},
    {"nombre": "PsiD", "inicio": 1676182, "fin": 1677607, "hebra": "-", "producto": "Descarboxilasa"},
]

fig, ax = plt.subplots(figsize=(12, 3))

# Línea base representando el contig
inicio_min = min(g["inicio"] for g in genes) - 500
fin_max = max(g["fin"] for g in genes) + 500
ax.plot([inicio_min, fin_max], [0, 0], color="gray", linewidth=1, zorder=1)

colores = {"PsiK": "#4C72B0", "PsiH": "#55A868", "psiT2": "#DD8452", "PsiM": "#C44E52", "PsiD": "#8172B2"}

for gen in genes:
    ancho = gen["fin"] - gen["inicio"]
    color = colores[gen["nombre"]]

    # Dibuja el gen como una flecha (rectángulo con punta indicando la hebra)
    direccion = 1 if gen["hebra"] == "+" else -1
    rect = patches.FancyArrow(
        gen["inicio"] if direccion == 1 else gen["fin"],
        0,
        ancho * direccion,
        0,
        width=0.3,
        head_width=0.6,
        head_length=ancho * 0.15,
        length_includes_head=True,
        color=color,
        zorder=2,
    )
    ax.add_patch(rect)

    # Etiqueta con el nombre del gen
    centro = (gen["inicio"] + gen["fin"]) / 2
    ax.text(centro, 0.9, gen["nombre"], ha="center", fontsize=11, fontweight="bold")
    ax.text(centro, -0.9, gen["producto"], ha="center", fontsize=8, style="italic")

ax.set_xlim(inicio_min, fin_max)
ax.set_ylim(-1.5, 1.5)
ax.set_yticks([])
ax.set_xlabel("Posición en el contig NC_063008.1 (pb)")
ax.set_title("Cluster biosintético de psilocibina — Psilocybe cubensis (cepa P.envy)")

plt.tight_layout()
plt.savefig("cluster_psilocibina.png", dpi=150)
print("Gráfico guardado como cluster_psilocibina.png")