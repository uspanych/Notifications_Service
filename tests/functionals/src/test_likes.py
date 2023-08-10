import time

from functionals.settings import test_settings
import pytest
import json
from http import HTTPStatus


service_url = test_settings.service_url + '/api/v1/new_series'
smtp_url = test_settings.smtp_url
headers = {'Content-Type': 'application/json'}


pytestmark = pytest.mark.asyncio


async def test_send(client_session):
    query_data = {
        "user_id": "string",
        "user_name": "string",
        "user_email": "string@Nikita.biba",
        "like_subject": "string",
        "subject_id": "some_id"
    }

    async with client_session.post(service_url, data=json.dumps(query_data), headers=headers) as response:
        pass

    assert response.status == HTTPStatus.OK

    time.sleep(600)

    async with client_session.get(smtp_url + "/api/v2/messages") as response_smtp:
        result_smtp = await response_smtp.json(content_type=None)

    assert result_smtp.get('count') == 1
    assert result_smtp['items'][0]['Content']['Headers']['To'][0] == query_data.get('user_email')

    async with client_session.delete(smtp_url + '/api/v1/messages') as response_smtp:
        pass
