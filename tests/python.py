import os
import subprocess
import sys


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :]
    python = os.path.realpath(sys.executable)
    run = subprocess.run([python] + argv)
    if run.returncode != 0:
        print(f"Error: {run.returncode}")
        sys.exit(run.returncode)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
