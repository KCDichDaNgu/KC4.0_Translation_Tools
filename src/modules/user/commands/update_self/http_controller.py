from interface_adapters.base_classes.response import ResponseBase
from modules.user.commands.update_self.command import UpdateUserCommand
from sanic.request import Request
from infrastructure.configs.message import MESSAGES

from sanic import response
from modules.user.commands.update_self.request_dto import UpdateUserRequestDto
from infrastructure.configs.main import StatusCodeEnum, GlobalConfig, get_cnf

from sanic_openapi import doc
from sanic.views import HTTPMethodView
from modules.user.dtos.auth_user_response import AuthUserResponse

from core.middlewares.authentication.core import login_required

config: GlobalConfig = get_cnf()
APP_CONFIG = config.APP_CONFIG

class UpdateSelf(HTTPMethodView):

    def __init__(self) -> None:
        super().__init__()
        from modules.user.commands.update_self.service import UserService
        self.__user_service = UserService()

    @doc.summary(APP_CONFIG.ROUTES['user.update_self']['summary'])
    @doc.description(APP_CONFIG.ROUTES['user.update_self']['desc'])
    @doc.consumes(UpdateUserRequestDto, location="body", required=True)
    @doc.produces(ResponseBase)
    @login_required
    async def put(self, request: Request):
        try:
            data = request.json
            # create new user
            
            command = UpdateUserCommand(
                id=data['id'],
                first_name=data['first_name'],
                last_name=data['last_name'],
                avatar=data['avatar'],
            )
            user = await self.__user_service.update_user(command)

            if user is None:
                return response.json(
                    status=400,
                    body={
                        'code': StatusCodeEnum.failed.value,
                        'message': MESSAGES['failed']
                    }
                )
            return response.json(body={
                'code': StatusCodeEnum.success.value,
                'message': MESSAGES['success']
            })

        except Exception as error:
            print(error)
            return response.json(
                status=500,
                body={
                    'code': StatusCodeEnum.failed.value,
                    'message': MESSAGES['failed']
                }
            )