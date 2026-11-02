# MPI híbrido: tableros y ramas

Se crean `min(max(1, N // 2), cantidad_de_tableros)` grupos. Los procesos se
distribuyen equilibradamente en esos grupos y los IDs se asignan entre grupos
en orden alternado. Cada grupo resuelve sus tableros secuencialmente y usa al
menos dos procesos para explorar ramas en paralelo cuando `N >= 2`. Con `N=1`
solo hay un grupo y la búsqueda es secuencial.

## Ejecutar con Docker en Windows (PowerShell)

Abre Docker Desktop y espera a que indique que el motor está en ejecución. Desde
la carpeta raíz del proyecto, usa `N=8` recomendado para este equipo. Si
calibras en otro equipo, reemplaza el valor por el recomendado allí:

```powershell
$N = 8
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_hibrido/resolver_mpi.py --all
```

Para resolver solo un ID:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n $N python /app/mpi_hibrido/resolver_mpi.py --id 7
```

Se puede indicar otro archivo con `--archivo /app/mi_archivo.txt`. La salida
muestra el estado y tiempo parcial de cada tablero, además del tiempo total MPI.
