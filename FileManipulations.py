import sys
import os
import os.path
import glob

def ReplaceInAllFileNames(dir, srcStr, trgtStr):
	if os.path.isdir(dir):
		dir = os.path.join(dir, '*.*')

	listFiles = glob.glob(dir)
	if len(listFiles) == 0:
		print("No files in " + dir)
		sys.exit()

	for file in listFiles:
		ext = os.path.splitext(file)[1]
		base = os.path.splitext(file)[0]

		newBase = base.replace(srcStr, trgtStr)

		src = os.path.abspath(os.path.join(dir, file))
		trgt = os.path.abspath(os.path.join(dir, newBase + ext))

		os.rename(src, trgt)

def main():
	if len(sys.argv) < 2:
		print('Missing directory.\n')
		print('usage: ReplaceInAllFiles.py <directoy> <look-for> <replace-with>')
		sys.exit()

	dir = sys.argv[1]

	if len(sys.argv) < 3:
		print('Missing string to replace.\n')
		print('usage: ReplaceInAllFiles.py <directoy> <look-for> <replace-with>')
		sys.exit()

	srcStr = sys.argv[2]
	trgtStr = ''

	if len(sys.argv) > 3:
		trgtStr = sys.argv[3]

	ReplaceInAllFileNames(dir, srcStr, trgtStr)

if __name__ == "__main__":
    main()