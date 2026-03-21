from src.db.session import analytics
from typing import List, Dict

class AnalyticsRepository:
    @staticmethod
    def save_click(click_data: dict) -> bool:
        result = analytics.insert_one(click_data)
        return result.acknowledged

    @staticmethod
    def get_all_clicks() -> List[dict]:
        cursor = analytics.find({}, {"_id": 0})
        return list(cursor)

    @staticmethod
    def get_stats() -> Dict:
        # Agregado simples para facilitar a retirada dos dados
        pipeline = [
            {
                "$group": {
                    "_id": {
                        "variant": "$variant",
                        "elementId": "$elementId"
                    },
                    "count": {"$sum": 1},
                    "emails": {"$push": "$email"}
                }
            }
        ]
        
        results = list(analytics.aggregate(pipeline))
        
        # Limpar os emails (remover None e duplicados)
        for res in results:
            res["emails"] = list(set([e for e in res["emails"] if e]))
            
        return {"stats": results}

analytics_repository = AnalyticsRepository()
