import os
import subprocess
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1 :]


def main():
    python = os.path.realpath(sys.executable)
    run = subprocess.run([python] + argv)
    if run.returncode != 0:
        print(f"Error: {run.returncode}")
        sys.exit(run.returncode)


if __name__ == "__main__":
    main()
