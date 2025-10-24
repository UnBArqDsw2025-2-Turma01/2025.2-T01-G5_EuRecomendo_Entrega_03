from .factories import StandardUserFactory, StaffUserFactory, UserFactory

def get_factory(kind: str) -> UserFactory:
    if kind == "staff":
        return StaffUserFactory()
    return StandardUserFactory()
