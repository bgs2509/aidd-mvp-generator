# Function: Service Naming

> **Purpose**: Defining names for services and components.

---

## Goal

Choose consistent and clear names for all
system components according to framework conventions.

---

## Naming Conventions

### Project Context

```
{context} — short project name (2-15 characters)

Examples:
- booking
- finance
- inventory
- orders
```

### Domain

```
{domain} — primary domain entity

Examples:
- restaurant
- transaction
- product
- order
```

---

## Naming Patterns

### Services

| Type | Pattern | Example |
|------|---------|---------|
| Business API | `{context}_api` | `booking_api` |
| Data API (PG) | `{context}_data` | `booking_data` |
| Data API (Mongo) | `{context}_docs` | `booking_docs` |
| Telegram Bot | `{context}_bot` | `booking_bot` |
| Background Worker | `{context}_worker` | `booking_worker` |

### Docker Services

| Type | Pattern | Example |
|------|---------|---------|
| Business API | `{context}-api` | `booking-api` |
| Data API | `{context}-data` | `booking-data` |
| PostgreSQL | `{context}-postgres` | `booking-postgres` |
| MongoDB | `{context}-mongo` | `booking-mongo` |
| Redis | `{context}-redis` | `booking-redis` |
| Bot | `{context}-bot` | `booking-bot` |
| Worker | `{context}-worker` | `booking-worker` |

### Directories

```
services/
├── {context}_api/           # Business API
│   └── src/
│       └── {context}_api/   # Python package
├── {context}_data/          # Data API
│   └── src/
│       └── {context}_data/
├── {context}_bot/           # Telegram Bot
│   └── src/
│       └── {context}_bot/
└── {context}_worker/        # Background Worker
    └── src/
        └── {context}_worker/
```

### Python Packages

| Element | Style | Example |
|---------|-------|---------|
| Package | snake_case | `booking_api` |
| Module | snake_case | `user_service.py` |
| Class | PascalCase | `UserService` |
| Function | snake_case | `create_user` |
| Variable | snake_case | `user_id` |
| Constant | UPPER_SNAKE | `MAX_RETRIES` |

### API Endpoints

| Element | Style | Example |
|---------|-------|---------|
| Path | kebab-case | `/api/v1/user-profiles` |
| Query parameter | snake_case | `?user_id=123` |
| Body field | snake_case | `{"user_name": "..."}` |

### Database

| Element | Style | Example |
|---------|-------|---------|
| Table | snake_case, plural | `users`, `order_items` |
| Column | snake_case | `created_at` |
| Index | `ix_{table}_{column}` | `ix_users_email` |
| FK | `fk_{table}_{ref}` | `fk_orders_user_id` |

---

## Naming Process

### Step 1: Define Context

```markdown
Project: Restaurant table booking service
Context: booking
Domain: restaurant
```

### Step 2: Define Services

```markdown
| Service | Python Name | Docker Name | Port |
|---------|-------------|-------------|------|
| Business API | booking_api | booking-api | 8000 |
| Data API | booking_data | booking-data | 8001 |
| Telegram Bot | booking_bot | booking-bot | — |
| PostgreSQL | — | booking-postgres | 5432 |
| Redis | — | booking-redis | 6379 |
```

### Step 3: Define Models

```markdown
| Model | Table | Class |
|-------|-------|-------|
| Restaurant | restaurants | Restaurant |
| Booking | bookings | Booking |
| User | users | User |
```

### Step 4: Define Endpoints

```markdown
| Endpoint | Service | Path |
|----------|---------|------|
| List restaurants | booking_api | /api/v1/restaurants |
| Create booking | booking_api | /api/v1/bookings |
| Get restaurant | booking_data | /api/v1/restaurants/{id} |
```

---

## Naming Checklist

### Services
- [ ] Context is defined (2-15 characters, snake_case)
- [ ] All services use the `{context}_{type}` pattern
- [ ] Docker services use the `{context}-{type}` pattern
- [ ] Ports do not conflict

### Python Code
- [ ] Packages in snake_case
- [ ] Classes in PascalCase
- [ ] Functions in snake_case
- [ ] Constants in UPPER_SNAKE_CASE

### API
- [ ] Paths in kebab-case
- [ ] Parameters in snake_case
- [ ] Versioning (/api/v1/)

### Database
- [ ] Tables in snake_case, plural
- [ ] Columns in snake_case
- [ ] Indexes follow the ix_{table}_{column} pattern

---

## Naming Result

```markdown
## Project Context

| Parameter | Value |
|-----------|-------|
| Context | {context} |
| Domain | {domain} |

## Services

| Service | Python | Docker | Port |
|---------|--------|--------|------|
| Business API | {context}_api | {context}-api | 8000 |
| Data API | {context}_data | {context}-data | 8001 |

## Data Models

| Entity | Table | Python Class |
|--------|-------|--------------|
| {Entity} | {entities} | {Entity} |

## API Endpoints

| Service | Prefix |
|---------|--------|
| Business API | /api/v1/{resource} |
| Data API | /api/v1/{resource} |
```

---

## References

| Document | Description |
|----------|-------------|
| `knowledge/architecture/naming/README.md` | General rules |
| `knowledge/architecture/naming/services.md` | Service naming |
| `knowledge/architecture/naming/python.md` | Python conventions |
| `conventions.md` | Project conventions |
