from sqlalchemy import create_engine, pool 
from sqlalchemy.orm import sessionmaker

from twisted_decorators import toThread

class DBDefer(object):

    def __init__(self, dsn, poolclass=pool.SingletonThreadPool):
        self.engine = create_engine(dsn, poolclass=poolclass)
    
    def __call__(self, func):

        @toThread
        def wrapper(*args, **kwargs):
            session = sessionmaker(bind=self.engine)()
            try:
                return func(session=session, *args, **kwargs)
            except:
                session.rollback()
                raise
            finally:
                session.close()

        return wrapper