graph TD
    classDef userClass fill:#E3F2FD,stroke:#1565C0,stroke-width:2px,color:#000
    classDef agentClass fill:#E8F5E9,stroke:#2E7D32,stroke-width:2px,color:#000

    subgraph User Context
        A[User specifies constraints like temperature and time duration]:::userClass
        H[Receives Final Report and Supplementary Files]:::userClass
    end

    subgraph COSMO Agent
        B[Generates CAD Model]:::agentClass
        C[Runs CAE Simulation]:::agentClass
        D[Intelligent Reasoning Evaluate and Refactor]:::agentClass
    end

    A -->|Initiates Task| B
    B -->|STEP File| C
    C -->|Simulation Data| D
    D -->|Target Not Met| B
    D -->|Optimization Complete| H
