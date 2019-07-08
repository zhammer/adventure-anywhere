import os
from typing import Any, Dict, Optional, cast

from adventure_anywhere.definitions import Config, Context
from adventure_anywhere.exceptions import CommandPolicyViolationError
from adventure_anywhere.s3_bucket_saves import S3BucketSavesGateway
from adventure_anywhere.use_adventure import do_command, last_output


def handle(event: Dict, context: Any) -> Dict:
    request_type = event["request"]["type"]
    if request_type == "LaunchRequest":
        return _handle_launch_request(event, context)
    elif request_type == "IntentRequest":
        return _handle_intent_request(event, context)
    else:
        raise RuntimeError(f"Cannot handle {request_type}")


def _handle_launch_request(event: Dict, context: Any) -> Dict:
    bucket_name = os.environ["SAVES_S3_BUCKET"]

    user_id = event["session"]["user"]["userId"]

    s3_bucket_saves = S3BucketSavesGateway(bucket_name)
    context = Context(saves=s3_bucket_saves)

    out = last_output(context, player_id=user_id)

    return _build_response(out)


def _handle_intent_request(event: Dict, context: Any) -> Dict:
    bucket_name = os.environ["SAVES_S3_BUCKET"]

    user_id = event["session"]["user"]["userId"]

    command = _pluck_command(event)

    s3_bucket_saves = S3BucketSavesGateway(bucket_name)
    context = Context(saves=s3_bucket_saves)

    try:
        out = do_command(context, command, player_id=user_id)
    except CommandPolicyViolationError as e:
        out = str(e)

    return _build_response(out)


def _build_response(response_text: str) -> Dict:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"text": response_text, "type": "PlainText"},
            "shouldEndSession": False,
        },
    }


def _pluck_command(event: Dict) -> str:
    slots = event["request"]["intent"]["slots"]

    command_a: str = slots["commandA"]["value"]
    command_b: Optional[str] = slots.get("commandB", {}).get("value", None)

    return f"{command_a} {command_b}" if command_b else command_a
