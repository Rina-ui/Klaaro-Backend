from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.adapters.dependencies import get_current_user
from app.infrastructure.database import get_db
from app.infrastructure.repositories.document_repository_impl import DocumentRepositoryImpl
from app.infrastructure.repositories.rapport_repository_impl import RapportRepositoryImpl
from app.infrastructure.repositories.decision_repository_impl import DecisionRepositoryImpl
from app.infrastructure.repositories.alerte_repository_impl import AlerteRepositoryImpl

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/summary")
def get_dashboard_summary(current_user=Depends(get_current_user), db: Session = Depends(get_db)):
    doc_repo = DocumentRepositoryImpl(db)
    rapport_repo = RapportRepositoryImpl(db)
    decision_repo = DecisionRepositoryImpl(db)
    alerte_repo = AlerteRepositoryImpl(db)

    documents = doc_repo.find_by_user_id(current_user.id)
    rapports = rapport_repo.find_by_user_id(current_user.id)
    decisions = decision_repo.find_by_user_id(current_user.id)
    alertes = alerte_repo.find_by_user_id(current_user.id)

    total_files = len(documents)
    analyses_count = len([r for r in rapports if r.type == "preprocessing"])
    predictions_count = len([r for r in rapports if r.type == "prediction"])
    decisions_count = len(decisions)
    alertes_count = len(alertes)

    # Volume par jour sur les 7 derniers jours, pour le sparkline du dashboard
    today = datetime.utcnow().date()
    daily_counts = {(today - timedelta(days=i)).isoformat(): 0 for i in range(6, -1, -1)}
    for doc in documents:
        day = doc.upload_date.date().isoformat()
        if day in daily_counts:
            daily_counts[day] += 1

    recent_files = sorted(documents, key=lambda d: d.upload_date, reverse=True)[:5]

    # Activité récente : fusion alertes + rapports + décisions, triée par date, top 6
    activity_items = []
    for a in alertes:
        activity_items.append({
            "kind": "alerte",
            "text": a.type,
            "sub": a.content[:60] if a.content else "",
            "date": a.send_date,
            "niveau_gravite": a.niveau_gravite,
        })
    for r in rapports:
        activity_items.append({
            "kind": "rapport",
            "text": "Analyse générée" if r.type == "preprocessing" else "Prédiction générée",
            "sub": r.type,
            "date": r.date_generation,
        })
    for d in decisions:
        activity_items.append({
            "kind": "decision",
            "text": "Décision enregistrée",
            "sub": d.content[:60] if d.content else "",
            "date": d.date,
        })

    activity_items.sort(key=lambda x: x["date"], reverse=True)
    recent_activity = activity_items[:6]

    return {
        "uploadedFilesCount": total_files,
        "analysesCount": analyses_count,
        "predictionsCount": predictions_count,
        "decisionsCount": decisions_count,
        "alertesCount": alertes_count,
        "recentFiles": [
            {
                "id": d.id,
                "name": d.name,
                "taille": d.taille,
                "type": d.type,
                "upload_date": d.upload_date.isoformat(),
            }
            for d in recent_files
        ],
        "recentActivity": [
            {
                "kind": item["kind"],
                "text": item["text"],
                "sub": item["sub"],
                "date": item["date"].isoformat(),
                "niveau_gravite": item.get("niveau_gravite"),
            }
            for item in recent_activity
        ],
        "uploadsByDay": [{"date": day, "count": count} for day, count in daily_counts.items()],
    }