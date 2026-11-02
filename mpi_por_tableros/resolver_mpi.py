"""Resuelve tableros independientes en paralelo con MPI."""

import argparse
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mpi4py import MPI

from mpi_common import leer_seeds, seleccionar_seeds
from sudoku import resolver_con_tiempo


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
    inicio = MPI.Wtime()
    tareas = [(nombre, tablero) for nombre, tablero in semillas]
    lotes = [tareas[rank::comunicador.Get_size()]
             for rank in range(comunicador.Get_size())]
    lote = comunicador.scatter(lotes if rank == 0 else None, root=0)

    resultados_locales = []
    for nombre, original in lote:
        resuelto, segundos = resolver_con_tiempo([fila[:] for fila in original])
        resultados_locales.append((nombre, resuelto, segundos))
    resultados = comunicador.gather(resultados_locales, root=0)

    if rank == 0:
        total = MPI.Wtime() - inicio
        por_id = {
            nombre: (resuelto, segundos)
            for lote_resultados in resultados
            for nombre, resuelto, segundos in lote_resultados
        }
        for nombre, _ in semillas:
            resuelto, segundos = por_id[nombre]
            print(f"\nID: {nombre}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {segundos:.6f} segundos", flush=True)
        print(f"\nTableros procesados: {len(por_id)}")
        print(f"Tiempo total MPI: {total:.6f} segundos")


if __name__ == "__main__":
    main()
