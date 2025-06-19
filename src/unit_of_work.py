from asyncio import shield

from src.adapters.database.repository_gateway import (
    RepositoriesGateway,
)
from src.adapters.database.session import async_session_maker
from src.utils.unit_of_work import UnitOfWorkProtocol


class UnitOfWork(UnitOfWorkProtocol):

    def __init__(self):
        self.db_session_factory = async_session_maker

    async def __aenter__(self):
        self.db_session = self.db_session_factory()
        self.repositories = RepositoriesGateway(self.db_session)

        return self

    async def __aexit__(self, *args):
        await self.rollback()
        await shield(self.db_session.close())

    async def commit(self):
        await self.db_session.commit()

    async def rollback(self):
        await self.db_session.rollback()
