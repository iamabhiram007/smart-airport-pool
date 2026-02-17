# Smart Airport Ride Pooling Backend

A backend system that automatically groups airport passengers into shared rides while minimizing detours and dynamically adjusting pricing based on ride occupancy and demand.

---

## Features

- Shared cab matching (similar to Uber Pool)
- Seat and luggage constraint enforcement
- Detour tolerance filtering
- Dynamic pricing based on occupancy & demand
- PostgreSQL persistent storage
- Concurrency-safe booking (no overbooking)
- REST APIs with Swagger documentation

---

## Tech Stack

- Backend Framework: FastAPI (Python)
- Database: PostgreSQL
- ORM: SQLAlchemy
- API Docs: Swagger / OpenAPI
- Algorithm: Greedy bin-packing + geo-distance matching

---

## How It Works

1. Passenger sends ride request
2. System finds nearby ride group
3. Passenger joins ride OR new ride created
4. Price calculated dynamically
5. Seat allocated atomically using DB locking

---

## Pricing Formula

Price = (Distance × Base Rate ÷ Occupancy) × Surge

Pooling always reduces price.

---

## Concurrency Safety

Uses PostgreSQL row-level locking:

SELECT ... FOR UPDATE

Prevents multiple users booking last seat.

---

## APIs

POST /ride/request
GET /ride/groups

Swagger:
http://127.0.0.1:8000/docs

---

## Run Locally

Create DB:
CREATE DATABASE ride_pool;

Run server:
uvicorn main:app --reload
