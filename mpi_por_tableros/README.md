# MPI por tableros

Cada tablero es una tarea independiente. Los procesos reciben IDs en orden
alternado (por ejemplo, con cuatro procesos, los lotes empiezan por 1, 2, 3 y
4) y el proceso coordinador reúne y muestra los resultados en el orden original.
El tiempo total MPI incluye el reparto, la resolución y la reunión de resultados;
los tiempos parciales son los de búsqueda de cada tablero.

## Ejecutar con Docker en Windows (PowerShell)

Abre Docker Desktop y espera a que indique que el motor está en ejecución. Desde
la carpeta raíz del proyecto, usa `N=8` recomendado para este equipo. Si
calibras en otro equipo, reemplaza el valor por el recomendado allí:

```powershell
$N = 8
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_por_tableros/resolver_mpi.py --all
```

Para resolver solo un ID:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_por_tableros/resolver_mpi.py --id 7
```

Se puede indicar otro archivo con `--archivo /app/mi_archivo.txt`.
