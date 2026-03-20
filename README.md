
# Medical Reconciliation System

## Overview

This project is a **Medical Reconciliation System** designed to manage and reconcile patient data, medical records, and prescriptions efficiently. The system allows users to upload, validate, and reconcile medical information, ensuring data consistency and reducing errors.

---

## Setup Instructions

1. **Clone the repository**

```
git clone https://github.com/nightking-12/medical-reconcilitation.git
cd medical-reconcilitation
```

2. **Create and activate virtual environment (Python example)**

```
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```
pip install -r requirements.txt
```

4. **Run the project**

```
python main.py
```

*(Replace `main.py` with your entrypoint if different)*

---

## Architecture Overview

The system is structured into the following main components:

* **Data Ingestion**: Upload and parse medical records (CSV/JSON).
* **Reconciliation Engine**: Core logic to detect and merge duplicates or conflicting entries.
* **Database**: Stores patient records and reconciliation results.
* **API / Frontend**: Optional interface for users to interact with the system.

**Diagram (optional):**

```
[User] --> [Frontend/API] --> [Reconciliation Engine] --> [Database]
```

---

## Assumptions & Trade-offs

* Using **SQLite** for simplicity and quick setup instead of a full-scale DB like PostgreSQL.
* Focused on small datasets; performance optimizations for large-scale medical data not implemented.
* No authentication for initial version.

---

## Known Limitations & Next Steps

* Currently does not support real-time syncing across multiple users.
* Limited error handling for malformed records.
* Next steps:

  * Add user authentication
  * Support multiple data formats (HL7, FHIR)
  * Improve reconciliation algorithm for scalability

---

## Dataset / Seed Script

A small sample dataset is included in `data/sample.json`.
To generate seed data:

```
python scripts/seed_data.py
```

Sample format:

```json
[
  {"id": 1, "name": "Alice Smith", "prescription": "Drug A"},
  {"id": 2, "name": "Bob Johnson", "prescription": "Drug B"}
]
```

---

## Tests

Unit tests for the core reconciliation engine are in `tests/`:

```
pytest tests/
```

Example test:

```python
def test_reconcile_duplicate_records():
    records = [{"id":1,"name":"Alice"},{"id":1,"name":"Alice Smith"}]
    result = reconcile(records)
    assert len(result) == 1
```



## AI Tools Used

* **AI Assistance**: Used ChatGPT to generate boilerplate README, suggest project structure, and initial seed scripts.
* **Manual Review**: Edited all AI-generated content to match project specifics, fixed syntax, and added actual dataset format.
* **Disagreement Example**: AI suggested default SQLite file location, but I manually updated it to `data/sample.db` for consistency.

---

## License


