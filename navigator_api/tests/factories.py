import factory
from navigator_api import model


class WorklowFactory(factory.Factory):
    class Meta:
        model = model.Workflow
    id = factory.Sequence(lambda n: int(n))
    decision_engine_id = factory.Faker('uuid4')
    dataset_id = factory.Faker('uuid4')
    user_id = factory.Faker('uuid4')
    skipped_tasks = []

