"""Resuelve los tableros en orden y paraleliza las ramas de cada uno."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mpi4py import MPI

from mpi_common import leer_seeds, resolver_por_ramas, seleccionar_seeds


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--archivo",
        type=Path,
        default=ROOT / "seeds.txt",
        help="archivo de seeds (por defecto: seeds.txt del proyecto)")
    seleccion = parser.add_mutually_exclusive_group()
    seleccion.add_argument("--id", help="resolver solo la seed con este ID")
    seleccion.add_argument("--all", action="store_true", help="resolver todos los IDs")
    args = parser.parse_args()

    comunicador = MPI.COMM_WORLD
    rank = comunicador.Get_rank()
    try:
        semillas = seleccionar_seeds(leer_seeds(args.archivo), args.id)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    comunicador.Barrier()
    inicio_total = MPI.Wtime()
    for nombre, original in semillas:
        resuelto, segundos = resolver_por_ramas(comunicador, original)
        if rank == 0:
            print(f"\nID: {nombre}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {segundos:.6f} segundos", flush=True)

    if rank == 0:
        print(f"\nTiempo total MPI: {MPI.Wtime() - inicio_total:.6f} segundos")


if __name__ == "__main__":
    main()
