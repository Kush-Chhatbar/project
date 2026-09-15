from app.models import SLARule

class SLARuleFactory:
    
    @staticmethod
    def create(priority, resolution_target_minutes):
        return SLARule(
            priority=priority,
            resolution_target_minutes=resolution_target_minutes,
            is_active=True
        )

    @staticmethod
    def create_batch(sla_rules):
        sla_rule_objects = []

        for sla_rule in sla_rules:
            rule = SLARuleFactory.create(
                priority=sla_rule["priority"],
                resolution_target_minutes=sla_rule["resolution_target_minutes"]
            )

            sla_rule_objects.append(rule)

        return sla_rule_objects