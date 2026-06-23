import sys
lines = []
with open("casing_iter1.frd", "r") as f:
    for i in range(1, 206565):
        line = f.readline()
        if i >= 206555:
            lines.append(line)
        
for i, line in enumerate(lines):
    print(f"Line {i}: {repr(line)}")
