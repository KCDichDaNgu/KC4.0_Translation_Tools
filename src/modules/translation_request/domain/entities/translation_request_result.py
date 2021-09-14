from pydantic import Field
from pydantic.class_validators import root_validator, validator
from typing import Any, Optional, Union

from pydantic.fields import PrivateAttr
from core.base_classes.entity import Entity
from pydantic.main import BaseModel
from core.value_objects import ID

import aiofiles
import json, os

class TranslationRequestResultProps(BaseModel):
    
    task_id: ID = Field(...)
    step: str = Field(...)
    file_path: Optional[str]

class TranslationRequestResultEntity(Entity[TranslationRequestResultProps]):

    async def save_request_result_to_file(self, dir_path, file_name, file_extension, content):

        async with aiofiles.open(f'{dir_path}/{file_name}.{file_extension}', 'w+') as f:
            json.dump(content, f)

            f.close()

        self.props.file_path = file_name

    async def read_data_from_file(self):

        if not self.check_if_file_exists():

            raise FileNotFoundError('File not found')

        async with aiofiles.open(self.props.file_path) as f:
            
            data = json.load(f)

            f.close()

            return data

    async def check_if_file_exists(self):

        return os.path.isfile(self.props.file_path)