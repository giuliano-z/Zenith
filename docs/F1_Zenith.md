# F1 — Software Requirements Specification: Zenith

**Versión:** 1.0 · Mayo 2026  
**Autor:** Giuliano Zulatto  
**Metodología:** GZSM v1.1  
**Estado:** F1 cerrado — Graduado a F2  
**Basado en:** IEEE 830-1998 (adaptado) · ISO/IEC 25010 · OWASP Top 10 (2021) · Ley 25.326

---

## 1. Introducción

### 1.1 Propósito

Este documento especifica los requerimientos funcionales y no funcionales del sistema **Zenith**, una aplicación web de gestión financiera personal diseñada nativamente para el contexto argentino. Está dirigido al desarrollador (Giuliano Zulatto) como guía de construcción y como artefacto de portfolio técnico.

### 1.2 Alcance

Zenith permite a uno o dos usuarios registrar y visualizar transacciones financieras, gestionar múltiples cuentas en pesos y dólares, registrar compras en cuotas y gestionar gastos compartidos entre dos personas. El sistema es self-hosteable, de código abierto (AGPL) y no requiere infraestructura de terceros más allá del servidor de deploy.

**No incluye en el MVP:** módulo de inversiones, IA, bot de Telegram, exportación PDF, módulo de patrimonio neto, integración automática con Mercado Pago, usuarios externos, modelo de monetización.

### 1.3 Definiciones y abreviaciones

| Término | Definición |
|---|---|
| ARS | Peso argentino |
| USD | Dólar estadounidense |
| Cuota | Pago diferido en N cuotas con monto fijo por cuota al momento del registro |
| Gasto compartido | Transacción cuyo monto se divide entre los dos usuarios registrados en el sistema |
| Tipo de cambio | Valor de conversión USD/ARS definido manualmente por el usuario con fecha de vigencia |
| Categoría | Etiqueta semántica asignada a una transacción (ej: Alimentación, Transporte) |
| Balance | Saldo neto de una cuenta o del sistema completo en un momento dado |
| MVP | Producto mínimo viable: conjunto de RF clasificados Must Have |
| TC | Tipo de cambio |
| RF | Requerimiento Funcional |
| RNF | Requerimiento No Funcional |
| RS | Requerimiento de Seguridad |
| SPA | Single Page Application |

### 1.4 Referencias

- F0 Problem Statement: Zenith v1.0 (Mayo 2026)
- GZSM v1.1 — Giuliano Zulatto
- IEEE 830-1998 (adaptado)
- ISO/IEC 25010:2011
- OWASP Top 10 (2021)
- Ley 25.326 — Protección de Datos Personales (Argentina)
- Clean Architecture — R.C. Martin

---

## 2. Descripción general

### 2.1 Perspectiva del producto

Zenith es una aplicación web standalone, self-hosteable. No depende de integraciones externas obligatorias en el MVP. El frontend es una SPA. El backend expone una API REST. La base de datos es relacional.

El sistema soporta exactamente **dos usuarios** en el MVP: el usuario principal (Giuliano) y un usuario secundario (su novia). No hay registro público ni invitaciones desde el frontend.

El stack técnico es agnóstico en este documento y se decide formalmente en F2. La arquitectura backend + frontend desacoplado está asumida.

### 2.2 Funciones principales

- Gestión de cuentas en ARS y/o USD por usuario
- Registro de transacciones (ingreso, gasto, transferencia entre cuentas propias)
- Registro de compras en cuotas con monto fijo por cuota
- Categorización de gastos con categorías predefinidas y personalizadas
- Dashboard financiero con resumen mensual y gráficos
- Gestión de gastos compartidos entre los dos usuarios del sistema
- Tipo de cambio ARS/USD configurable manualmente con historial

### 2.3 Usuarios del sistema

| Rol | Descripción |
|---|---|
| **Usuario principal** | Giuliano. Acceso completo a sus cuentas y transacciones. Puede crear y resolver gastos compartidos. Setup inicial del sistema. |
| **Usuario secundario** | La novia. Acceso completo a sus propias cuentas y transacciones. Puede ver y resolver gastos compartidos con el usuario principal. |

Ambos roles tienen las mismas capacidades dentro de sus propios datos. El "usuario principal" solo se distingue en que realiza el setup inicial (creación de usuarios en el primer boot).

### 2.4 Restricciones generales

- El sistema soporta máximo 2 usuarios en el MVP.
- El tipo de cambio USD/ARS es ingresado manualmente; no hay integración automática con ninguna API en el MVP.
- La aplicación no procesa pagos ni interactúa con Mercado Pago, BCRA ni AFIP en el MVP.
- Las cuotas tienen monto fijo por cuota (sin ajuste automático por inflación en el MVP).
- No hay notificaciones push, email ni alertas proactivas en el MVP.

---

## 3. Requerimientos Funcionales

### Módulo AUTH — Autenticación y usuarios

---

**RF-001: Registro de usuario**

```
Descripción:    El sistema debe permitir registrar un usuario con email,
                nombre y contraseña. En el MVP, el registro es manual
                (no hay formulario público de signup).
Actor:          Administrador del sistema / setup inicial
Precondición:   No existe ningún usuario con ese email en el sistema.
Postcondición:  El usuario queda creado con contraseña hasheada.
                Está listo para autenticarse.

Criterio de aceptación:
  Dado que no existe ningún usuario con el email "giuliano@zenith.app",
  cuando se crea el usuario con nombre "Giuliano", email y contraseña válidos,
  entonces el sistema responde 201, el hash de contraseña se almacena
  (nunca el texto plano) y el usuario puede autenticarse con esas credenciales.

Prioridad MoSCoW: Must Have
Dependencias:    —
```

---

**RF-002: Login**

```
Descripción:    El sistema debe permitir que un usuario autenticado inicie
                sesión con email y contraseña para obtener acceso a la API.
Actor:          Usuario principal / Usuario secundario
Precondición:   El usuario existe y está activo en el sistema.
Postcondición:  El sistema devuelve un token de acceso válido. El usuario
                puede acceder a todos los endpoints protegidos.

Criterio de aceptación:
  Dado un usuario registrado,
  cuando envía email y contraseña correctos al endpoint de login,
  entonces el sistema responde 200 con un token JWT de acceso válido
  y el usuario puede llamar endpoints protegidos con ese token.

  Dado un usuario registrado,
  cuando envía una contraseña incorrecta,
  entonces el sistema responde 401 con mensaje genérico que no revela
  si el email existe o si solo la contraseña es incorrecta.

Prioridad MoSCoW: Must Have
Dependencias:    RF-001
```

---

**RF-003: Logout**

```
Descripción:    El sistema debe permitir que el usuario invalide su token
                de acceso activo.
Actor:          Usuario autenticado
Precondición:   El usuario tiene una sesión activa.
Postcondición:  El token queda invalidado. Cualquier request posterior
                con ese token recibe HTTP 401.

Criterio de aceptación:
  Dado un usuario con token activo,
  cuando llama al endpoint de logout con ese token,
  entonces el sistema responde 200 y cualquier request posterior
  con ese mismo token devuelve 401.

Prioridad MoSCoW: Must Have
Dependencias:    RF-002
```

---

**RF-004: Cambio de contraseña**

```
Descripción:    El sistema debe permitir que el usuario actualice su
                contraseña proveyendo la contraseña actual y la nueva.
Actor:          Usuario autenticado
Precondición:   El usuario está autenticado.
Postcondición:  La contraseña queda actualizada con el nuevo hash.
                Las sesiones previas quedan invalidadas.

Criterio de aceptación:
  Dado un usuario autenticado que provee su contraseña actual correcta
  y una nueva contraseña de al menos 8 caracteres,
  cuando envía el request de cambio,
  entonces el sistema responde 200, actualiza el hash
  y el token anterior deja de ser válido.

  Dado que la contraseña actual provista es incorrecta,
  cuando se envía el request,
  entonces el sistema responde 400 sin actualizar nada.

Prioridad MoSCoW: Should Have
Dependencias:    RF-002
```

---

### Módulo ACCOUNTS — Cuentas

---

**RF-005: Crear cuenta**

```
Descripción:    El sistema debe permitir que el usuario cree una cuenta
                financiera especificando nombre, tipo y moneda.
Actor:          Usuario autenticado
Precondición:   El usuario está autenticado.
Postcondición:  La cuenta queda creada con balance = balance inicial (default 0)
                y pertenece exclusivamente al usuario creador.

Tipos válidos: cash (efectivo), digital_wallet (billetera digital),
               bank (cuenta bancaria), savings (caja de ahorro).
Monedas válidas: ARS, USD.

Criterio de aceptación:
  Dado un usuario autenticado,
  cuando crea una cuenta con nombre "Mercado Pago", tipo "digital_wallet",
  moneda "ARS" y balance inicial $5.000,
  entonces el sistema responde 201, la cuenta aparece en el listado
  del usuario con balance $5.000 y no es visible para el otro usuario.

Prioridad MoSCoW: Must Have
Dependencias:    RF-001
```

---

**RF-006: Listar cuentas**

```
Descripción:    El sistema debe devolver todas las cuentas activas del
                usuario autenticado con su balance calculado al momento
                de la consulta.
Actor:          Usuario autenticado
Precondición:   El usuario está autenticado.
Postcondición:  —

Criterio de aceptación:
  Dado un usuario con 3 cuentas activas (ARS y USD),
  cuando solicita el listado,
  entonces el sistema devuelve exactamente esas 3 cuentas con nombre,
  tipo, moneda y balance actual calculado.
  Las cuentas del otro usuario no aparecen en el resultado.

Prioridad MoSCoW: Must Have
Dependencias:    RF-005
```

---

**RF-007: Editar cuenta**

```
Descripción:    El sistema debe permitir editar el nombre y tipo de una
                cuenta existente del usuario.
Actor:          Usuario autenticado (propietario de la cuenta)
Precondición:   La cuenta existe y pertenece al usuario autenticado.
Postcondición:  Los datos de la cuenta quedan actualizados.

Criterio de aceptación:
  Dado una cuenta "Efectivo" del usuario,
  cuando envía el request con nombre "Efectivo Casa",
  entonces el sistema responde 200 y la cuenta muestra
  el nuevo nombre en el listado y en el dashboard.

  Dado una cuenta de otro usuario,
  cuando el usuario autenticado intenta editarla,
  entonces el sistema responde 403.

Prioridad MoSCoW: Should Have
Dependencias:    RF-005
```

---

**RF-008: Archivar cuenta**

```
Descripción:    El sistema debe permitir archivar una cuenta (soft delete).
                Las transacciones asociadas no se eliminan ni modifican.
Actor:          Usuario autenticado (propietario de la cuenta)
Precondición:   La cuenta existe y pertenece al usuario.
Postcondición:  La cuenta queda archivada y no aparece en listados activos.
                Sus transacciones históricas permanecen consultables.

Criterio de aceptación:
  Dado una cuenta con balance $0,
  cuando el usuario la archiva,
  entonces desaparece del listado activo y del dashboard,
  pero sus transacciones históricas siguen siendo consultables
  en el historial filtrado.

  Dado una cuenta con balance > $0,
  cuando el usuario intenta archivarla,
  entonces el sistema advierte del balance no nulo y requiere
  confirmación explícita antes de proceder.

Prioridad MoSCoW: Could Have
Dependencias:    RF-005
```

---

### Módulo TRANSACTIONS — Transacciones

---

**RF-009: Registrar transacción simple**

```
Descripción:    El sistema debe permitir registrar un gasto, ingreso o
                transferencia entre cuentas propias, con monto, categoría,
                cuenta, fecha y descripción opcional.
Actor:          Usuario autenticado
Precondición:   Existe al menos una cuenta activa del usuario.
Postcondición:  La transacción queda registrada. El balance de la(s) cuenta(s)
                involucrada(s) se actualiza inmediatamente.

Tipos de transacción: income (ingreso), expense (gasto),
                      transfer (transferencia entre cuentas propias).

Criterio de aceptación:
  Dado un usuario con cuenta ARS con balance $10.000,
  cuando registra un gasto de $2.000 en categoría "Alimentación"
  con fecha de hoy y descripción "Almuerzo",
  entonces la transacción queda registrada, el balance de la cuenta
  pasa a $8.000 y la transacción aparece en el historial.

  Dado un usuario con cuenta origen ARS ($10.000) y cuenta destino ARS ($5.000),
  cuando registra una transferencia de $3.000 entre ambas,
  entonces la cuenta origen queda en $7.000, la destino en $8.000,
  y se registran dos movimientos vinculados en el historial.

Prioridad MoSCoW: Must Have
Dependencias:    RF-005, RF-014
```

---

**RF-010: Registrar transacción en cuotas**

```
Descripción:    El sistema debe permitir registrar una compra en N cuotas
                especificando el monto total, la cantidad de cuotas y la
                fecha de la primera cuota. El monto por cuota es fijo
                (monto_total / N) en el MVP.
Actor:          Usuario autenticado
Precondición:   Existe al menos una cuenta activa del usuario.
Postcondición:  Se generan N transacciones futuras (una por cuota),
                asociadas a la compra original. Cada cuota impacta en el
                balance de la cuenta en su fecha de vencimiento.

Criterio de aceptación:
  Dado un usuario que registra una compra de $60.000 en 3 cuotas mensuales
  iniciando en junio 2026, en su cuenta ARS "Mercado Pago",
  cuando confirma el registro,
  entonces el sistema crea 3 transacciones de $20.000 c/u con fechas
  01/06, 01/07 y 01/08/2026, todas vinculadas a la compra original.
  El balance de la cuenta disminuye $20.000 el 01/06 (cuota vencida),
  y las cuotas futuras no impactan el balance hasta su fecha.

  Dado una compra en cuotas registrada,
  cuando el usuario cancela la compra completa,
  entonces se eliminan todas las cuotas futuras no procesadas y se
  registra un ajuste por las cuotas ya procesadas.

Prioridad MoSCoW: Must Have
Dependencias:    RF-009
```

---

**RF-011: Listar transacciones con filtros**

```
Descripción:    El sistema debe permitir listar transacciones del usuario
                aplicando filtros por cuenta, categoría, tipo, rango de
                fechas y moneda. El resultado debe estar paginado.
Actor:          Usuario autenticado
Precondición:   Existen transacciones registradas del usuario.
Postcondición:  —

Criterio de aceptación:
  Dado un usuario con 50 transacciones en mayo,
  cuando filtra por categoría "Alimentación" y mes mayo 2026,
  entonces el sistema devuelve solo las transacciones que cumplen
  ambos filtros, ordenadas por fecha descendente, paginadas de a 20.

  Dado el mismo usuario,
  cuando consulta el listado sin filtros,
  entonces el sistema no devuelve ninguna transacción del otro usuario.

Prioridad MoSCoW: Must Have
Dependencias:    RF-009
```

---

**RF-012: Editar transacción**

```
Descripción:    El sistema debe permitir editar monto, descripción, categoría
                y fecha de una transacción existente del usuario.
Actor:          Usuario autenticado (creador de la transacción)
Precondición:   La transacción existe y pertenece al usuario autenticado.
Postcondición:  La transacción queda actualizada. El balance de la(s) cuenta(s)
                afectada(s) se recalcula automáticamente.

Criterio de aceptación:
  Dado una transacción de $2.000 en "Alimentación" en la cuenta ARS,
  cuando el usuario cambia el monto a $2.500,
  entonces la transacción muestra $2.500 y el balance de la cuenta
  se ajusta en -$500 adicionales respecto al estado anterior.

Prioridad MoSCoW: Should Have
Dependencias:    RF-009
```

---

**RF-013: Eliminar transacción**

```
Descripción:    El sistema debe permitir eliminar una transacción simple.
                Para compras en cuotas, debe permitir eliminar la compra
                completa (todas las cuotas) o solo las cuotas futuras.
Actor:          Usuario autenticado (creador de la transacción)
Precondición:   La transacción existe y pertenece al usuario autenticado.
Postcondición:  La(s) transacción(es) queda(n) eliminada(s). El balance
                de la(s) cuenta(s) se recalcula.

Criterio de aceptación:
  Dado una transacción simple eliminada,
  cuando el usuario la elimina,
  entonces desaparece del historial y el balance de la cuenta
  vuelve al valor previo a ese registro.

  Dado una compra en 3 cuotas (1 procesada, 2 futuras),
  cuando el usuario cancela las cuotas restantes,
  entonces solo las 2 cuotas futuras se eliminan; la cuota ya
  procesada permanece en el historial.

Prioridad MoSCoW: Should Have
Dependencias:    RF-009, RF-010
```

---

### Módulo CATEGORIES — Categorías

---

**RF-014: Categorías por defecto del sistema**

```
Descripción:    El sistema debe proveer un conjunto de categorías predefinidas
                disponibles para todos los usuarios desde el primer uso.
Actor:          Sistema (automático en setup)
Precondición:   El sistema fue inicializado.
Postcondición:  Las categorías por defecto están disponibles para todos
                los usuarios registrados.

Categorías por defecto:
  Ingresos: Sueldo, Freelance, Alquiler cobrado, Transferencia recibida, Otros ingresos
  Gastos:   Alimentación, Transporte, Vivienda, Salud, Educación,
            Entretenimiento, Ropa y calzado, Servicios, Suscripciones,
            Salidas y restaurantes, Otros gastos

Criterio de aceptación:
  Dado que el sistema está inicializado y un usuario se registra,
  cuando accede al selector de categorías para registrar una transacción,
  entonces las categorías por defecto están disponibles sin ninguna
  acción manual previa del usuario.

Prioridad MoSCoW: Must Have
Dependencias:    RF-001
```

---

**RF-015: Crear categoría personalizada**

```
Descripción:    El sistema debe permitir que el usuario cree categorías
                adicionales con nombre y color/ícono optativos.
Actor:          Usuario autenticado
Precondición:   El usuario está autenticado.
Postcondición:  La categoría queda creada y disponible para asignar
                a transacciones de ese usuario.

Criterio de aceptación:
  Dado un usuario autenticado,
  cuando crea la categoría "Mascota" con color #4CAF50,
  entonces "Mascota" aparece en el selector de categorías al registrar
  una transacción nueva y está disponible solo para ese usuario.

Prioridad MoSCoW: Should Have
Dependencias:    RF-001
```

---

**RF-016: Editar y eliminar categoría personalizada**

```
Descripción:    El sistema debe permitir editar el nombre de una categoría
                personalizada o eliminarla si no tiene transacciones asociadas.
Actor:          Usuario autenticado
Precondición:   La categoría existe y pertenece al usuario.
Postcondición:  La categoría queda actualizada o eliminada.

Criterio de aceptación:
  Dado una categoría personalizada sin transacciones asociadas,
  cuando el usuario la elimina,
  entonces desaparece del listado de categorías.

  Dado una categoría personalizada con transacciones asociadas,
  cuando el usuario intenta eliminarla,
  entonces el sistema responde 409 con mensaje que indica cuántas
  transacciones tienen esa categoría y sugiere reasignarlas primero.

  Las categorías por defecto del sistema no pueden ser eliminadas.

Prioridad MoSCoW: Could Have
Dependencias:    RF-014, RF-015
```

---

### Módulo CURRENCY — Tipo de cambio

---

**RF-017: Configurar tipo de cambio USD/ARS**

```
Descripción:    El sistema debe permitir al usuario registrar el tipo de cambio
                USD/ARS actual con una fecha de vigencia. El TC más reciente
                es el vigente hasta que se registre uno nuevo.
Actor:          Usuario autenticado
Precondición:   El usuario está autenticado.
Postcondición:  El tipo de cambio queda registrado y se usa para conversiones
                a partir de su fecha de vigencia.

Criterio de aceptación:
  Dado un usuario que registra TC = 1.200 ARS/USD con fecha de hoy,
  cuando el dashboard muestra cuentas en USD con vista consolidada en ARS,
  entonces los saldos en USD se muestran multiplicados por 1.200.

  Dado que no hay ningún TC registrado,
  cuando el usuario tiene cuentas en USD y ARS,
  entonces el sistema muestra los saldos en moneda nativa sin convertir,
  y avisa que no hay TC configurado.

Prioridad MoSCoW: Must Have
Dependencias:    RF-001
```

---

**RF-018: Historial de tipos de cambio**

```
Descripción:    El sistema debe guardar el historial completo de tipos de
                cambio ingresados para permitir conversiones históricas correctas.
Actor:          Sistema (automático al registrar TC)
Precondición:   Se registró al menos un tipo de cambio.
Postcondición:  El historial de TC es consultable y se usa para conversiones
                históricas.

Criterio de aceptación:
  Dado que el usuario ingresó TC=$1.000 en marzo y TC=$1.200 en mayo,
  cuando consulta transacciones de marzo con vista en ARS,
  entonces el sistema usa TC=$1.000 para esas transacciones,
  no el TC actual de $1.200.

Prioridad MoSCoW: Should Have
Dependencias:    RF-017
```

---

### Módulo DASHBOARD — Panel principal

---

**RF-019: Resumen financiero mensual**

```
Descripción:    El sistema debe mostrar en el dashboard un resumen del mes
                seleccionado: total de ingresos, total de gastos, ahorro/déficit
                neto y balance total de todas las cuentas activas.
Actor:          Usuario autenticado
Precondición:   El usuario tiene al menos una cuenta y al menos una transacción.
Postcondición:  —

Criterio de aceptación:
  Dado un usuario con ingresos de $80.000 y gastos de $55.000 en mayo 2026,
  y cuentas en ARS y USD,
  cuando accede al dashboard de mayo,
  entonces ve: Ingresos: $80.000 | Gastos: $55.000 | Ahorro: $25.000
  y el balance total de sus cuentas en ARS y en USD (separados por moneda,
  con conversión opcional si hay TC configurado).

Prioridad MoSCoW: Must Have
Dependencias:    RF-009, RF-017
```

---

**RF-020: Gráfico de distribución de gastos por categoría**

```
Descripción:    El sistema debe mostrar un gráfico (torta o barras) con la
                distribución de gastos por categoría del período seleccionado.
Actor:          Usuario autenticado
Precondición:   Existen gastos categorizados en el período seleccionado.
Postcondición:  —

Criterio de aceptación:
  Dado un usuario con gastos en 5 categorías en mayo,
  cuando selecciona mayo en el dashboard,
  entonces el gráfico muestra las 5 categorías con monto y porcentaje
  sobre el total de gastos del mes.
  Las categorías con $0 no aparecen en el gráfico.

Prioridad MoSCoW: Must Have
Dependencias:    RF-011, RF-019
```

---

**RF-021: Gráfico de evolución de balance mensual**

```
Descripción:    El sistema debe mostrar un gráfico de línea con el balance
                neto mensual (ingresos - gastos) de los últimos 6 meses.
Actor:          Usuario autenticado
Precondición:   Existen transacciones de al menos 2 meses distintos.
Postcondición:  —

Criterio de aceptación:
  Dado un usuario con transacciones en los últimos 4 meses,
  cuando accede al dashboard,
  entonces el gráfico de línea muestra 4 puntos de datos (uno por mes)
  con el balance neto de cada mes, y permite distinguir visualmente
  los meses con ahorro de los meses con déficit.

Prioridad MoSCoW: Should Have
Dependencias:    RF-019
```

---

### Módulo SHARED — Gastos compartidos

---

**RF-022: Registrar gasto compartido**

```
Descripción:    El sistema debe permitir que cualquiera de los dos usuarios
                registre un gasto compartido, especificando quién pagó,
                el monto total y la división (por defecto 50/50, editable).
Actor:          Usuario autenticado (cualquiera de los dos)
Precondición:   Ambos usuarios están registrados en el sistema.
Postcondición:  El gasto queda registrado en la cuenta del usuario pagador.
                El sistema registra la deuda correspondiente del otro usuario.

Criterio de aceptación:
  Dado que el usuario A pagó $10.000 en una cena (división 50/50),
  cuando A registra el gasto compartido en su cuenta "Mercado Pago",
  entonces: la transacción de $10.000 se registra en la cuenta de A
  bajo categoría del gasto, y el sistema registra que B le debe $5.000 a A.

  Dado una división no 50/50 (ej: A pagó todo, corresponde 70/30),
  cuando A registra la división personalizada,
  entonces el sistema registra que B le debe $3.000 (30% de $10.000).

Prioridad MoSCoW: Must Have
Dependencias:    RF-009, RF-001
```

---

**RF-023: Ver balance consolidado de gastos compartidos**

```
Descripción:    El sistema debe mostrar el balance neto de deudas entre
                los dos usuarios de forma consolidada (compensación automática).
Actor:          Usuario autenticado
Precondición:   Existen gastos compartidos registrados.
Postcondición:  —

Criterio de aceptación:
  Dado que A le debe $5.000 a B (por un gasto donde B pagó)
  y B le debe $3.000 a A (por otro gasto donde A pagó),
  cuando cualquiera de los dos consulta el balance compartido,
  entonces el sistema muestra: "A le debe $2.000 a B" (compensación neta)
  y no muestra ambas deudas por separado como obligatorio.

Prioridad MoSCoW: Must Have
Dependencias:    RF-022
```

---

**RF-024: Saldar deuda de gasto compartido**

```
Descripción:    El sistema debe permitir marcar el balance compartido como
                saldado, registrando opcionalmente la transferencia de pago
                en la cuenta correspondiente.
Actor:          Cualquier usuario de los dos (el que recibe confirma)
Precondición:   Existe un balance neto pendiente entre los dos usuarios.
Postcondición:  El balance compartido queda en $0.
                Si se registró la transferencia, ambas cuentas se actualizan.

Criterio de aceptación:
  Dado que A le debe $2.000 a B (balance neto),
  cuando B marca el balance como saldado,
  entonces el balance compartido pasa a $0 y se registra el evento
  en el historial de gastos compartidos con la fecha de saldo.

  Dado que A transfirió $2.000 a B por Mercado Pago y quiere registrarlo,
  cuando A registra la transferencia al saldar,
  entonces la cuenta de A disminuye $2.000 y la de B aumenta $2.000,
  y el balance compartido queda en $0.

Prioridad MoSCoW: Must Have
Dependencias:    RF-022, RF-023
```

---

## 4. Requerimientos No Funcionales (ISO/IEC 25010)

---

**RNF-001: Eficiencia de rendimiento**
```
Los endpoints de listado (transacciones, cuentas, dashboard) deben
responder en < 500ms para el percentil 95 bajo carga de uso normal
(2 usuarios concurrentes, dataset de hasta 5.000 transacciones).

El endpoint del dashboard (que agrega datos) debe responder en < 800ms
bajo las mismas condiciones.

Herramienta de medición: pytest-benchmark o k6 en entorno de test.
```

**RNF-002: Fiabilidad**
```
El sistema debe mantener disponibilidad >= 99% mensual cuando está
deployado en Railway (equivalente a < 7.2 hs de downtime/mes).

En caso de error no recuperable en el backend, el sistema debe:
  - Devolver HTTP 500 con mensaje genérico al cliente.
  - Registrar el error completo (stack trace) en el log del servidor.
  - No exponer stack traces ni rutas internas al cliente.
```

**RNF-003: Seguridad — contraseñas**
```
Toda contraseña debe almacenarse usando bcrypt o Argon2id con
cost factor >= 12.
Ninguna contraseña puede almacenarse en texto plano, logs ni
variables de entorno en ninguna circunstancia.
```

**RNF-004: Seguridad — autenticación**
```
Toda ruta que devuelva o modifique datos de usuario debe requerir
un token de autenticación válido (JWT u equivalente).
Un request sin token o con token expirado devuelve HTTP 401.
Los tokens de acceso expiran en máximo 24 horas.
```

**RNF-005: Seguridad — aislamiento de datos entre usuarios**
```
Ningún usuario puede ver, editar ni eliminar cuentas, transacciones
o categorías de otro usuario, excepto los gastos compartidos
explícitamente creados entre los dos.

Un request a un recurso de otro usuario devuelve HTTP 403, nunca 404
(para no confirmar la existencia del recurso).

Criterio verificable: test de autorización cruzada que comprueba que
el usuario B no puede acceder a ningún recurso del usuario A excepto
los gastos compartidos. Este test corre en CI en cada push.
```

**RNF-006: Mantenibilidad — cobertura de tests**
```
La cobertura de tests unitarios debe ser >= 80% en la capa de dominio
y servicios de negocio.
Cada RF clasificado como Must Have debe tener al menos un test de
integración que valide su criterio de aceptación Given/When/Then.
Herramienta: pytest + coverage.py (backend), Vitest o Jest (frontend).
```

**RNF-007: Mantenibilidad — calidad de código**
```
El código backend debe pasar linting sin errores (ruff o flake8).
El código frontend debe pasar ESLint sin errores.
Ningún módulo/archivo debe superar 400 líneas de código.
Ninguna función/método debe superar 50 líneas.
Estos límites se verifican en el pipeline CI antes del merge.
```

**RNF-008: Portabilidad — containerización**
```
El sistema completo (backend + base de datos) debe poder inicializarse
con docker-compose up sin configuración manual adicional más allá del
archivo .env (cuya plantilla .env.example está en el repositorio).

El sistema debe funcionar en cualquier entorno con Docker Engine
instalado: Linux, macOS, WSL2 en Windows.
```

**RNF-009: Usabilidad**
```
Un usuario sin experiencia previa con herramientas de gestión financiera
debe poder:
  a) Registrar su primera transacción en < 3 minutos desde el primer login.
  b) Entender el dashboard principal sin leer documentación.

Criterio de validación: el usuario secundario (la novia) completa los
pasos (a) y (b) en la primera sesión de uso conjunto, sin ayuda activa
del desarrollador. Si no los cumple, se documenta qué falló y se itera
la UI antes de declarar el MVP cerrado.
```

**RNF-010: Portabilidad — deploy**
```
El sistema debe poder deployarse en Railway sin modificación de código.
Solo variables de entorno distinguen el entorno local del de producción.
El proceso de deploy a Railway debe documentarse en el README en < 10 pasos.
```

---

## 5. Requerimientos de Seguridad

Basado en OWASP Top 10 (2021) aplicables al contexto de Zenith.

---

**RS-001: Inyección — A03:2021**
```
Toda interacción con la base de datos debe realizarse a través del ORM
o queries parametrizadas. Está prohibida la concatenación de strings en
queries SQL en cualquier circunstancia.

Criterio verificable: bandit -r src/ no reporta issues de nivel HIGH
relacionados a inyección. Este check corre en CI antes de cada deploy.
```

**RS-002: Autenticación rota — A07:2021**
```
El sistema debe:
  - Bloquear el acceso a rutas protegidas sin token válido (HTTP 401).
  - No revelar si el email existe o no en mensajes de error de login.
  - Expirar tokens de acceso en máximo 24 horas.
  - No implementar "recordar contraseña" en el MVP (reduce superficie
    de ataque en una herramienta personal).
```

**RS-003: Exposición de datos sensibles — A02:2021**
```
  - Toda comunicación debe ser sobre HTTPS en producción
    (Railway lo provee por defecto; redirigir HTTP → HTTPS).
  - Ninguna respuesta de API incluye el hash de contraseña.
  - Los logs no contienen contraseñas, tokens ni datos financieros.
  - Las variables sensibles (SECRET_KEY, DATABASE_URL, etc.)
    nunca se commitean al repositorio.
  - El repositorio incluye .env.example con claves sin valores reales.
```

**RS-004: Control de acceso roto — A01:2021**
```
  - Cada endpoint que devuelve o modifica datos verifica que el recurso
    solicitado pertenece al usuario autenticado.
  - El acceso no autorizado devuelve HTTP 403, nunca HTTP 404.
  - Los gastos compartidos son el único punto de datos cruzados,
    y requieren que ambos usuarios estén explícitamente vinculados al gasto.
  - El test de aislamiento entre usuarios (RNF-005) actúa como control
    verificable de este requerimiento.
```

**RS-005: Componentes vulnerables — A06:2021**
```
Antes de cada deploy a producción, ejecutar:
  - pip-audit (o safety) para dependencias Python.
  - npm audit para dependencias del frontend.
Cualquier dependencia con CVE de severidad HIGH o CRITICAL debe ser
actualizada o justificada con ADR antes del deploy.
Este check se integra en el pipeline CI/CD.
```

**RS-006: Ley 25.326 — Protección de Datos Personales (Argentina)**
```
El sistema puede publicarse en GitHub con licencia AGPL y ser usado
por terceros en modo self-hosted. Por ello:

  - Los datos de cada usuario son de su exclusiva propiedad.
  - El sistema no envía datos a terceros en ninguna circunstancia.
  - El repositorio incluye aviso de privacidad en el README indicando
    que todos los datos se almacenan localmente (self-hosted).
  - El sistema debe incluir funcionalidad de borrado de cuenta y sus
    datos asociados antes de habilitarse para uso por terceros (MVP+1).

Nota: En uso exclusivamente personal y self-hosted, la Ley 25.326 aplica
de forma limitada, pero los principios de minimización de datos y
autodeterminación informativa se respetan por diseño desde el inicio.
```

---

## 6. Restricciones y supuestos

### 6.1 Restricciones técnicas

- **Stack**: A definir formalmente en F2. El SRS es agnóstico al framework. El autor tiene experiencia probada con Python/Django/PostgreSQL (Lino Saludable) y el GZSM §F2.3 guía la decisión de stack. Frontend: React + TypeScript es la dirección natural dado el contexto de portfolio.
- **Base de datos**: Relacional (PostgreSQL preferido).
- **Deploy MVP**: Railway para backend. Frontend puede deployarse en Railway Static, Vercel o Netlify.
- **Usuarios máximos MVP**: 2. No hay lógica multi-tenant compleja.
- **Sin integraciones externas obligatorias**: El TC se ingresa manualmente. Sin conexión a Mercado Pago, BCRA, AFIP ni ninguna API financiera externa.
- **Licencia**: AGPL-3.0.

### 6.2 Restricciones de equipo y tiempo

- Desarrollador único: Giuliano Zulatto.
- Tiempo disponible: variable. La restricción práctica es la urgencia de portfolio para búsqueda de primer empleo.
- Implicancia: el conjunto de RF Must Have debe ser construible en 6-8 semanas de trabajo focalizado.

### 6.3 Supuestos

- El usuario secundario (la novia) no tiene requisitos técnicos propios; sus necesidades están cubiertas por el perfil de usuario primario.
- El tipo de cambio se actualiza manualmente según criterio del usuario (puede ser diario, semanal o puntual).
- Las cuotas en el MVP tienen monto fijo por cuota (sin ajuste automático por inflación). El ajuste se evalúa en F4 post-MVP.
- El sistema no requiere notificaciones push, email ni alertas proactivas en el MVP.
- El primer boot del sistema incluye un script de setup que crea los dos usuarios y las categorías por defecto.

---

## 7. Priorización MoSCoW

### Must Have — MVP (6-8 semanas)

| ID | Descripción |
|---|---|
| RF-001 | Registro de usuario |
| RF-002 | Login |
| RF-003 | Logout |
| RF-005 | Crear cuenta |
| RF-006 | Listar cuentas |
| RF-009 | Registrar transacción simple |
| RF-010 | Registrar transacción en cuotas |
| RF-011 | Listar transacciones con filtros |
| RF-014 | Categorías por defecto |
| RF-017 | Configurar tipo de cambio USD/ARS |
| RF-019 | Dashboard: resumen financiero mensual |
| RF-020 | Dashboard: gráfico de distribución por categoría |
| RF-022 | Registrar gasto compartido |
| RF-023 | Ver balance consolidado de gastos compartidos |
| RF-024 | Saldar deuda de gasto compartido |
| RNF-001 | Performance < 500ms P95 |
| RNF-003 | Contraseñas hasheadas (bcrypt/Argon2id) |
| RNF-004 | Autenticación con token en rutas protegidas |
| RNF-005 | Aislamiento de datos entre usuarios |
| RNF-006 | Cobertura >= 80% en capa de dominio |
| RNF-008 | Docker Compose funcional |
| RNF-010 | Deploy en Railway |
| RS-001 a RS-006 | Seguridad OWASP + Ley 25.326 |

### Should Have — Post-MVP v1.1

| ID | Descripción |
|---|---|
| RF-004 | Cambio de contraseña |
| RF-007 | Editar cuenta |
| RF-012 | Editar transacción |
| RF-013 | Eliminar transacción |
| RF-015 | Crear categoría personalizada |
| RF-018 | Historial de tipos de cambio para conversión histórica |
| RF-021 | Gráfico de evolución de balance mensual |
| RNF-002 | Disponibilidad >= 99% mensual en Railway |
| RNF-007 | Límites de LOC en módulos y funciones |
| RNF-009 | Validación de usabilidad con usuario secundario |

### Could Have — Backlog futuro

| ID | Descripción |
|---|---|
| RF-008 | Archivar cuenta (soft delete) |
| RF-016 | Eliminar categoría personalizada |

### Won't Have — Explícitamente fuera del MVP y del proyecto

- IA en cualquier forma
- Bot de Telegram
- Módulo de inversiones (cedears, acciones, bonos) → proyecto separado
- Exportación PDF
- Módulo de patrimonio neto
- Usuarios externos o modelo de monetización
- Integración automática con Mercado Pago o cualquier API financiera
- Notificaciones push o email
- Contenido educativo o alfabetización financiera
- Aplicación móvil nativa

---

## Apéndice: Verificación criterio de salida F1 (GZSM §F1.4)

| Criterio | Estado |
|---|---|
| ☑ Todos los RF tienen criterio de aceptación testeable (Given/When/Then). | Cumplido — RF-001 a RF-024 |
| ☑ Todos los RNF tienen métrica medible, no descripción subjetiva. | Cumplido — RNF-001 a RNF-010 |
| ☑ La priorización MoSCoW está definida y el MVP está claro. | Cumplido — Sección 7 |
| ☑ Los requerimientos de seguridad están listados como RS, no como afterthought. | Cumplido — Sección 5 (RS-001 a RS-006) |
| ☑ El documento tiene número de versión y fecha. | v1.0 · Mayo 2026 |

**Estado: F1 CERRADO — Listo para iniciar F2·Arquitectura.**

---

*GZSM v1.1 · Giuliano Zulatto · Ingeniería en Software — Universidad Siglo 21*  
*Próximo paso: PT-03 → F2·Arquitectura — ADRs, decisión de stack, estructura de capas.*
