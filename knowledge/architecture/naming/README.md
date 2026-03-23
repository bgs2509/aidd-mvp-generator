# Naming Conventions

> **Purpose**: Unified naming rules across the project.

---

## General Principles

```
1. Consistency — same rules everywhere
2. Readability — clear names
3. Context — name reflects purpose
```

---

## Summary Table

| Element | Style | Example |
|---------|-------|--------|
| Python package | snake_case | `booking_api` |
| Python module | snake_case | `user_service.py` |
| Python class | PascalCase | `UserService` |
| Python function | snake_case | `create_user` |
| Python variable | snake_case | `user_id` |
| Python constant | UPPER_SNAKE | `MAX_RETRIES` |
| Docker service | kebab-case | `booking-api` |
| API path | kebab-case | `/api/v1/user-profiles` |
| Query parameter | snake_case | `?user_id=123` |
| JSON field | snake_case | `{"user_name": "..."}` |
| DB table | snake_case, plural | `users` |
| DB column | snake_case | `created_at` |
| Environment variable | UPPER_SNAKE | `DATABASE_URL` |

---

## Project Context

```
{context} — short project name

Requirements:
- 2-15 characters
- snake_case
- Descriptive

Examples:
- booking
- finance
- inventory
- orders
```

---

## Domain

```
{domain} — primary entity

Requirements:
- Noun
- Singular
- snake_case

Examples:
- restaurant
- transaction
- product
- order
```

---

## Detailed Rules

- `services.md` — service naming
- `python.md` — Python naming

---

## Quick Reference

### Services

```
Python package:  {context}_{type}     -> booking_api
Docker:          {context}-{type}     -> booking-api
Directory:       services/{context}_{type}/
```

### Models

```
Class:           {Entity}             -> Restaurant
Table:           {entities}           -> restaurants
File:            {entity}.py          -> restaurant.py
```

### API

```
Path:            /api/v1/{resources}  -> /api/v1/restaurants
Endpoint:        POST /api/v1/{resources}/{id}
```

### Tests

```
File:            test_{module}.py     -> test_user_service.py
Class:           Test{Feature}        -> TestUserCreation
Function:        test_{scenario}      -> test_create_user_success
```
