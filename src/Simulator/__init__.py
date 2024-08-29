import os
import sys

ran = False
Simulator = None


def main():
    __folder = os.path.dirname(__file__)
    __library = os.path.join(__folder, "lib")

    if not os.path.exists(__library):
        import subprocess

        try:
            import ziglang
        except ImportError:
            raise ImportError(
                "Ziglang is required to build the simulator library. Please install ziglang"
            )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "ziglang",
                "build",
                "-p",
                ".",
                "--release=fast",
            ],
            cwd=__folder,
        )

    sys.path.append(__library)
    import libSim

    global Simulator
    Simulator = libSim.Simulator
    sys.path.pop()


if not ran:
    main()
    ran = True
