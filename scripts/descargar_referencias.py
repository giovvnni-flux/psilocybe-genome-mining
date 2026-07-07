import requests

# Accessions de UniProt para las 4 enzimas de la ruta de psilocibina
# Fuente: Fricke et al. 2017, depositado en UniProt
accessions = {
    "PsiD": "P0DPA6",
    "PsiH": "P0DPA7",
    "PsiK": "P0DPA8",
    "PsiM": "P0DPA9",
}

with open("referencias_psilocibina.fasta", "w") as out_file:
    for nombre, accession in accessions.items():
        url = f"https://rest.uniprot.org/uniprotkb/{accession}.fasta"
        response = requests.get(url)
        if response.status_code == 200:
            out_file.write(response.text)
            print(f"{nombre} ({accession}) descargado correctamente")
        else:
            print(f"Error descargando {nombre} ({accession}): status {response.status_code}")