from Bio import SeqIO

path = "psilocybe_penvy/ncbi_dataset/data/GCF_017499595.1/GCF_017499595.1_MGC_Penvy_1_genomic.fna"

contigs = list(SeqIO.parse(path, "fasta"))

print(f"Número de contigs: {len(contigs)}")
print(f"Tamaño total del genoma: {sum(len(c.seq) for c in contigs):,} bp\n")

contigs_ordenados = sorted(contigs, key=lambda c: len(c.seq), reverse=True)

print("Los 5 contigs más grandes:")
for c in contigs_ordenados[:5]:
    print(f"  {c.id}: {len(c.seq):,} bp")