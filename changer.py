import sys

target_filename = sys.argv[1]
source_filename = sys.argv[2]

with open(target_filename, 'w') as target:
    with open(source_filename, 'r') as source:
        target.write(source.read())
