import os
import sys

from typing import List, Dict
from common import DeliveryAgentInfo, Parcel, Id
from node import Node

ran = False


class Simulator:
    def __init__(self, node: Node, all_parcels: List[Parcel]) -> None: ...
    def set_parcels(self, parcels: List[Parcel]) -> None: ...
    def simulate(
        self, agent_allocations: List[Dict[DeliveryAgentInfo, List[Id]]]
    ) -> None: ...


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
