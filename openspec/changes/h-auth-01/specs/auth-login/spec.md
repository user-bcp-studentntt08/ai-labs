## ADDED Requirements

### Requirement: Credenciales tratadas como datos
El sistema SHALL tratar `username` y `password` de `POST /auth/login` exclusivamente como valores de datos: ningún contenido de esos campos SHALL alterar la estructura de la consulta que busca al usuario.

#### Scenario: Inyección en el usuario
- **WHEN** se envía `POST /auth/login` con `username` igual a `' OR '1'='1` y un `password` cualquiera
- **THEN** la respuesta es `401`
- **AND** el cuerpo no contiene `token`

#### Scenario: Inyección en la contraseña
- **WHEN** se envía `POST /auth/login` con `username` igual a `student` y `password` igual a `' OR '1'='1`
- **THEN** la respuesta es `401`
- **AND** el cuerpo no contiene `token`

#### Scenario: Inyección en ambos campos
- **WHEN** se envía `POST /auth/login` con `username` y `password` iguales a `' OR '1'='1`
- **THEN** la respuesta es `401`
- **AND** el cuerpo no contiene `token`

### Requirement: Login válido preservado
El sistema SHALL seguir autenticando con credenciales válidas y devolviendo el mismo formato de respuesta exitosa.

#### Scenario: Usuario del taller
- **WHEN** se envía `POST /auth/login` con `username` igual a `student` y `password` igual a `Workshop123!`
- **THEN** la respuesta es `200`
- **AND** `user.username` es `student`
- **AND** `token` está presente
- **AND** el cuerpo conserva `expiresIn`, `user.displayName`, `user.role` y `debug`

#### Scenario: Contraseña incorrecta
- **WHEN** se envía `POST /auth/login` con `username` igual a `student` y una contraseña que no coincide
- **THEN** la respuesta es `401`
- **AND** el cuerpo no contiene `token`

### Requirement: Validación de entrada preservada
El sistema SHALL seguir rechazando con `400` las solicitudes sin cuerpo, sin `username` o sin `password`, sin consultar usuarios.

#### Scenario: Usuario vacío
- **WHEN** se envía `POST /auth/login` con `username` vacío o ausente
- **THEN** la respuesta es `400` con `message` igual a `Username is required`

#### Scenario: Contraseña vacía
- **WHEN** se envía `POST /auth/login` con `username` válido y `password` vacío o ausente
- **THEN** la respuesta es `400` con `message` igual a `Password is required`

### Requirement: Intento de inyección cubierto por pruebas
La suite de pruebas de `auth/` SHALL incluir en `AuthResourceTest` al menos una prueba del intento de inyección SQL en `POST /auth/login`, y SHALL pasar con `mvn test` ejecutado desde `auth/`.

#### Scenario: Suite de auth
- **WHEN** se ejecuta `mvn test` desde `auth/`
- **THEN** `AuthResourceTest` incluye la prueba del intento de inyección
- **AND** todas las pruebas pasan
