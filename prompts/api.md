AMBITO

Workspace ai-labs abierto en su raíz. Lee código solo en api/.

Todas las rutas parten de la raíz. Lee [README.md](http://README.md), [RETO.md](http://RETO.md) y docs/ generales.

Este pedido es de solo lectura; no escribas archivos ni ejecutes pruebas o

comandos. Git, si fuera necesario consultarlo, se ejecuta desde la raíz; las

pruebas propuestas usan cwd api/.

No leas ni modifiques código de auth/ ni web/. Usa IDs H-API-NN y componente api.

CONTEXTO

La API usa FastAPI y SQLite. Lee docs/[ENDPOINTS.md](http://ENDPOINTS.md) si existe. Localiza las

rutas HTTP relevantes hasta las consultas SQLite, incluyendo filtros y

operaciones de creación. No des por cierta la lista de [RETO.md](http://RETO.md) ni presupongas

que solo un endpoint está afectado.

OBJETIVO

Determinar si entradas de las peticiones llegan concatenadas a consultas SQL

y si las consultas usan parámetros.

RESTRICCIONES

No edites código ni ejecutes pruebas, comandos o ataques contra servicios

remotos. Usa solo código y datos ficticios locales. Si falta un archivo o no

puedes comprobar algo, dilo. No cambies contratos ni leas otros componentes.

CRITERIOS DE ACEPTACIÓN

Identifica el recorrido de cada entrada relevante desde la ruta HTTP hasta la

consulta, con archivo y línea.

Distingue concatenación, parametrización y cualquier caso no comprobado.

Propón pruebas locales para una petición válida, una inválida y una entrada

con comilla. Considera el token de autorización y los campos o filtros que

lleguen a SQL; indica el resultado esperado según el contrato observado.

No afirmes que una prueba pasó si solo la propusiste.

FORMATO DE RESPUESTA

Tabla: afirmación | evidencia archivo:línea | comprobado o hipótesis |

prueba propuesta.

Termina con preguntas abiertas y comandos no ejecutados.