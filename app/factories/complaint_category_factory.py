from app.models.complaint_category import ComplaintCategory

class ComplaintCategoryFactory:
    @staticmethod
    def create(name, description):
        return ComplaintCategory(
            name=name,
            description=description,
            is_active=True
        )

    @staticmethod
    def create_batch(categories):
        complaint_categories = []

        for category in categories:
            complaint_category = ComplaintCategoryFactory.create(
                name=category["name"],
                description=category["description"]
            )

            complaint_categories.append(complaint_category)

        return complaint_categories
