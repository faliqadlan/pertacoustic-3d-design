# PERTACOUSTIC: Laporan Biweekly 5

Periode: Biweekly 5

Tanggal: 30 Juli 2026
Status: **Preliminary screening: PASS**

Dokumen ini mencatat desain awal dan pemeriksaan menggunakan perhitungan serta simulasi. Status PASS, jika tercapai, hanya berarti bahwa model awal memenuhi kriteria pemeriksaan yang tertulis di laporan ini. Status tersebut **bukan** gambar manufaktur, sertifikasi bejana tekan, atau kualifikasi seal.

## 1. Rencana dan realisasi pekerjaan

Telah dilakukan desain casing, interface ke HTI-02-DHPC/D, electronics layout, thermal analysis, dan structural analysis.

## 2. Ringkasan kemajuan

- Casing dirancang dengan diameter luar (OD) 200 mm, panjang 425 mm, dinding Inconel 35 mm, tutup depan/belakang 50 mm, aerogel radial 42.5 mm, dan PEEK 2 mm.
- Elektronik dipindahkan menjauh dari kedua tutup. Aerogel aksial di depan sepanjang 50 mm dan di belakang sepanjang 71 mm menghambat panas yang masuk dari ujung casing.
- Model CAD memuat tiga jalur konduktor, bagian analog depan, PCM1808, STM32F411, serta ruang RTC/SD/daya.
- PA12/nylon hanya dipertimbangkan untuk komponen pendukung yang tidak menahan tekanan: dudukan elektronik, pengarah kabel, pengganjal, atau penahan tarikan kabel. PA12/nylon tidak dipakai sebagai penghalang langsung terhadap fluida sumur.

## 3. Dasar desain dan istilah mekanik

Ukuran nominal ulir yang dipakai adalah `7/16-20 UNF-2A` pada casing untuk dipasangkan dengan `7/16-20 UNF-2B` pada HTI. Nominal berarti nama ukuran menurut standar; ukuran hasil manufaktur tetap dapat sedikit lebih besar atau kecil selama masih berada dalam toleransi yang diizinkan. `7/16` adalah diameter utama nominal, `20` berarti 20 ulir per inci, `UNF` adalah seri ulir halus, `2A` adalah kelas ulir luar, dan `2B` adalah kelas ulir dalam.

**Thread/ulir** adalah alur heliks untuk menyambungkan dua komponen. **Thread HTI** berarti ulir sambungan milik hydrophone HTI, bukan seal tekanan untuk ruang elektronik. Gambar HTI masih bertanda “for reference only”. Karena itu, **datum** (acuan pengukuran)—permukaan atau sumbu acuan untuk semua pengukuran—dan **thread tolerance** (toleransi ulir)—batas penyimpangan diameter, pitch, serta bentuk ulir—harus dikonfirmasi kepada HTI sebelum manufaktur.

**Envelope** adalah kotak atau ruang batas yang disediakan agar suatu komponen pasti muat. Envelope sementara STM32F411 adalah 55 × 22 × 12 mm dan PCM1808 adalah 52 × 32 × 18 mm. **Assembly clearance** 1,5 mm adalah ruang tambahan agar board dapat dimasukkan dan tidak bergesekan. Dari ukuran tersebut digunakan **clear ID** 41 mm, yaitu diameter dalam bersih yang benar-benar tersedia untuk elektronik setelah material casing dan insulasi dihitung.

![Rakitan CAD](figures/cad_assembly.png)

Adapter depan terdiri dari ulir nominal, **shoulder** atau bidang bertingkat yang menjadi penahan aksial, **spigot** atau bagian silinder yang masuk ke bore pasangan untuk menjaga posisi, tiga lubang kabel, dan dua alur seal awal. **Seal groove** adalah alur tempat O-ring atau seal. **Pressure seal** adalah komponen yang mencegah fluida bertekanan masuk ke ruang elektronik; lokasinya terpisah dari ulir HTI.

Jenis **elastomer** atau bahan lentur seal, **backup ring** yang menopang seal agar tidak terdorong keluar, **extrusion gap** atau celah tempat seal dapat tertekan keluar, dan **tolerance stack** atau gabungan seluruh variasi ukuran komponen belum ditetapkan. Karena itu, geometri alur yang terlihat di CAD masih konseptual dan belum boleh dibuat.

Dalam model struktur, **barrel** adalah dinding silinder panjang dan **endcap** adalah tutup tekanan di depan serta belakang. Model FEA (Finite Element Analysis) dibuat **defeatured**, artinya detail kecil seperti ulir, kontak seal, dan alur lokal dihilangkan agar pemeriksaan global casing lebih stabil dan lebih cepat.

## 4. Susunan elektronik

![Penampang memanjang](figures/longitudinal_section.png)

Urutan aksialnya adalah HTI, analog front-end, PCM1808, STM32F411, lalu RTC/SD/daya. **Conductor path** adalah jalur listrik dari tiga pin/kabel HTI menuju elektronik. Tiga jalur dipertahankan karena pinout final belum dikonfirmasi.

**Analog front-end** adalah rangkaian pertama yang menerima sinyal analog kecil dari hydrophone, kemudian menguatkan dan menyaringnya sebelum masuk ke PCM1808. **Analog front-end zone** adalah ruang di dalam model yang dialokasikan untuk rangkaian tersebut. **Configurable analog front-end** berarti nilai penguatan, penyaringan, dan hubungan pin belum dikunci sehingga dapat disesuaikan setelah data HTI tersedia.

**Preamplifier mode** menjelaskan apakah preamplifier berada di dalam HTI, membutuhkan catu daya tertentu, dan bagaimana sinyal keluarannya dibaca. **Pinout** adalah daftar fungsi setiap pin, misalnya sinyal, ground, dan catu daya. PCM1808 mengubah sinyal analog menjadi data digital; STM32F411 mengendalikan akuisisi dan penyimpanan; ruang RTC/SD/daya disediakan untuk jam waktu nyata, kartu penyimpanan, dan rangkaian catu daya.

## 5. Pemeriksaan struktur

| OD (mm) | Muat | Dinding Inconel (mm) | Aerogel (mm) | Pemeriksaan analitis | Catatan |
|---:|---|---:|---:|---|---|
| 43 | no | - | - | - | Insufficient radial space for 41 mm clear ID, PEEK, pressure wall, and aerogel. |
| 50 | no | - | - | - | Insufficient radial space for 41 mm clear ID, PEEK, pressure wall, and aerogel. |
| 60 | yes | 5.25 | 2.25 | PASS | analytical geometry/wall screen only |
| 200 | yes | 35.0 | 42.5 | PASS | analytical geometry/wall screen only |

Perhitungan **Lamé** memperkirakan tegangan pada dinding silinder tebal akibat tekanan. **Equivalent stress** atau tegangan von Mises menyederhanakan kombinasi tegangan menjadi satu angka untuk dibandingkan dengan kekuatan luluh material. Hasil analitis dinding adalah 206.79 MPa dengan **factor of safety (FoS)** 4.84. FoS adalah perbandingan kekuatan material terhadap beban terhitung; FoS 2 berarti kapasitas perhitungan dua kali beban rencana.

![Perbandingan struktur](figures/structural_comparison.png)

FEA menghitung seluruh barrel dan kedua endcap. Tegangan coarse, medium, dan fine adalah 199.21, 206.52, dan 212.51 MPa. **Displacement** adalah perpindahan bentuk akibat beban; hasil fine adalah 0.785 mm.

**Mesh convergence** memeriksa apakah hasil berubah ketika elemen dibuat lebih kecil. Perubahan medium ke fine adalah 2.82% untuk tegangan dan 3.47% untuk displacement. Angka ini dilaporkan sebagai informasi karena pemeriksaan struktur periode ini dibatasi pada screening awal, bukan sertifikasi struktur.

**Buckling** adalah kegagalan ketika dinding tertekuk akibat tekanan luar sebelum material patah. Persamaan silinder panjang memberi buckling factor analitis 18.04; faktor 2 berarti kapasitas hitung sedikitnya dua kali tekanan rencana. Pemeriksaan ini cukup untuk screening awal, tetapi bukan pengganti uji tekanan atau sertifikasi. Perhitungan retensi ulir memberi FoS 6.58, tetapi angka nominal ini belum menggantikan konfirmasi toleransi ulir dan desain seal.

**Thermo-mechanical load** berarti beban struktur yang menggabungkan tekanan dan perubahan temperatur. Model sekarang masih memindahkan profil temperatur radial ke model struktur, belum melakukan **direct mapping** dari setiap titik hasil termal 3D. Hasil struktur karena itu tetap dibaca sebagai screening awal.

## 6. Pemeriksaan termal

![Riwayat temperatur](figures/thermal_history.png)

Simulasi termal 3D casing tertutup memperhitungkan barrel, endcap Inconel depan/belakang, aerogel radial, **front/rear axial aerogel buffer**, serta daya panas internal elektronik sebesar **1 W** (1 joule per detik). **Axial aerogel buffer** adalah lapisan aerogel memanjang di antara endcap dan ruang elektronik untuk menghambat aliran panas aksial dari ujung casing.

| Pemeriksaan input model | Nilai |
|---|---|
| Temperatur awal | 25°C |
| Batas luar | 150°C pada barrel dan kedua endcap |
| Panas internal | 1 W total |
| Waktu | 3.600 detik atau 1 jam |
| Perubahan mesh medium ke fine | 1.1799% |

| Zona elektronik | Temperatur maksimum batas rongga setelah 1 jam (°C) | Penilaian |
|---|---:|---|
| Analog front-end | 62.06 | diterima sementara |
| PCM1808 | 62.88 | diterima sementara |
| STM32F411 | 62.38 | diterima sementara |
| RTC/SD/power | 62.31 | diterima sementara |

**Maximum cavity-boundary temperature** adalah temperatur tertinggi pada permukaan dalam yang menghadap ruang elektronik, bukan temperatur chip. Nilai maksimum model adalah 62.88°C. **Chip junction temperature** adalah temperatur di bagian aktif silikon; nilainya belum dihitung karena board dan chip belum dimodelkan sebagai benda padat.

**Operating ceiling** adalah temperatur operasi maksimum yang diizinkan produsen komponen. PCM1808 memiliki ceiling 85°C [2], tetapi desain memakai batas pemeriksaan 70°C agar tersedia margin.

Perbedaan model radial dan model 3D tertutup berasal dari panas yang juga masuk melalui endcap. Menambah diameter dan aerogel radial memperlambat panas dari sisi barrel, tetapi tidak memperpanjang jalur panas dari depan atau belakang. Karena itu, desain ini juga memindahkan elektronik dan menambah insulasi aksial.

**Thermal resistance** dalam K/W menyatakan kenaikan beda temperatur yang dibutuhkan untuk mengalirkan satu watt panas; angka lebih besar berarti insulasi lebih baik. Perkiraan resistansi aksial depan adalah 454.4 K/W dan belakang 645.2 K/W. **Axial heat leak** adalah panas yang merambat dari endcap menuju elektronik melalui jalur tersebut; perkiraan awalnya 0.28 W dari depan dan 0.19 W dari belakang.

Angka **0,0007%** pada model lama berarti hasil mesh medium dan fine hanya berbeda sekitar tujuh bagian per sejuta. Itu menunjukkan hasil mesh termal lama sudah stabil, tetapi tidak berarti temperaturnya memenuhi batas. Nilai desain baru yang dipakai untuk status adalah 1.1799%.

## 7. Hasil saat ini

Status desain: **Preliminary screening: PASS**.

Status PASS ditetapkan apabila seluruh zona elektronik tidak melebihi 70°C, perubahan mesh termal di bawah 5%, tegangan statik fine tidak melebihi 500 MPa, serta perhitungan analitis memberi FoS luluh dan buckling factor sedikitnya 2. Status ini tetap merupakan screening awal, bukan sertifikasi struktur.

## 8. Pekerjaan berikutnya

### Dapat dilakukan sekarang dengan model

- Menjaga CAD, posisi elektronik, panjang insulasi, dan geometri endcap tetap konsisten dengan model yang sudah diperiksa.
- Mengulang simulasi bila ukuran, daya, material, tekanan, atau temperatur rencana berubah.
- Membuat daftar pendek material berdasarkan produk yang benar-benar tersedia.

### Memerlukan pengukuran, data pemasok, atau pengujian fisik

- Mengukur board STM32F411 dan PCM1808 beserta konektor dan header.
- Mengukur daya elektronik saat logging dan standby; angka 1 W saat ini masih asumsi.
- Memilih grade aerogel, PEEK, perlakuan panas Inconel, elastomer, dan backup ring yang dapat dibeli.
- Menghitung alur seal dan tolerance stack setelah material seal, celah, serta ukuran manufaktur ditetapkan.
- Menguji kupon Inconel/aerogel/PEEK di oven atau bak panas untuk membandingkan model dengan benda nyata.

## 9. Referensi

1. [High Tech Inc., HTI-02-DHPC/D](https://www.hightechincusa.com/products/hydrophones/hti02dhpc.html)
2. [Texas Instruments, PCM1808](https://www.ti.com/product/PCM1808)
3. [Special Metals, INCONEL Alloy 718 Technical Bulletin](https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-718.pdf)
4. [Victrex, PEEK 450G Technical Data Sheet](https://images.victrex.com/-/media/downloads/datasheets/victrex_tds_450g.pdf)
5. [Aspen Aerogels, Pyrogel HPS Product Data Sheet](https://www.aerogel.com/wp-content/uploads/2021/06/Pyrogel-HPS-Datasheet-English.pdf)
6. HTI-02-DHPC/D Mechanical Outline 02-001-25-00-00, supplier document marked "for reference only".
