import shutil
from pathlib import Path


LOCAL_DATABASE = Path("work_hours.db")

# Change this to your mounted NAS path
NAS_PATH = Path("/mnt/work-nas/working_hours")


def backup_to_nas():

    try:

        # NAS not mounted / unavailable
        if not NAS_PATH.exists():
            return False, (
                "NAS is not available."
            )

        NAS_PATH.mkdir(
            parents=True,
            exist_ok=True
        )

        destination = (
            NAS_PATH /
            "work_hours_latest.db"
        )

        shutil.copy2(
            LOCAL_DATABASE,
            destination
        )

        return True, (
            "Backup successful."
        )

    except Exception as error:

        return False, str(error)