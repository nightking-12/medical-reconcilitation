from fastapi import FastAPI
from pymongo import MongoClient
from pydantic import BaseModel
from typing import List
from datetime import datetime, timedelta

app = FastAPI()

# --- MongoDB connection ---
client = MongoClient("mongodb://localhost:27017")  # adjust if needed
db = client["med_reconciliation"]

patients_col = db["patients"]
snapshots_col = db["medication_snapshots"]
conflicts_col = db["conflicts"]

# --- Pydantic models ---
class Dose(BaseModel):
    value: float
    unit: str

class Medication(BaseModel):
    name: str
    dose: Dose
    frequency: str
    status: str  # active/stopped

class MedicationSnapshotIn(BaseModel):
    patient_id: str
    source: str
    medications: List[Medication]

# --- Ingestion endpoint ---
@app.post("/ingest_snapshot")
def ingest_snapshot(snapshot: MedicationSnapshotIn):
    # Normalize medication names and units
    for med in snapshot.medications:
        med.name = med.name.strip().lower()
        med.dose.unit = med.dose.unit.lower()

    # Determine version number for this patient+source
    last_snapshot = snapshots_col.find_one(
        {"patient_id": snapshot.patient_id, "source": snapshot.source},
        sort=[("version", -1)]
    )
    version = (last_snapshot["version"] if last_snapshot else 0) + 1

    # Prepare snapshot document
    doc = snapshot.dict()
    doc["version"] = version
    doc["created_at"] = datetime.utcnow()
    doc["updated_at"] = doc["created_at"]

    snapshots_col.insert_one(doc)

    # Run conflict detection
    detect_conflicts(snapshot.patient_id)

    return {"status": "success", "version": version}

# --- Conflict detection ---
def detect_conflicts(patient_id: str):
    snapshots = list(snapshots_col.find({"patient_id": patient_id}))
    meds_by_source = {}
    
    for snap in snapshots:
        # Map med name to medication info for each source
        meds_by_source[snap["source"]] = {m["name"]: m for m in snap["medications"]}

    # Collect all unique medication names across sources
    meds_names = set()
    for meds in meds_by_source.values():
        meds_names.update(meds.keys())

    # Clear previous conflicts for this patient to avoid duplicates
    conflicts_col.delete_many({"patient_id": patient_id})

    for med_name in meds_names:
        doses = []
        for source, meds in meds_by_source.items():
            if med_name in meds:
                dose_info = meds[med_name]["dose"]
                doses.append({
                    "source": source,
                    "dose": f"{dose_info['value']} {dose_info['unit']}"
                })

        # Detect dose mismatch conflicts
        if len(doses) > 1 and len(set(d["dose"] for d in doses)) > 1:
            created_at = datetime.utcnow()
            conflicts_col.insert_one({
                "patient_id": patient_id,
                "clinic_id": "clinic_x",  # TODO: Replace with actual clinic_id as appropriate
                "conflict_type": "dose_mismatch",
                "drug_name": med_name,
                "details": {"sources": doses},
                "status": "unresolved",
                "created_at": created_at,
                "updated_at": created_at
            })

# --- Reporting endpoint: unresolved conflicts per clinic ---
@app.get("/report/unresolved/{clinic_id}")
def report_unresolved(clinic_id: str):
    pipeline = [
        {"$match": {"clinic_id": clinic_id, "status": "unresolved"}},
        {"$group": {"_id": "$patient_id", "count": {"$sum": 1}}}
    ]
    result = list(conflicts_col.aggregate(pipeline))
    return result

# --- Reporting endpoint: patients with ≥2 conflicts in last 30 days ---
@app.get("/report/conflicts_30days/{clinic_id}")
def report_conflicts_30days(clinic_id: str):
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)

    pipeline = [
        {
            "$match": {
                "clinic_id": clinic_id,
                "status": "unresolved",
                "created_at": {"$gte": thirty_days_ago}
            }
        },
        {
            "$group": {
                "_id": "$patient_id",
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {"count": {"$gte": 2}}
        }
    ]

    result = list(conflicts_col.aggregate(pipeline))
    return result