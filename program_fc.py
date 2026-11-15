import json


def baca_file_aturan(lokasi_file):
    with open(lokasi_file, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluasi_syarat(aturan_item, memori_fakta):
    daftar_syarat = aturan_item["jika"]
    jenis_mode = aturan_item["mode"]

    if jenis_mode == "dan":
        for s in daftar_syarat:
            if s not in memori_fakta:
                return False
        return True
    elif jenis_mode == "atau":
        for s in daftar_syarat:
            if s in memori_fakta:
                return True
        return False
    return False


def tampilkan_pohon_alasan(fakta_target, asal_fakta, memori_fakta, level=1):
    if fakta_target not in asal_fakta:
        return

    r = asal_fakta[fakta_target]
    premis_terpakai = [p for p in r["jika"] if p in memori_fakta]
    indent = "  " * level
    print(f"{indent}{fakta_target}  <- {r['id']} ({', '.join(premis_terpakai)})")

    for p in premis_terpakai:
        if p in asal_fakta:
            tampilkan_pohon_alasan(p, asal_fakta, memori_fakta, level + 1)


def jalankan_sistem():
    data_kb = baca_file_aturan("kb_cabai.json")
    aturan_list = data_kb["aturan"]

    # Pisahkan fakta pertanyaan (fakta yang tidak pernah menjadi hasil 'maka')
    himpunan_maka = set(r["maka"] for r in aturan_list)
    himpunan_jika = set(s for r in aturan_list for s in r["jika"])

    pertanyaan_gejala = []
    for r in aturan_list:
        for s in r["jika"]:
            if s not in himpunan_maka and s not in pertanyaan_gejala:
                pertanyaan_gejala.append(s)

    # Kesimpulan akhir adalah hasil 'maka' yang tidak menjadi syarat 'jika' aturan lain
    target_akhir = []
    for r in aturan_list:
        if r["maka"] not in himpunan_jika and r["maka"] not in target_akhir:
            target_akhir.append(r["maka"])

    print(data_kb["judul"])
    print("Jawab y/t.")

    memori = []
    nomor = 1
    for gejala in pertanyaan_gejala:
        respon = input(f"{nomor}. Apakah {gejala}? (y/t) > ").strip().lower()
        if respon == "y":
            memori.append(gejala)
        nomor += 1

    teks_fakta_awal = ", ".join(memori) if memori else "tidak ada"
    print(f"\nFakta awal: {teks_fakta_awal}\n")

    # Proses Forward Chaining
    asal_aturan = {}
    nomor_siklus = 1

    while True:
        aturan_cocok = []
        for r in aturan_list:
            if evaluasi_syarat(r, memori) and r["maka"] not in memori:
                aturan_cocok.append(r)

        if len(aturan_cocok) == 0:
            print(f"Siklus {nomor_siklus}: tidak ada aturan baru, berhenti")
            break

        aturan_terpilih = aturan_cocok[0]
        fakta_baru = aturan_terpilih["maka"]
        memori.append(fakta_baru)
        asal_aturan[fakta_baru] = aturan_terpilih

        print(f"Siklus {nomor_siklus}: {aturan_terpilih['id']} -> {fakta_baru}")
        nomor_siklus += 1

    # Filter kesimpulan akhir yang berhasil masuk ke memori
    hasil_diagnosis = [item for item in memori if item in target_akhir]

    if hasil_diagnosis:
        print(f"\nKesimpulan: {', '.join(hasil_diagnosis)}")
        print("Alasan:")
        for d in hasil_diagnosis:
            tampilkan_pohon_alasan(d, asal_aturan, memori, level=1)
    else:
        print("\nKesimpulan: tidak ada")
        print("Alasan: tidak ada aturan kesimpulan akhir yang terpenuhi.")

    print(f"\nCatatan: {data_kb['batas']}")


if __name__ == "__main__":
    jalankan_sistem()