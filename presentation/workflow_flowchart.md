sequenceDiagram
    actor User as Konteks Pengguna
    participant Agent as Agentic Loop

    User->>+Agent: Menentukan batasan (suhu & durasi waktu)
    
    loop Agentic Loop (Hingga Target Tercapai)
        Agent->>Agent: Membuat Model CAD
        Agent->>Agent: Menjalankan Simulasi CAE (menggunakan File STEP)
        Agent->>Agent: Penalaran dan Evaluasi (Data Simulasi)
    end
    
    Agent-->>-User: Menyerahkan Laporan Akhir dan File Pendukung
