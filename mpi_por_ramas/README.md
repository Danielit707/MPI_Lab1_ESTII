# MPI por ramas

El coordinador procesa los IDs en el orden del archivo y no empieza el
siguiente tablero hasta que termina el actual. Para cada tablero, crea tareas
con los valores válidos de la primera casilla vacía. Los demás procesos exploran
esas ramas en paralelo con backtracking; si aparece una solución, se solicita a
los trabajadores activos que cancelen su búsqueda.

## Ejecutar con Docker en Windows (PowerShell)

Abre Docker Desktop y espera a que indique que el motor está en ejecución. Desde
la carpeta raíz del proyecto, usa `N=8` recomendado para este equipo. Si
calibras en otro equipo, reemplaza el valor por el recomendado allí:

```powershell
$N = 8
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_por_ramas/resolver_mpi.py --all
```

Para resolver solo un ID:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_por_ramas/resolver_mpi.py --id 7
```

Se puede indicar otro archivo con `--archivo /app/mi_archivo.txt`. La salida
muestra el tiempo parcial por tablero y el tiempo total de la ejecución MPI.
