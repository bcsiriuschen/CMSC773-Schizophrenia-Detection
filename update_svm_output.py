import sys
for line in open(sys.argv[1]):
    print float(line.strip()) - 0.5 + 0.000000001