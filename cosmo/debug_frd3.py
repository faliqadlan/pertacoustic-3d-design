lines = []
with open("casing_iter1.frd", "r") as f:
    for line in f:
        if line.strip() == "3":
            print(f"Found '3' at: {line.rstrip()}")
            break
