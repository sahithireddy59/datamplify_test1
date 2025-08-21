# # airflow_utils/airflow_user.py

# from flask_appbuilder.security.sqla.models import User, Role
# from airflow.app import create_app
# from airflow import settings

# app = create_app()
# sm = app.appbuilder.sm
# session = settings.Session()

# def create_static_role(role_name="standard_user"):
#     existing_role = sm.find_role(role_name)
#     if existing_role:
#         print(f"✅ Role '{role_name}' already exists.")
#         return

#     role = sm.add_role(role_name)

#     permissions = [
#         ("can_read", "DAG"),
#         ("can_edit", "DAG"),
#         ("can_trigger", "DAG"),
#         ("can_dag_read", "DAG"),
#         ("can_dag_edit", "DAG"),
#         ("can_log", "TaskInstance"),
#         ("can_read", "TaskInstance"),
#         ("can_delete", "DagRun"),
#     ]

#     for perm_name, view_menu in permissions:
#         sm.add_permission_role(role, perm_name, view_menu)

#     session.commit()
#     print(f"✅ Role '{role_name}' created with permissions.")

# def create_airflow_user(username, email, password, role_name="standard_user"):
#     existing_user = sm.find_user(username=username)
#     if existing_user:
#         print(f"User '{username}' already exists.")
#         return

#     role = sm.find_role(role_name)
#     if not role:
#         print(f"❌ Role '{role_name}' not found.")
#         return

#     sm.add_user(
#         username=username,
#         first_name=username.capitalize(),
#         last_name="User",
#         email=email,
#         role=role,
#         password=password,
#     )

#     session.commit()
#     print(f"✅ Created Airflow user '{username}' with role '{role_name}'.")
