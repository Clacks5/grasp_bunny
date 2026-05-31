import os


DB_CONFIG = {
    "host": os.getenv("GRASP_BUNNY_DB_HOST", "localhost"),
    "user": os.getenv("GRASP_BUNNY_DB_USER", "root"),
    "password": os.getenv("GRASP_BUNNY_DB_PASSWORD", ""),
    "database": os.getenv("GRASP_BUNNY_DB_NAME", "grasp_bunny"),
}
