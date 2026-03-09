import os
import sys
import logging
from github import Github
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def main():
    moscow_tz = ZoneInfo("Europe/Moscow")
    deadlines = {
        "lab:clang": datetime(2025, 3, 17, hour=19, tzinfo=moscow_tz),
        "lab:llvm ir": datetime(2099, 6, 1, hour=19, tzinfo=moscow_tz),
        "lab:backend": datetime(2099, 6, 1, hour=19, tzinfo=moscow_tz),
        "lab:mlir": datetime(2099, 6, 1, hour=19, tzinfo=moscow_tz),
    }
    lab_labels = ["lab:clang", "lab:llvm ir", "lab:backend", "lab:mlir"]

    gh = Github(os.environ["GITHUB_TOKEN"])
    repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
    pr = repo.get_pull(int(os.environ["PR_NUMBER"]))
    current_labels = [label.name for label in pr.get_labels()]
    lab_label = next((l for l in current_labels if l in lab_labels), None)

    logger.log(f"Repository: {repo}, PR: {pr}, Labels: {current_labels}")

    if not lab_label:
        logger.info("Lab label not found")
        return

    pr_created_date = pr.created_at.astimezone(moscow_tz)
    current_date = datetime.now(moscow_tz)
    deadline_date = deadlines[lab_label]
    time_before_deadline = deadline_date - pr_created_date
    LABEL_LOW_PRIORITY = "low priority"
    LABEL_DELAYED = "delayed"

    logger.info(
        f"Lab: {lab_label}, Created: {pr_created_date}, Deadline: {deadline_date}"
    )
    logger.info(f"Time before deadline: {time_before_deadline}")

    if current_date > deadline_date:
        if LABEL_DELAYED not in current_labels:
            logger.info("Adding label: delayed")
            pr.add_to_labels(LABEL_DELAYED)
        if LABEL_LOW_PRIORITY in current_labels:
            logger.info("Removing label: low priority")
            pr.remove_from_labels(LABEL_LOW_PRIORITY)
    elif time_before_deadline < timedelta(hours=72):
        if LABEL_LOW_PRIORITY not in current_labels:
            logger.info("Adding label: low priority")
            pr.add_to_labels(LABEL_LOW_PRIORITY)


if __name__ == "__main__":
    sys.exit(main())
