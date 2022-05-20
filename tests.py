from pathlib import Path 

path = Path()
for file in path.rglob("*"):
	print(file.parent)

