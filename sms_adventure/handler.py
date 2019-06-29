import os
from typing import Any, Dict

from sms_adventure.s3_bucket_saves import S3BucketSavesGateway
from sms_adventure.definitions import Context
from sms_adventure.game import GameGateway
from sms_adventure.use_adventure import do_sms_command
from sms_adventure.exceptions import CommandPolicyViolationError


def handle_sms(event: Dict, context: Any) -> str:
    bucket_name = os.environ["SAVES_S3_BUCKET"]

    sms_number = event["body"]["From"]
    command = event["body"]["Body"].lower()

    game = GameGateway()
    s3_bucket_saves = S3BucketSavesGateway(bucket_name)
    context = Context(game=game, saves=s3_bucket_saves)

    try:
        out = do_sms_command(context, command, sms_number)
    except CommandPolicyViolationError as e:
        out = f"SMS ERROR: {str(e)}"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>'
        f"<Response><Message>{out}</Message></Response>"
    )

