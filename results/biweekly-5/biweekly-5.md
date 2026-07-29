# PERTACOUSTIC — Laporan Biweekly 5

**Periode laporan:** Biweekly 5  
**Tanggal:** 30 Juli 2026  
**Status dokumen:** Rekayasa awal, bukan persetujuan manufaktur atau sertifikasi tekanan

## Daftar Isi

1. Rencana Tata Waktu dan Realisasi Pekerjaan
2. Ringkasan Kemajuan Pelaksanaan Pekerjaan
3. Deskripsi Kemajuan Pelaksanaan Pekerjaan
4. Rencana Pekerjaan Dua Minggu ke Depan
5. Daftar Pustaka

## 1. Rencana Tata Waktu dan Realisasi Pekerjaan

Laporan Biweekly 4 mencatat kemajuan kumulatif 20%. Pada Biweekly 5 dilakukan pekerjaan desain casing, penyaringan dimensi, pemodelan antarmuka HTI, dan analisis awal termal-struktural. Persentase kumulatif baru tidak ditetapkan karena bobot resmi pekerjaan belum dikonfirmasi oleh pengelola proyek.

## 2. Ringkasan Kemajuan Pelaksanaan Pekerjaan

- Dibuat konsep casing yang terhubung ke drat betina `7/16-20 UNF-2B` pada HTI-02-DHPC/D menggunakan adapter jantan nominal `7/16-20 UNF-2A`.
- Dibuat rute tiga konduktor dari feedthrough HTI menuju front-end analog, ADC PCM1808, STM32F411, dan ruang RTC/SD/daya.
- Stack material dasar ditetapkan sebagai Inconel 718–aerogel tersegel–PEEK.
- PA12/nylon tidak dipilih sebagai pressure housing; penggunaannya dibatasi untuk carrier, guide kabel, atau strain relief setelah grade material ditentukan.
- Dilakukan penyaringan OD 43, 50, dan 60 mm serta kandidat turunan. Diperoleh kandidat referensi yang lolos fit dan struktur, tetapi target termal satu jam belum tercapai.

## 3. Deskripsi Kemajuan Pelaksanaan Pekerjaan

### 3.1 Dasar Desain dan Batasan

Mechanical outline pemasok digunakan untuk konsep antarmuka. Dokumen tersebut bertanda *for reference only*, sehingga ukuran drat dan datum harus dikonfirmasi kepada HTI sebelum gambar manufaktur diterbitkan. Halaman produk HTI juga menjelaskan bahwa tipe preamplifier, endcap, kabel, dan filter dapat dikustomisasi [1]. Oleh karena itu, jalur tiga konduktor dipertahankan sampai mode current/voltage preamplifier dikonfirmasi.

Envelope sementara komponen adalah 55 × 22 × 12 mm untuk STM32F411 dan 52 × 32 × 18 mm untuk PCM1808. Setelah clearance 1,5 mm, kebutuhan diameter ruang bersih adalah 41 mm. Ukuran ini berasal dari informasi internet dan wajib diperiksa dengan jangka sorong pada komponen yang telah dibeli.

PCM1808 memiliki rentang operasi IC −40 sampai 85°C [2]. Nilai 85°C hanya dipakai sebagai batas penyaringan; target desain tetap 50°C, sedangkan 50–70°C dikategorikan bersyarat.

### 3.2 Konsep Mekanik, Drat, Seal, dan Kabel

![Model CAD casing dan HTI](figures/cad_assembly.png)

Adapter depan memiliki drat heliks nominal, lubang tiga konduktor, shoulder, spigot, dan ruang dua seal radial. Drat HTI hanya berfungsi sebagai retensi mekanik. Pressure boundary elektronik dibentuk oleh housing Inconel dan seal pada spigot yang terpisah. Jenis elastomer, backup ring, toleransi groove, dan extrusion gap belum dapat disahkan tanpa standar seal dan data fluida.

Tiga kabel diberi strain relief sebelum sambungan solder. ADC ditempatkan dekat sensor untuk meminimalkan panjang jalur analog. Shield dan ground termination disediakan secara konseptual, tetapi rangkaian front-end belum difinalkan karena mode preamplifier HTI belum diketahui.

### 3.3 Penempatan Elektronik dan Material

![Penampang dan penempatan elektronik](figures/longitudinal_section.png)

Urutan aksial yang dimodelkan adalah HTI → front-end analog → PCM1808 → STM32F411 → ruang RTC/SD/daya. Aerogel ditempatkan sepenuhnya di dalam pressure housing sehingga tidak menerima tekanan sumur atau kontak langsung dengan fluida.

Inconel 718 dipilih sebagai pressure shell awal. Data modulus dan sifat temperatur berasal dari bulletin Special Metals, tetapi nilai aktual tetap bergantung pada product form dan heat treatment [3]. PEEK 450G dipertahankan sebagai carrier karena kestabilan termal dan isolasi listriknya [4]. Nylon hanya menjadi alternatif carrier setelah grade, creep, penyerapan air, dan stabilitas dimensinya tersedia.

### 3.4 Penyaringan Geometri dan Struktur

| OD (mm) | Muat | Wall Inconel (mm) | Aerogel (mm) | Struktur | Keterangan |
|---:|---|---:|---:|---|---|
| 43 | Tidak | - | - | - | Insufficient radial space for 41 mm clear ID, PEEK, pressure wall, and aerogel. |
| 50 | Tidak | - | - | - | Insufficient radial space for 41 mm clear ID, PEEK, pressure wall, and aerogel. |
| 60 | Lolos | 5.25 | 2.25 | PASS | Lolos penyaringan geometri/struktur |

Kandidat referensi terkecil yang lolos fit dan struktur adalah **OD 60 mm**, dengan Inconel 5.25 mm, aerogel 2.25 mm, PEEK 2.0 mm, dan clear ID 41 mm. Hasil analitik Lamé memberikan tegangan ekuivalen 373.92 MPa dan faktor keamanan luluh 2.67. Penyaringan buckling silinder panjang menghasilkan faktor 2.26. Tidak ada kandidat aerogel padat sampai OD 80 mm yang memenuhi batas 70°C selama satu jam tanpa mengkreditkan massa termal elektronik yang belum terukur. Nilai ini adalah screening konservatif, bukan collapse rating tersertifikasi.

Perhitungan konservatif retensi drat menghasilkan faktor keamanan 6.58. Beban tersebut sengaja menganggap pressure thrust bekerja pada diameter drat, walaupun konsep aktual memisahkan drat HTI dari pressure boundary.

![Perbandingan struktur](figures/structural_comparison.png)

FEA mesh halus menghasilkan tegangan nodal maksimum 433.37 MPa dan perpindahan maksimum 0.0714 mm. Perubahan tegangan mesh medium-ke-fine adalah 2,76%, sedangkan perubahan perpindahan 0,53%. FEA menggunakan segmen shell representatif sepanjang 30 mm dengan tekanan pada permukaan luar dan gradien temperatur; endcap, kontak, dan seal belum dimodelkan. Tegangan nodal lokal dapat mengandung singularitas mesh; keputusan desain menggunakan perbandingan dengan solusi Lamé dan tren mesh, bukan satu puncak nodal saja.

### 3.5 Analisis Termal

![Riwayat temperatur](figures/thermal_history.png)

Model radial transient menggunakan temperatur awal 25°C, batas luar 150°C, durasi 1 jam, dan panas internal 0/1/2 W. Kandidat referensi mencapai **153.41°C pada 1 jam dan 1 W**, sehingga dikategorikan **redesign**. Hasil yang dapat melebihi 150°C berasal dari panas internal pada kondisi mendekati tunak; ini bukan kesalahan clipping.

![Trade-off termal](figures/thermal_tradeoff.png)

Model 3D CalculiX tanpa panas internal menghasilkan temperatur batas dalam 149.62°C setelah 1 jam. Model radial dan model 3D memiliki idealisasi berbeda; selisihnya dilaporkan dan tidak disembunyikan. Analisis ini belum memodelkan endcap heat bridge, kontak nyata, kabel, toleransi aerogel, atau distribusi daya elektronik terukur.

### 3.6 Konvergensi dan Keterbatasan

Studi radial menggunakan 12, 24, dan 48 sel total. Seluruh kandidat yang dilaporkan harus memiliki perubahan mesh menengah-ke-halus di bawah 5%. Model struktur CalculiX dijalankan dengan mesh coarse, medium, dan fine. File input, output solver, dan ringkasan disimpan pada folder `simulation/`.

Hasil belum mencakup massa termal aktual elektronik, uji kebocoran, fatigue, shock/vibration, respons akustik casing, sour-service qualification, toleransi manufaktur, atau proof pressure. Tidak ada klaim bahwa desain siap diproduksi. Simulasi juga menemukan kesalahan unit pada workflow lama: konduktivitas pernah dibagi 1.000. Kesalahan tersebut telah diperbaiki, sehingga hasil lama yang mendekati 25°C tidak digunakan.

## 4. Rencana Pekerjaan Dua Minggu ke Depan

- Ukur dimensi aktual STM32F411 dan PCM1808, termasuk header, jack, mounting hole, dan tinggi konektor.
- Konfirmasi drawing terkendali, mode preamplifier, pinout, kabel, dan detail endcap kepada HTI.
- Tentukan batas maksimum OD dan panjang tool dari kebutuhan sumur.
- Pilih grade aerogel, PEEK, seal, dan kondisi heat treatment Inconel yang dapat dibeli.
- Tambahkan massa termal aktual, endcap heat bridge, contact resistance, dan daya elektronik hasil pengukuran ke model termal.
- Bandingkan aerogel padat terhadap vacuum gap/thermal flask dan thermal-mass buffer karena stack padat saat ini gagal pada satu jam.
- Lakukan desain groove seal sesuai standar yang dipilih, tolerance stack-up, dan review manufaktur.
- Siapkan pressure test, leak test, thermal soak, dan pemeriksaan akustik setelah prototipe tersedia.

## 5. Daftar Pustaka

1. [High Tech Inc., HTI-02-DHPC/D](https://www.hightechincusa.com/products/hydrophones/hti02dhpc.html)
2. [Texas Instruments, PCM1808](https://www.ti.com/product/PCM1808)
3. [Special Metals, INCONEL Alloy 718 Technical Bulletin](https://www.specialmetals.com/documents/technical-bulletins/inconel/inconel-alloy-718.pdf)
4. [Victrex, PEEK 450G Technical Data Sheet](https://images.victrex.com/-/media/downloads/datasheets/victrex_tds_450g.pdf)
5. HTI-02-DHPC/D Mechanical Outline 02-001-25-00-00, dokumen pemasok, *for reference only*.

---

**Catatan:** Dokumen ini melaporkan hasil rekayasa awal yang dapat direproduksi. Semua ukuran internet, asumsi material, hasil simulasi, dan keputusan sementara dipisahkan dari data pemasok yang telah diverifikasi.
