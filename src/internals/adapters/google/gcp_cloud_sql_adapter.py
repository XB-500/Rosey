import os
from mabel.logging import get_logger  # type:ignore
from ...errors import MissingDependencyError

try:
    import psycopg2  # type:ignore
except ImportError:
    psycopg2 = None


class DatabaseConnection(object):  # pragma: no cover
    def __init__(self):
        """
        Wraps connection handling in a context manager
        """
        self.connector = None

    def __enter__(self):
        if not psycopg2:
            raise MissingDependencyError(
                "Library `psycopg2` is missing, install or include in requirements.txt"
            )
        self.connector = psycopg2.connect(
            host=os.environ.get("POSTGRES_HOST"),
            port=os.environ.get("POSTGRES_PORT"),
            user=os.environ.get("POSTGRES_USER"),
            password=os.environ.get("POSTGRES_PASSWORD"),
        )
        return self.connector

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_tb is None:
            self.connector.commit()
        else:
            self.connector.rollback()
        self.connector.close()


class CloudSqlAdapter:  # pragma: no cover
    @staticmethod
    def run(sql, vals=()):
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, vals)
                conn.commit()
                return cursor.rowcount
        except (Exception, psycopg2.DatabaseError) as error:
            get_logger().error(
                f"Error in `CloudSqlAdapter` - {type(error).__name__}: {error}"
            )
            raise error

    @staticmethod
    def create(sql, vals=()):
        return CloudSqlAdapter.run(sql, vals)

    @staticmethod
    def read(sql, vals=()):
        try:
            with DatabaseConnection() as conn:
                cursor = conn.cursor()
                cursor.execute(sql, vals)
                row = cursor.fetchone()
                while row is not None:
                    yield row
                    row = cursor.fetchone()
        except (Exception, psycopg2.DatabaseError) as error:
            get_logger().error(
                f"Error in `CloudSqlAdapter` - {type(error).__name__}: {error}"
            )
            raise error

    @staticmethod
    def update(sql, vals=()):
        return CloudSqlAdapter.create(sql, vals)

    @staticmethod
    def delete(sql, vals=()):
        return CloudSqlAdapter.create(sql, vals)

    @staticmethod
    def run_no_transaction(sql):
        """
        Don't use this unless you know what you're doing
        """
        try:
            with DatabaseConnection() as conn:
                conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
                conn.cursor().execute(sql)
        except (Exception, psycopg2.DatabaseError) as error:
            get_logger().error(
                f"Error in `CloudSqlAdapter` - {type(error).__name__}: {error}"
            )
            raise error
