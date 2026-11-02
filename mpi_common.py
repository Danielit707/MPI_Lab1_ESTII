"""Utilidades compartidas por las implementaciones MPI."""

from pathlib import Path


def leer_seeds(ruta):
    """Lee y valida líneas con formato id|81 caracteres."""
    seeds = {}
    for numero_linea, texto in enumerate(
            Path(ruta).read_text(encoding="utf-8").splitlines(), start=1):
        texto = texto.strip()
        if not texto or texto.startswith("#"):
            continue
        if "|" not in texto:
            raise ValueError(f"línea {numero_linea}: falta el separador '|'")
        identificador, contenido = texto.split("|", 1)
        identificador = identificador.strip()
        contenido = contenido.strip().replace(".", "0")
        if not identificador:
            raise ValueError(f"línea {numero_linea}: el ID está vacío")
        if identificador in seeds:
            raise ValueError(f"línea {numero_linea}: ID duplicado '{identificador}'")
        if len(contenido) != 81 or any(c not in "0123456789" for c in contenido):
            raise ValueError(
                f"línea {numero_linea}: el tablero debe tener 81 dígitos, 0 o '.'")
        celdas = [int(c) for c in contenido]
        seeds[identificador] = [celdas[i:i + 9] for i in range(0, 81, 9)]
    if not seeds:
        raise ValueError(f"no se encontraron seeds en {ruta}")
    return seeds


def seleccionar_seeds(seeds, identificador):
    """Devuelve las seeds solicitadas conservando el orden del archivo."""
    if identificador is None:
        return list(seeds.items())
    if identificador not in seeds:
        disponibles = ", ".join(seeds)
        raise ValueError(f"ID '{identificador}' no existe. Disponibles: {disponibles}")
    return [(identificador, seeds[identificador])]


def _crear_ramas(tablero):
    for fila in range(9):
        for columna in range(9):
            if tablero[fila][columna] == 0:
                from sudoku import puede_colocar

                ramas = []
                for valor in range(1, 10):
                    if puede_colocar(tablero, fila, columna, valor):
                        rama = [r[:] for r in tablero]
                        rama[fila][columna] = valor
                        ramas.append(rama)
                return ramas
    return [[fila[:] for fila in tablero]]


def _resolver_rama(tablero, cancelada):
    from sudoku import puede_colocar

    def buscar():
        if cancelada():
            return False
        for fila in range(9):
            for columna in range(9):
                if tablero[fila][columna] != 0:
                    continue
                for valor in range(1, 10):
                    if puede_colocar(tablero, fila, columna, valor):
                        tablero[fila][columna] = valor
                        if buscar():
                            return True
                        tablero[fila][columna] = 0
                return False
        return True

    return buscar()


def resolver_por_ramas(comunicador, tablero):
    """Distribuye las opciones de la primera casilla vacía por el comunicador."""
    from mpi4py import MPI

    rank = comunicador.Get_rank()
    cantidad = comunicador.Get_size()
    if cantidad == 1:
        from sudoku import resolver_con_tiempo

        return resolver_con_tiempo([fila[:] for fila in tablero])

    inicio = MPI.Wtime()
    ramas = _crear_ramas(tablero) if rank == 0 else None
    ramas = comunicador.bcast(ramas, root=0)

    tag_trabajo = 31
    tag_resultado = 32
    tag_cancelar = 33
    tag_finalizado = 34

    if rank != 0:
        while True:
            indice = comunicador.recv(source=0, tag=tag_trabajo)
            if indice is None:
                estado = MPI.Status()
                if comunicador.Iprobe(source=0, tag=tag_cancelar, status=estado):
                    comunicador.recv(source=0, tag=tag_cancelar)
                break

            detener = False

            def cancelada():
                nonlocal detener
                if comunicador.Iprobe(source=0, tag=tag_cancelar):
                    comunicador.recv(source=0, tag=tag_cancelar)
                    detener = True
                return detener

            solucion = [fila[:] for fila in ramas[indice]]
            resuelto = _resolver_rama(solucion, cancelada)
            if detener:
                break
            comunicador.send(
                (resuelto, solucion if resuelto else None),
                dest=0,
                tag=tag_resultado)
        comunicador.send(None, dest=0, tag=tag_finalizado)
        return False, 0.0

    trabajadores = set(range(1, cantidad))
    activos = set()
    finalizados = set()
    siguiente = 0
    solucion = None

    for trabajador in trabajadores:
        if siguiente < len(ramas):
            comunicador.send(siguiente, dest=trabajador, tag=tag_trabajo)
            activos.add(trabajador)
            siguiente += 1
        else:
            comunicador.send(None, dest=trabajador, tag=tag_trabajo)

    while len(finalizados) < len(trabajadores):
        estado = MPI.Status()
        if comunicador.Iprobe(source=MPI.ANY_SOURCE, tag=tag_resultado, status=estado):
            trabajador = estado.Get_source()
            resuelto, candidata = comunicador.recv(
                source=trabajador, tag=tag_resultado)
            activos.discard(trabajador)
            if resuelto and solucion is None:
                solucion = candidata
                for ocupado in activos:
                    comunicador.send(None, dest=ocupado, tag=tag_cancelar)
                activos.clear()

            if solucion is not None:
                comunicador.send(None, dest=trabajador, tag=tag_trabajo)
            elif siguiente < len(ramas):
                comunicador.send(siguiente, dest=trabajador, tag=tag_trabajo)
                activos.add(trabajador)
                siguiente += 1
            else:
                comunicador.send(None, dest=trabajador, tag=tag_trabajo)
        elif comunicador.Iprobe(
                source=MPI.ANY_SOURCE, tag=tag_finalizado, status=estado):
            trabajador = estado.Get_source()
            comunicador.recv(source=trabajador, tag=tag_finalizado)
            finalizados.add(trabajador)

    segundos = MPI.Wtime() - inicio
    return solucion is not None, segundos
