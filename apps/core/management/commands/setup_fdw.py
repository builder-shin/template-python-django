import os
import logging

from django.core.management.base import BaseCommand
from django.db import connection

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Setup Foreign Data Wrapper (FDW) for cross-database access to auth service"

    def add_arguments(self, parser):
        parser.add_argument("--teardown", action="store_true", help="Remove FDW configuration")
        parser.add_argument("--test", action="store_true", help="Test FDW connectivity")
        parser.add_argument("--refresh", action="store_true", help="Teardown and re-setup FDW")

    def handle(self, *args, **options):
        if options["refresh"]:
            self._teardown()
            self._setup()
        elif options["teardown"]:
            self._teardown()
        elif options["test"]:
            self._test()
        else:
            self._setup()

    def _get_auth_db_config(self):
        return {
            "host": os.environ.get("AUTH_DB_HOST", "localhost"),
            "port": os.environ.get("AUTH_DB_PORT", "5432"),
            "dbname": os.environ.get("AUTH_DB_NAME", "auth_dev"),
            "user": os.environ.get("AUTH_DB_USER", "postgres"),
            "password": os.environ.get("AUTH_DB_PASSWORD", ""),
        }

    def _get_local_user(self):
        return os.environ.get("DEV_DATABASE_USERNAME", os.environ.get("DATABASE_USER", "postgres"))

    def _setup(self):
        config = self._get_auth_db_config()
        local_user = self._get_local_user()

        self.stdout.write("Setting up FDW...")

        try:
            with connection.cursor() as cursor:
                cursor.execute("CREATE EXTENSION IF NOT EXISTS postgres_fdw;")

                cursor.execute("CREATE SCHEMA IF NOT EXISTS auth;")

                cursor.execute("DROP SERVER IF EXISTS auth_server CASCADE;")
                cursor.execute(
                    f"CREATE SERVER auth_server FOREIGN DATA WRAPPER postgres_fdw "
                    f"OPTIONS (host '{config['host']}', port '{config['port']}', dbname '{config['dbname']}');"
                )

                cursor.execute(
                    f"CREATE USER MAPPING IF NOT EXISTS FOR {local_user} "
                    f"SERVER auth_server "
                    f"OPTIONS (user '{config['user']}', password '{config['password']}');"
                )

                foreign_tables = {
                    "users": """
                        id UUID,
                        email VARCHAR(255),
                        name VARCHAR(255),
                        workspace_id UUID,
                        auth_method VARCHAR(50),
                        verified_at TIMESTAMPTZ,
                        mobile VARCHAR(50),
                        job_id UUID
                    """,
                    "user_consents": """
                        id UUID,
                        user_id UUID,
                        consent_type VARCHAR(100),
                        is_agreed BOOLEAN,
                        consent_version VARCHAR(50),
                        agreed_at TIMESTAMPTZ,
                        withdrawn_at TIMESTAMPTZ
                    """,
                    "workspaces": """
                        id UUID,
                        kind VARCHAR(50),
                        name VARCHAR(255),
                        domain VARCHAR(255),
                        status VARCHAR(50),
                        invite_code VARCHAR(100),
                        created_at TIMESTAMPTZ,
                        updated_at TIMESTAMPTZ
                    """,
                    "workspace_members": """
                        id UUID,
                        workspace_id UUID,
                        user_id UUID,
                        role VARCHAR(50),
                        member_status VARCHAR(50),
                        invited_at TIMESTAMPTZ,
                        joined_at TIMESTAMPTZ,
                        invited_by UUID,
                        status_changed_at TIMESTAMPTZ
                    """,
                }

                for table_name, columns in foreign_tables.items():
                    cursor.execute(f"DROP FOREIGN TABLE IF EXISTS auth.{table_name};")
                    cursor.execute(
                        f"CREATE FOREIGN TABLE auth.{table_name} ({columns}) "
                        f"SERVER auth_server OPTIONS (schema_name 'public', table_name '{table_name}');"
                    )

            self.stdout.write(self.style.SUCCESS("FDW setup complete."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FDW setup failed: {e}"))
            raise

    def _teardown(self):
        self.stdout.write("Tearing down FDW...")

        try:
            with connection.cursor() as cursor:
                cursor.execute("DROP SCHEMA IF EXISTS auth CASCADE;")
                cursor.execute("DROP SERVER IF EXISTS auth_server CASCADE;")

            self.stdout.write(self.style.SUCCESS("FDW teardown complete."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FDW teardown failed: {e}"))
            raise

    def _test(self):
        self.stdout.write("Testing FDW connectivity...")

        try:
            with connection.cursor() as cursor:
                tables = ["users", "user_consents", "workspaces", "workspace_members"]
                for table in tables:
                    cursor.execute(f"SELECT COUNT(*) FROM auth.{table};")
                    count = cursor.fetchone()[0]
                    self.stdout.write(f"  auth.{table}: {count} rows")
            self.stdout.write(self.style.SUCCESS("FDW test passed."))

        except Exception as e:
            self.stdout.write(self.style.ERROR(f"FDW test failed: {e}"))
            raise
