import os

def check_migration_files(app_name):
    migrations_path = os.path.join(app_name, 'migrations')
    if not os.path.exists(migrations_path):
        print(f"No migrations directory found for app: {app_name}")
        return
    
    migration_files = [f for f in os.listdir(migrations_path) if f != '__init__.py' and f.endswith('.py')]
    
    if migration_files:
        print(f"Found additional migration files in {app_name}/migrations: {migration_files}")
    else:
        print(f"All migration files (except __init__.py) have been removed in {app_name}/migrations.")

apps = ['accounts', 'dashboard', 'reservations', 'main']  # List all your app names here

for app in apps:
    check_migration_files(app)
