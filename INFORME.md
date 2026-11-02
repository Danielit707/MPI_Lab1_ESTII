# Informe de resultados

Se ejecutaron tres mediciones por caso en Windows con Docker Desktop, usando el
mismo `seeds.txt` y el contenedor `augustosalazar/slim-mpi:2` (Open MPI 4.1.4).
Los tiempos MPI son los informados por el programa desde el reparto del trabajo
hasta reunir los resultados; no incluyen el arranque de Docker.

## Entorno y calibración

- Equipo: Windows con Docker Desktop; el contenedor reportó `nproc=8`
- Versión del contenedor: `augustosalazar/slim-mpi:2` (Open MPI 4.1.4)
- Cantidad de repeticiones por ejecución: 3
- `N` recomendado por el calibrador: 8 (mediana del calibrador: 2,013 s)

El calibrador probó `N=1` a `N=8`; el mejor valor mediano fue `N=8`.
Comando usado en Windows, desde la raíz del proyecto:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 python /app/detectar_procesos_mpi.py
```

Usa ese mismo `N` para las tres implementaciones MPI. El calibrador ejecuta
tres mediciones por cada cantidad de procesos y recomienda la de menor mediana.

## Mediciones

Cada comando se ejecutó tres veces. Para la versión serial se tomó el
`Tiempo total`; para MPI, `Tiempo total MPI`. La tabla muestra las medianas.

| Implementación | Caso | Procesos | Mediana del tiempo total (s) | Aceleración frente a secuencial |
| --- | --- | ---: | ---: | ---: |
| Secuencial | Todos los IDs | 1 | 151,545 | 1,00 |
| MPI por tableros | Todos los IDs | 8 | 45,088 | 3,36 |
| MPI por ramas | Todos los IDs, uno después de otro | 8 | 127,864 | 1,19 |
| MPI híbrido | Todos los IDs | 8 | 76,085 | 1,99 |

Tiempos de las tres ejecuciones, en segundos:

| Implementación | Ejecución 1 | Ejecución 2 | Ejecución 3 |
| --- | ---: | ---: | ---: |
| Secuencial | 155,691 | 148,785 | 151,545 |
| MPI por tableros | 47,877 | 42,011 | 45,088 |
| MPI por ramas | 127,864 | 132,615 | 119,932 |
| MPI híbrido | 85,906 | 74,813 | 76,085 |

Comandos de Windows PowerShell usados, desde la raíz del proyecto:

```powershell
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 python /app/baseline_secuencial.py --all
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_tableros/resolver_mpi.py --all
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_por_ramas/resolver_mpi.py --all
docker run --rm -v "${PWD}:/app" augustosalazar/slim-mpi:2 mpiexec --allow-run-as-root --use-hwthread-cpus --oversubscribe -n 8 python /app/mpi_hibrido/resolver_mpi.py --all
```

Calcula cada aceleración como `mediana secuencial / mediana MPI`.

## Conclusiones

- **Mejor estrategia:** repartir tableros, con 45,088 s frente a 151,545 s en
  serie: aceleración de 3,36x y reducción del tiempo de 70,2 %. La híbrida tardó
  76,085 s (1,99x); la de ramas, 127,864 s (1,19x).
- **Comunicación y balance:** repartir tableros ofrece tareas independientes y
  necesita poca comunicación, por lo que mantiene ocupados varios procesos. La
  asignación alternada distribuye el costo desigual de los IDs. La variante por
  ramas procesa los tableros uno por uno y paga coordinación y cancelación para
  cada tablero; dividir las primeras opciones tampoco garantiza ramas de igual
  costo. La combinación reduce parte de la serialización, pero conserva la
  coordinación de ramas dentro de cada grupo.
- **Comparación:** en estas mediciones, repartir tableros fue la opción más
  eficaz; el híbrido quedó en segundo lugar y repartir ramas obtuvo la menor
  mejora. Los resultados dependen del equipo y de la distribución de trabajo.
