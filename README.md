# Smart Airport Ride Pooling Backend

A backend system that automatically groups airport passengers into shared rides while minimizing detours and dynamically adjusting pricing based on ride occupancy and demand.

---

## Features

* Shared cab matching (similar to Uber Pool)
* Seat and luggage constraint enforcement
* Detour tolerance filtering
* Dynamic pricing based on occupancy & demand
* PostgreSQL persistent storage
* Concurrency-safe booking (no overbooking)
* REST APIs with Swagger documentation

---

## Tech Stack

* **Python:** 3.10+
* **Backend Framework:** FastAPI
* **Database:** PostgreSQL
* **ORM:** SQLAlchemy
* **API Docs:** Swagger / OpenAPI
* **Algorithm:** Greedy bin-packing + geo-distance matching

---

## How It Works

1. Passenger sends ride request
2. System finds nearby ride group
3. Passenger joins ride OR new ride created
4. Price calculated dynamically
5. Seat allocated atomically using DB transaction

---

## Pricing Formula

Price = (Distance × Base Rate ÷ Occupancy) × Surge

Pooling always reduces price.

---

## Concurrency Safety

Seat allocation happens inside a database transaction.
The ride row is locked during update, ensuring only one request can modify capacity at a time.

Result:

* No negative seat counts
* No double booking
* Safe under concurrent requests

---

## APIs

### Request Ride

`POST /ride/request`

### List Active Ride Groups

`GET /ride/groups`

Swagger UI:
http://127.0.0.1:8000/docs

---

## Example Request

```json
POST /ride/request

{
  "passenger_id": "p1",
  "pickup": { "lat": 28.556, "lng": 77.100 },
  "drop": { "lat": 28.600, "lng": 77.200 },
  "seats": 1,
  "luggage": 1
}
```

---

## Run Locally

### 1. Create database

```sql
CREATE DATABASE ride_pool;
```

### 2. Set environment variable

Use your local PostgreSQL username:

```bash
export DATABASE_URL="postgresql://<your_db_user>@localhost:5432/ride_pool"
```

Example:

```bash
export DATABASE_URL="postgresql://postgres@localhost:5432/ride_pool"
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize tables

```bash
python init_db.py
```

### 5. Run server

```bash
uvicorn main:app --reload
```

Open:
http://127.0.0.1:8000/docs

---

## Database Schema

### ride_groups

| Column            | Type  | Description                |
| ----------------- | ----- | -------------------------- |
| id                | UUID  | Unique ride identifier     |
| available_seats   | INT   | Remaining seat capacity    |
| available_luggage | INT   | Remaining luggage capacity |
| pickup_lat        | FLOAT | Pickup latitude            |
| pickup_lng        | FLOAT | Pickup longitude           |

---

## Indexing Strategy

```sql
CREATE INDEX idx_pickup_location ON ride_groups(pickup_lat, pickup_lng);
CREATE INDEX idx_available_seats ON ride_groups(available_seats);
CREATE INDEX idx_active_rides ON ride_groups(available_seats) WHERE available_seats > 0;
```

Purpose:

* Faster ride matching
* Avoid full table scans
* Maintain <300ms response time at high load

---

## Concurrency Handling Strategy

* Seat allocation inside DB transaction
* Only one request updates a ride row at a time
* If ride becomes full → new ride created

Guarantees atomic booking even under simultaneous requests.

---

## High Level Architecture

Client → Load Balancer → FastAPI Servers → PostgreSQL

### Components

**Client**
Sends ride requests via REST API.

**Load Balancer**
Distributes traffic across backend instances.

**FastAPI Service (Stateless)**

* Validation
* Matching algorithm
* Pricing calculation
* Transactional booking

**PostgreSQL (Source of Truth)**

* Stores ride groups
* Ensures consistency
* Handles row locking

**Future Improvement**
Redis geo-index for faster nearby ride lookup.

---

## Scalability

* Stateless backend allows horizontal scaling
* Matching complexity bounded by airport zone
* Supports ~100 RPS with multiple instances
* Database ensures strong consistency
