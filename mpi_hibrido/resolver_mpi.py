"""Reparte tableros entre grupos y ramas dentro de cada grupo."""

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

    mundo = MPI.COMM_WORLD
    rank = mundo.Get_rank()
    try:
        semillas = seleccionar_seeds(leer_seeds(args.archivo), args.id)
    except (OSError, ValueError) as error:
        parser.error(str(error))

    cantidad_grupos = min(max(1, mundo.Get_size() // 2), len(semillas))
    grupo_id = rank % cantidad_grupos
    grupo = mundo.Split(color=grupo_id, key=rank)
    tableros_grupo = semillas[grupo_id::cantidad_grupos]

    mundo.Barrier()
    inicio_total = MPI.Wtime()
    resultados_locales = []
    for nombre, original in tableros_grupo:
        resuelto, segundos = resolver_por_ramas(grupo, original)
        if grupo.Get_rank() == 0:
            resultados_locales.append((nombre, resuelto, segundos))

    resultados_grupos = mundo.gather(
        resultados_locales if grupo.Get_rank() == 0 else [], root=0)
    if rank == 0:
        tiempo_total = MPI.Wtime() - inicio_total
        por_id = {
            nombre: (resuelto, segundos)
            for resultados_grupo in resultados_grupos
            for nombre, resuelto, segundos in resultados_grupo
        }
        for nombre, _ in semillas:
            resuelto, segundos = por_id[nombre]
            print(f"\nID: {nombre}")
            print("Resuelto" if resuelto else "Sin solución")
            print(f"Tiempo parcial: {segundos:.6f} segundos", flush=True)
        print(f"\nTableros procesados: {len(por_id)}")
        print(f"Tiempo total MPI: {tiempo_total:.6f} segundos")


if __name__ == "__main__":
    main()
