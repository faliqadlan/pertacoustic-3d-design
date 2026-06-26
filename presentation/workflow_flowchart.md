sequenceDiagram
    actor User as User Context
    participant Agent as Agentic Loop

    User->>+Agent: Specifies constraints (temp & time duration)
    
    loop Agentic Loop (Until Target is Met)
        Agent->>Agent: Generates CAD Model
        Agent->>Agent: Runs CAE Simulation (using STEP File)
        Agent->>Agent: Reasoning and Evaluate (Simulation Data)
    end
    
    Agent-->>-User: Delivers Final Report and Supplementary Files
