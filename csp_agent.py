import json
import csv
import datetime as dt
import itertools as it
from z3 import *

TEMPLATE = "template.json"
OUTPUT = "krs.csv"

print("[+] TEMPLATE FILE:", TEMPLATE, "\n")

# Buka template krs
f = open(TEMPLATE, "r")

# Masukin data ke variabel
data = json.load(f)
daftar_mahasiswa = data["nim"]
daftar_matkul = data["matkul"]

jumlah_mahasiswa = len(daftar_mahasiswa)
jumlah_matkul = len(daftar_matkul)


print("[+] Daftar paralel bentrok: ")

# Mencari paralel yang bentrok
daftar_paralel_bentrok = []
for id_matkul_a, id_matkul_b in it.combinations(range(jumlah_matkul), 2):
    paralel_bentrok = []
    matkul_a = daftar_matkul[id_matkul_a]
    matkul_b = daftar_matkul[id_matkul_b]

    daftar_paralel_a = range(len(matkul_a["paralel"]))
    daftar_paralel_b = range(len(matkul_b["paralel"]))

    for id_paralel_a, id_paralel_b in it.product(daftar_paralel_a, daftar_paralel_b):
        paralel_a = matkul_a["paralel"][id_paralel_a]
        paralel_b = matkul_b["paralel"][id_paralel_b]

        if paralel_a["hari"].lower() != paralel_b["hari"].lower():
            continue

        mulai_paralel_a = dt.datetime.strptime(paralel_a["mulai"], "%H:%M") 
        selesai_paralel_a = dt.datetime.strptime(paralel_a["selesai"], "%H:%M") 

        mulai_paralel_b = dt.datetime.strptime(paralel_b["mulai"], "%H:%M") 
        selesai_paralel_b = dt.datetime.strptime(paralel_b["selesai"], "%H:%M") 


        if selesai_paralel_a < mulai_paralel_b:
            continue
        if selesai_paralel_b < mulai_paralel_a:
            continue
        print(f"[+] {matkul_b['nama']} ({id_paralel_b + 1}) \t {matkul_a['nama']} ({id_paralel_a + 1})")
        paralel_bentrok.append([id_matkul_a, id_paralel_a, id_matkul_b, id_paralel_b])
    daftar_paralel_bentrok.append(paralel_bentrok)


# Buat solver dan symbolic variabel
solver = Solver()
jadwal = [[[Bool(f"jadwal_{i}_{j}_{k}") for k in range(len(daftar_matkul[j]["paralel"]))] for j in range(jumlah_matkul)] for i in range(jumlah_mahasiswa)]


print("\n[+] Membuat symbolic variabel")
print("[+] Membuat constraints")
for id_mahasiswa in range(jumlah_mahasiswa):
    # Constraint 1: Setiap mahasiswa cuma boleh ambil satu paralel di setiap matkul
    for id_matkul in range(jumlah_matkul):
        solver.add(Sum(jadwal[id_mahasiswa][id_matkul]) == 1)

    # Constraint 2: Masing-masing mahasiswa punya jadwal, setiap paralel di jadwal ga boleh bentrok
    for paralel_bentrok in daftar_paralel_bentrok:
        for id_matkul_a, id_paralel_a, id_matkul_b, id_paralel_b in paralel_bentrok:
            solver.add(And(jadwal[id_mahasiswa][id_matkul_a][id_paralel_a], jadwal[id_mahasiswa][id_matkul_b][id_paralel_b]) == False)


# Constraint 3: Jumlah mahasiswa di mMasing-masing paralel harus seimbang, tapi ada faktor toleransi 1.2 biar lebih cepet nyelesain cspnya
for id_matkul, matkul in enumerate(daftar_matkul):
    jumlah_paralel = len(matkul["paralel"])
    jumlah_max_paralel = jumlah_mahasiswa / jumlah_paralel * 1.2
    for id_paralel in range(jumlah_paralel):
        solver.add(Sum([jadwal[id_mahasiswa][id_matkul][id_paralel] for id_mahasiswa in range(jumlah_mahasiswa)]) <= jumlah_max_paralel)

# Solve cspnya
print("[+] Menyelesaikan CSP...\n")
if solver.check() == sat:
    print("[+] Satisfiable")
    print("[+] OUPUT FILE: ", OUTPUT)
    model = solver.model()
    daftar_baris = []

    for id_mahasiswa in range(jumlah_mahasiswa):
        daftar_paralel = []
        for id_matkul in range(jumlah_matkul):
            paralel = next(filter(lambda p: is_true(model[p]), jadwal[id_mahasiswa][id_matkul]))
            id_paralel = jadwal[id_mahasiswa][id_matkul].index(paralel) + 1
            daftar_paralel.append(id_paralel)
        baris = [daftar_mahasiswa[id_mahasiswa]] + [f"{p}" for p in daftar_paralel]
        daftar_baris.append(baris)

    # Tulis ke csv
    header = ["NIM"] + [matkul["nama"] for matkul in daftar_matkul]
    with open(OUTPUT, "w") as out:
        csvwriter = csv.writer(out)
        csvwriter.writerow(header)
        csvwriter.writerows(daftar_baris)
else:
    print("[-] Unsatisfiable")
f.close()
