import os
import subprocess
import sys


def main():
    argv = sys.argv
    argv = argv[argv.index("--") + 1 :]
    python = os.path.realpath(sys.executable)
    run = subprocess.run([python] + argv, check=False)
    if run.returncode != 0:
        print(f"Error: {run.returncode}")
        sys.exit(run.returncode)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, OSError, subprocess.SubprocessError) as e:
        # ValueError covers a missing "--" separator in the arguments, while the
        # OS and subprocess errors cover failures launching the interpreter
        print(f"Error: {e}")
        sys.exit(1)
