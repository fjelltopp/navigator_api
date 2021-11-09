import factory
from navigator_api import model as _model


class WorklowFactory(factory.alchemy.SQLAlchemyModelFactory):
    class Meta:
        model = _model.Workflow
        sqlalchemy_session = _model.db.session
        sqlalchemy_get_or_create = ('dataset_id','user_id')
        sqlalchemy_session_persistence = 'commit'
    id = factory.Sequence(lambda n: int(n))
    decision_engine_id = factory.Faker('uuid4')
    dataset_id = factory.Faker('uuid4')
    user_id = factory.Faker('uuid4')
    skipped_tasks = []

