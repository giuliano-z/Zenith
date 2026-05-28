# ADR-004: Modelo de Balance — Calculado en Tiempo Real vs Materializado

**Estado:** Aceptado  
**Fecha:** Mayo 2026  
**Autor:** Giuliano Zulatto  
**Proyecto:** Zenith  

---

## Contexto

El balance de una cuenta en Zenith no es un número simple. Se compone de:

1. **Transacciones simples** (income, expense, transfer): impactan el balance en su fecha de registro.
2. **Cuotas (installments)**: impactan el balance solo cuando su `fecha_vencimiento <= hoy`. Las cuotas futuras NO afectan el balance actual.
3. **Gastos compartidos**: el monto pagado por el usuario se registra como transacción normal en su cuenta; la deuda del otro usuario es un estado separado (módulo SHARED).

Esta complejidad plantea una decisión de diseño fundamental: ¿el balance se **calcula** cada vez que se consulta (query en tiempo real), o se **almacena** como campo actualizable (campo materializado)?

La restricción crítica es RNF-001: el endpoint de listado de cuentas debe responder en < 500ms P95 con hasta 5.000 transacciones en el dataset.

---

## Decisión

**El balance se calcula en tiempo real mediante una query de agregación (SUM) sobre las transacciones, sin campo materializado.**

Se introduce un índice compuesto en la tabla de transacciones para garantizar el rendimiento dentro del umbral de RNF-001.

---

## Modelo de datos relevante

```python
# accounts/models.py
class Account(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    type = models.CharField(choices=AccountType.choices)
    currency = models.CharField(choices=Currency.choices)
    initial_balance = models.DecimalField(max_digits=14, decimal_places=2, default=0)
    is_archived = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    # ⚠️ Sin campo `balance`: se calcula en accounts/services.py

# transactions/models.py
class Transaction(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    type = models.CharField(choices=TransactionType.choices)  # income/expense/transfer
    amount = models.DecimalField(max_digits=14, decimal_places=2)
    date = models.DateField()  # fecha efectiva (cuotas: fecha_vencimiento)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255, blank=True)
    installment_group = models.ForeignKey('InstallmentGroup', null=True, blank=True, on_delete=models.SET_NULL)
    is_processed = models.BooleanField(default=True)  # False = cuota futura

    class Meta:
        indexes = [
            models.Index(fields=['account', 'date', 'is_processed']),  # Índice crítico para el cálculo de balance
        ]
```

## Función de cálculo de balance

```python
# accounts/services.py
from django.db.models import Sum, Q
from decimal import Decimal
from datetime import date

def get_account_balance(account: Account) -> Decimal:
    """
    Calcula el balance actual de una cuenta.
    Solo considera transacciones con fecha <= hoy y is_processed=True.
    Las cuotas futuras (is_processed=False, date > hoy) NO se incluyen.
    """
    today = date.today()
    
    processed = account.transaction_set.filter(
        Q(is_processed=True) | Q(date__lte=today)
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    return account.initial_balance + processed
```

**Nota sobre `amount` con signo:** Las transacciones de tipo `expense` y `transfer_out` se almacenan con `amount` negativo. Las de tipo `income` y `transfer_in` con `amount` positivo. El balance es la suma algebraica. Esto elimina la necesidad de lógica condicional en la función de cálculo y permite el `SUM` directo.

---

## Análisis de rendimiento

Con 5.000 transacciones totales y 2 usuarios, cada cuenta tiene en promedio < 2.500 transacciones.

El `SUM` sobre una columna indexada en PostgreSQL para < 2.500 filas es < 5ms en condiciones normales. El overhead del endpoint de listado de cuentas (que calcula el balance de cada cuenta del usuario) suma múltiples SELECTs. Con 10 cuentas activas por usuario, el tiempo de DB sería < 50ms. El overhead de Django + DRF + serialización se mantiene dentro de RNF-001 (< 500ms P95).

El índice compuesto `(account, date, is_processed)` garantiza que la query use Index Scan en vez de Seq Scan incluso con crecimiento del dataset post-MVP.

---

## Alternativa evaluada y descartada

**Campo `balance` materializado en `Account`**

En este modelo, el campo `balance` se actualiza atómicamente cada vez que se registra, edita o elimina una transacción (usando `F()` expressions o transacciones atómicas de Django).

Por qué se descarta:
- **Complejidad de consistencia**: cada operación sobre transacciones (crear, editar, eliminar, cancelar cuotas) debe actualizar el balance de forma atómica. Con cuotas (N transacciones ligadas a un grupo) y transferencias (2 cuentas afectadas simultáneamente), el riesgo de inconsistencia es alto.
- **Cuotas futuras**: el balance materializado tendría que ignorar cuotas futuras, lo que requiere lógica adicional en cada operación de escritura para determinar qué cuotas ya "impactaron" el balance.
- El problema del balance desnormalizado es clásico en sistemas financieros: una sola actualización fallida deja el balance incorrecto indefinidamente. El cálculo en tiempo real no puede tener este bug estructural: el balance siempre refleja el estado real de las transacciones.
- Con el dataset del MVP (< 5.000 transacciones) y el índice correcto, el rendimiento del cálculo en tiempo real supera el umbral de RNF-001 con margen.

**Cuándo el campo materializado sería correcto:** dataset de millones de transacciones con decenas de usuarios concurrentes. En ese escenario, el recálculo en tiempo real sería el cuello de botella. La migración desde cálculo real a campo materializado es una decisión de F4, cuando haya evidencia de degradación.

---

## Consecuencias positivas

- El balance siempre es correcto: deriva directamente de las transacciones registradas. No puede desincronizarse.
- Simplifica las operaciones de escritura (crear, editar, eliminar transacciones): no hay que actualizar un campo derivado.
- El comportamiento de las cuotas (solo impactan cuando `date <= hoy`) es trivial de implementar con el filtro `is_processed` sin lógica extra.
- Facilita RF-018 (historial de TC para conversiones históricas): el balance en una fecha pasada se calcula filtrando `date <= fecha_objetivo`.

## Consecuencias negativas (deuda técnica aceptada)

- Cada request de listado de cuentas genera N queries (una por cuenta para calcular su balance). Se mitiga con `prefetch_related` o anotaciones de Django para hacer la agregación en una sola query con `GROUP BY account_id`.
- Si el dataset crece significativamente (post-MVP, usuarios externos), el recálculo en tiempo real puede degradarse. Esta decisión se reevalúa en F4 con métricas GQM reales.

---

## RNF impactados

| RNF | Cómo esta decisión lo satisface |
|---|---|
| RNF-001 (< 500ms P95) | Índice compuesto + agregación SUM en PostgreSQL para < 5.000 transacciones queda dentro del umbral. |
| RNF-006 (cobertura >= 80%) | `get_account_balance()` es una función pura testeable con fixtures de Django, sin mocks complejos. |
| RF-010 (cuotas) | `is_processed=False` para cuotas futuras resuelve su exclusión del balance sin lógica adicional. |
| RF-018 (TC histórico) | El cálculo por fecha es nativo: filtrar `date <= fecha` produce el balance histórico correcto. |
