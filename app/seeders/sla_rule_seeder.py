from app.extensions import db
from app.factories.sla_rule_factory import SLARuleFactory

def seed_sla_rules():

    sla_rules = [
        {
            "priority": "Critical",
            "resolution_target_minutes": 60
        },
        {
            "priority": "High",
            "resolution_target_minutes": 240
        },
        {
            "priority": "Medium",
            "resolution_target_minutes": 720
        },
        {
            "priority": "Low",
            "resolution_target_minutes": 1440
        }
    ]

    sla_rule_objects = SLARuleFactory.create_batch(sla_rules)

    db.session.add_all(sla_rule_objects)
    db.session.commit()

    print(f"{len(sla_rule_objects)} SLA rules created.")