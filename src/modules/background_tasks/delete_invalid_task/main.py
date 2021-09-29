from datetime import datetime
import aiofiles
import aiofiles.os

from uuid import UUID
from modules.language_detection_request.database.language_detection_history.repository import LanguageDetectionHistoryRepository
from modules.translation_request.database.translation_history.repository import TranslationHistoryRepository
from infrastructure.configs.main import GlobalConfig, get_cnf, get_mongodb_instance
from infrastructure.configs.task import (
    StepStatusEnum
)
from modules.task.database.task_result.repository import TasktResultRepository
from modules.task.database.task.repository import TaskRepository
from core.utils.common import chunk_arr
from core.utils.file import delete_files, get_task_result_full_file_path
import asyncio
from infrastructure.adapters.logger import Logger

config: GlobalConfig = get_cnf()
db_instance = get_mongodb_instance()

translation_history_repository = TranslationHistoryRepository()
language_detection_history_repository = LanguageDetectionHistoryRepository()
task_repository = TaskRepository()
task_result_repository = TasktResultRepository()

logger = Logger('Task: delete_invalid_task')


async def main():

    logger.debug(
        msg=f'New task delete_invalid_task run in {datetime.now()}'
    )

    print(f'New task delete_invalid_task run in {datetime.now()}')

    try:

        invalid_tasks = await task_repository.find_many(
            params={
                '$or': [
                    {
                        "step_status": {
                            "$in": [StepStatusEnum.cancelled.value,  StepStatusEnum.closed.value]
                        }
                    },
                    {
                        "expired_date": {
                            "$lt": datetime.now()
                        }
                    }
                ]
            }
        )

        invalid_tasks_ids = list(map(lambda task: task.id.value, invalid_tasks)) if not invalid_tasks is None else []

        invalid_tasks_results = []

        invalid_tasks_results = await task_result_repository.find_many(
            params={
                "task_id": {
                    "$in": [UUID(task_id) for task_id in invalid_tasks_ids]
                }
            }
        )


        invalid_tasks_file_paths = list(map(lambda task: task.props.file_path, invalid_tasks_results))

        if len(invalid_tasks_ids) == 0:
            logger.debug(
                msg=f'An task delete_invalid_task end in {datetime.now()}\n')

            print(f'An task delete_invalid_task end in {datetime.now()}\n')
            return

        async with db_instance.session() as session:

            async with session.start_transaction():

                clean_request = []

                clean_request.append(
                    language_detection_history_repository.delete_many_by_condition(
                        conditions=[{"task_id": invalid_tasks_ids}]
                    )
                )

                clean_request.append(
                    translation_history_repository.delete_many_by_condition(
                        conditions=[{"task_id": invalid_tasks_ids}]
                    )
                )

                clean_request.append(
                    task_result_repository.delete_many_by_condition(
                        conditions=[{"task_id": invalid_tasks_ids}]
                    )
                )

                clean_request.append(
                    task_repository.delete_many_by_condition(
                        conditions=[{"_id": invalid_tasks_ids}]
                    )
                )

                await delete_files(invalid_tasks_file_paths)

                await asyncio.gather(*clean_request)

    except Exception as e:
        logger.error(e)

        print(e)

    logger.debug(
        msg=f'An task delete_invalid_task end in {datetime.now()}\n'
    )
