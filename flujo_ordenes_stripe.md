# 📦 Flujo de Procesamiento de Órdenes con Stripe

## 🎯 Resumen Ejecutivo

Este documento describe una arquitectura robusta para procesar órdenes en un e-commerce utilizando Stripe como pasarela de pagos.

Incluye:

- Modelo entidad-relación corregido
- Flujo de pagos con Payment Intents
- Webhooks e idempotencia
- Manejo de errores
- Máquina de estados
- Seguridad y validaciones
- Diagramas Mermaid corregidos y compatibles

---

# 📊 Flujo General del Sistema

## Flujo recomendado con Stripe

```text
Order (PENDING)
    ↓
Crear PaymentIntent en Stripe
    ↓
Cliente paga en Stripe Checkout
    ↓
Stripe envía webhook
    ↓
Webhook valida firma
    ↓
Payment = COMPLETED
    ↓
Order = PROCESSING
    ↓
Fulfillment
    ↓
SHIPPED → DELIVERED
```

---

# 🧱 Modelo de Datos

## Tabla `payments` — Campos adicionales

```python
stripe_payment_intent_id: String(unique=True)
stripe_charge_id: String(nullable=True)

payment_method_type: Enum(
    "card",
    "bank_transfer",
    "wallet"
)

last_four: String(4, nullable=True)

error_message: Text(nullable=True)

webhook_received_at: DateTime(nullable=True)
```

---

# 🆕 Nuevas Tablas

## `payment_transactions`

Auditoría de TODOS los intentos de pago.

```python
id: PK

payment_id: FK -> payments.id

stripe_event_id: String(unique=True)

status: Enum(
    "pending",
    "succeeded",
    "failed"
)

amount: Decimal

metadata_json: JSON

created_at: DateTime
```

---

## `order_timeline`

Historial completo de eventos de la orden.

```python
id: PK

order_id: FK -> orders.id

event_type: Enum(
    "created",
    "payment_started",
    "payment_completed",
    "payment_failed",
    "processing",
    "shipped",
    "delivered",
    "cancelled"
)

status_from: String(nullable=True)

status_to: String(nullable=True)

user_id: FK -> users.id(nullable=True)

notes: Text(nullable=True)

created_at: DateTime
```

---

# 🧾 Tabla `orders` — Nuevos campos

```python
shipping_address: String

estimated_delivery_date: DateTime(nullable=True)

payment_deadline: DateTime

notes: Text(nullable=True)
```

---

# 📐 Diagrama Entidad-Relación (ER) — Mermaid Corregido

```mermaid
erDiagram

    CUSTOMERS ||--o{ ORDERS : creates

    ORDERS ||--|{ ORDER_DETAILS : contains
    PRODUCTS ||--o{ ORDER_DETAILS : referenced_by

    ORDERS ||--|| PAYMENTS : has

    PAYMENTS ||--o{ PAYMENT_TRANSACTIONS : logs

    ORDERS ||--o{ ORDER_TIMELINE : generates

    CUSTOMERS {
        int id PK
        string names
        string email UK
    }

    ORDERS {
        int id PK
        decimal total_amount
        string status
        string shipping_address
        datetime payment_deadline
        datetime estimated_delivery_date
        text notes
        int customer_id FK
    }

    ORDER_DETAILS {
        int id PK
        int quantity
        decimal price
        int order_id FK
        int product_id FK
    }

    PRODUCTS {
        int id PK
        string name
        decimal price
    }

    PAYMENTS {
        int id PK
        string status
        string payment_method_type
        string stripe_payment_intent_id UK
        string stripe_charge_id
        string last_four
        text error_message
        datetime webhook_received_at
        int order_id FK
    }

    PAYMENT_TRANSACTIONS {
        int id PK
        string stripe_event_id UK
        string status
        decimal amount
        json metadata_json
        datetime created_at
        int payment_id FK
    }

    ORDER_TIMELINE {
        int id PK
        string event_type
        string status_from
        string status_to
        text notes
        datetime created_at
        int order_id FK
    }
```

---

# 🔄 Relaciones del Sistema

```text
CUSTOMERS (1)
    └── ORDERS (N)
            ├── ORDER_DETAILS (N)
            │       └── PRODUCTS
            │
            ├── PAYMENTS (1)
            │       └── PAYMENT_TRANSACTIONS (N)
            │
            └── ORDER_TIMELINE (N)
```

---

# 🧭 FASE 1 — Creación de Orden

## Paso 1 — Cliente crea carrito

El cliente:

- agrega productos
- define dirección de envío
- selecciona método de pago

---

## Paso 2 — Crear Order

```python
order.status = "PENDING"

order.payment_deadline = now() + timedelta(hours=24)
```

---

## Paso 3 — Crear OrderDetails

```python
for item in cart:
    OrderDetail.create(
        product_id=item.product_id,
        quantity=item.quantity,
        price=item.price
    )
```

---

## Paso 4 — Crear Payment

```python
payment.status = "PENDING"

payment.payment_method_type = "card"
```

---

## Paso 5 — Registrar Timeline

```python
OrderTimeline.create(
    event_type="created",
    status_from=None,
    status_to="PENDING"
)
```

---

# 💳 FASE 2 — Integración con Stripe

## Endpoint

```http
POST /orders/{id}/pay
```

---

## Crear PaymentIntent

```python
intent = stripe.PaymentIntent.create(
    amount=int(order.total_amount * 100),
    currency="usd",
    payment_method_types=["card"],
    metadata={
        "order_id": order.id
    }
)
```

---

## Guardar referencia Stripe

```python
payment.stripe_payment_intent_id = intent.id

payment.status = "PROCESSING"
```

---

## Registrar timeline

```python
OrderTimeline.create(
    event_type="payment_started",
    status_from="PENDING",
    status_to="PROCESSING"
)
```

---

# 🔀 Diagrama de Secuencia — Pago y Webhook

```mermaid
sequenceDiagram

    actor Cliente

    participant API
    participant Stripe
    participant DB

    Cliente->>API: POST /orders/{id}/pay

    API->>Stripe: Create PaymentIntent

    Stripe-->>API: payment_intent_id

    API->>DB: Update payment status

    API-->>Cliente: checkout_url

    Cliente->>Stripe: Completa pago

    Stripe->>API: Webhook payment_intent.succeeded

    API->>API: Validar firma webhook

    alt Pago exitoso

        API->>DB: Payment = COMPLETED

        API->>DB: Order = PROCESSING

        API->>DB: Insert timeline events

        API-->>Stripe: 200 OK

    else Pago fallido

        API->>DB: Payment = FAILED

        API->>DB: Insert payment_failed

        API-->>Stripe: 200 OK

    end
```

---

# 🪝 FASE 3 — Webhook Stripe

## Endpoint

```http
POST /webhooks/stripe
```

---

## Validación de Firma

```python
event = stripe.Webhook.construct_event(
    payload=body,
    sig_header=sig_header,
    secret=STRIPE_ENDPOINT_SECRET
)
```

---

## Extraer datos del charge

```python
charge = event.data.object.charges.data[0]

payment.stripe_charge_id = charge.id

payment.last_four = (
    charge.payment_method_details.card.last4
)

payment.webhook_received_at = now()
```

---

## Registrar PaymentTransaction

```python
PaymentTransaction.create(
    payment_id=payment.id,
    stripe_event_id=event.id,
    status="succeeded",
    amount=order.total_amount,
    metadata_json=event.to_dict()
)
```

---

## Actualizar estados

```python
payment.status = "COMPLETED"

order.status = "PROCESSING"
```

---

# 📦 FASE 4 — Fulfillment

## Order PROCESSING

Significa:

- pago confirmado
- iniciar preparación
- generar envío

---

## Registrar timeline

```python
OrderTimeline.create(
    event_type="processing",
    status_from="PENDING",
    status_to="PROCESSING"
)
```

---

# 🚚 FASE 5 — Envío y Entrega

## Cuando se envía

```python
order.status = "SHIPPED"
```

Acciones:

- generar tracking
- enviar email
- calcular ETA

---

## Cuando se entrega

```python
order.status = "DELIVERED"
```

Acciones:

- registrar entrega
- solicitar review

---

# ⚠️ Casos de Error

---

## Caso 1 — Orden expirada

```text
PENDING > 24h
    ↓
CANCELLED
```

Acciones:

- liberar inventario
- cancelar PaymentIntent
- enviar email

---

## Caso 2 — Pago rechazado

Webhook:

```text
payment_intent.payment_failed
```

Acciones:

- Payment = FAILED
- guardar error_message
- permitir retry

---

## Caso 3 — Reintento de pago

```text
FAILED
    ↓
Nuevo PaymentIntent
```

Se reemplaza:

```python
payment.stripe_payment_intent_id
```

---

## Caso 4 — Webhook duplicado

Solución:

```python
stripe_event_id UNIQUE
```

---

## Caso 5 — Cancelación manual

```python
stripe.PaymentIntent.cancel(intent_id)
```

---

# 🔄 Máquina de Estados — Mermaid Corregido

```mermaid
stateDiagram-v2

    state "Orders" as Orders {

        [*] --> PENDING

        PENDING --> PROCESSING : payment_completed

        PENDING --> CANCELLED : timeout

        PROCESSING --> SHIPPED : fulfillment

        SHIPPED --> DELIVERED : delivered

        DELIVERED --> [*]

        CANCELLED --> [*]
    }

    state "Payments" as Payments {

        [*] --> PAYMENT_PENDING

        PAYMENT_PENDING --> PROCESSING_PAYMENT : validating

        PROCESSING_PAYMENT --> COMPLETED : success

        PROCESSING_PAYMENT --> FAILED : rejected

        FAILED --> PAYMENT_PENDING : retry

        COMPLETED --> [*]
    }
```

---

# 🚨 Flujo de Errores — Mermaid Corregido

```mermaid
flowchart TD

    A["Order Created<br/>PENDING"]

    A --> B{"Expired?"}

    B -->|Yes| C["Order CANCELLED"]

    C --> D["Release inventory"]

    D --> E([END])

    B -->|No| F["Create PaymentIntent"]

    F --> G["Payment PROCESSING"]

    G --> H{"Stripe approves?"}

    H -->|Yes| I["payment_intent.succeeded"]

    I --> J["Payment COMPLETED"]

    J --> K["Order PROCESSING"]

    K --> L([SUCCESS])

    H -->|No| M["payment_intent.payment_failed"]

    M --> N["Payment FAILED"]

    N --> O{"Retry allowed?"}

    O -->|Yes| F

    O -->|No| C
```

---

# 🏗️ Arquitectura del Sistema — Mermaid Corregido

```mermaid
graph TB

    subgraph Frontend
        CLIENT["Cliente"]
        WEB["React / Vue"]
    end

    subgraph Backend
        API["FastAPI"]
        WEBHOOK["Stripe Webhook"]
        ORDER_SERVICE["OrderService"]
        PAYMENT_SERVICE["PaymentService"]
    end

    subgraph Database
        DB[(PostgreSQL)]
        REDIS[(Redis)]
    end

    subgraph Queue
        CELERY["Celery Workers"]
    end

    subgraph External
        STRIPE["Stripe API"]
        EMAIL["Email Service"]
    end

    CLIENT --> WEB

    WEB --> API

    API --> ORDER_SERVICE

    API --> PAYMENT_SERVICE

    PAYMENT_SERVICE --> STRIPE

    STRIPE --> WEBHOOK

    WEBHOOK --> DB

    API --> DB

    API --> REDIS

    API --> CELERY

    CELERY --> EMAIL
```

---

# 📊 Data Flow Diagram — Mermaid Corregido

```mermaid
graph LR

    CLIENT["Cliente"]

    API["FastAPI"]

    ORDER_SERVICE["OrderService"]

    PAYMENT_SERVICE["PaymentService"]

    WEBHOOK["WebhookHandler"]

    ORDERS_DB[(Orders)]

    PAYMENTS_DB[(Payments)]

    TIMELINE_DB[(Timeline)]

    STRIPE["Stripe"]

    CLIENT --> API

    API --> ORDER_SERVICE

    ORDER_SERVICE --> ORDERS_DB

    ORDER_SERVICE --> PAYMENT_SERVICE

    PAYMENT_SERVICE --> STRIPE

    PAYMENT_SERVICE --> PAYMENTS_DB

    STRIPE --> WEBHOOK

    WEBHOOK --> PAYMENTS_DB

    WEBHOOK --> ORDERS_DB

    WEBHOOK --> TIMELINE_DB
```

---

# ✅ Validaciones Clave

```text
✔ Order.total_amount >= 0

✔ total_amount = SUM(order_details)

✔ Un Payment por Order

✔ stripe_payment_intent_id UNIQUE

✔ Verificar firma del webhook

✔ stripe_event_id UNIQUE

✔ payment_deadline futuro

✔ COMPLETED => Order != PENDING

✔ Registrar TODOS los cambios en timeline
```

---

# 🔐 Seguridad

## Nunca guardar tarjetas

Stripe maneja:

- PAN
- CVV
- expiración
- tokenización

Tu backend nunca toca datos sensibles.

---

## Validar webhooks

```python
stripe.Webhook.construct_event(
    body,
    sig_header,
    STRIPE_ENDPOINT_SECRET
)
```

---

## HTTPS obligatorio

Stripe requiere HTTPS para webhooks.

---

## Variables de entorno

```env
STRIPE_SECRET_KEY=
STRIPE_WEBHOOK_SECRET=
```

---

# 📋 Checklist de Implementación

```text
[ ] Agregar campos a payments
[ ] Crear payment_transactions
[ ] Crear order_timeline
[ ] Crear migraciones Alembic

[ ] Implementar POST /orders/{id}/pay

[ ] Implementar POST /webhooks/stripe

[ ] Validar firmas Stripe

[ ] Crear PaymentService

[ ] Crear OrderService

[ ] Implementar state machine

[ ] Configurar retries

[ ] Configurar cron expiración

[ ] Configurar Stripe Dashboard

[ ] Crear tests

[ ] Documentar Swagger/Postman
```

---

# 📚 Referencias Oficiales

- [Stripe Payment Intents API](https://stripe.com/docs/payments/payment-intents?utm_source=chatgpt.com)
- [Stripe Webhooks](https://stripe.com/docs/webhooks?utm_source=chatgpt.com)
- [Webhook Signature Verification](https://stripe.com/docs/webhooks/signatures?utm_source=chatgpt.com)
- [PCI Compliance en Stripe](https://stripe.com/docs/security/compliance?utm_source=chatgpt.com)

---

# 🚀 Próximos Pasos

1. Crear migraciones Alembic
2. Implementar modelos SQLAlchemy
3. Crear servicios de dominio
4. Implementar endpoints FastAPI
5. Integrar Stripe SDK
6. Crear tests unitarios/integración
7. Configurar observabilidad y logs
8. Deploy y monitoreo
