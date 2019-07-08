import os
from typing import Any, Dict, Optional, cast

from adventure_anywhere.definitions import Config, Context
from adventure_anywhere.exceptions import CommandPolicyViolationError
from adventure_anywhere.s3_bucket_saves import S3BucketSavesGateway
from adventure_anywhere.use_adventure import do_command, last_output
from adventure_anywhere.game import GameEngine


session_close_prompt = (
    "SAVING PROGRESS IN ADVENTURE. RESUME GAME BY SAYING 'ALEXA, OPEN ADVENTURE.'"
)


def handle(event: Dict, context: Any) -> Dict:
    request_type = event["request"]["type"]
    intent_name = event["request"].get("intent", {}).get("name", "")
    if request_type == "LaunchRequest":
        return _handle_launch_request(event, context)
    elif request_type == "HelpIntent":
        return _handle_help_request(event, context)
    elif request_type == "IntentRequest" and intent_name == "CommandIntent":
        return _handle_command_intent_request(event, context)
    elif request_type == "IntentRequest" and intent_name == "AMAZON.HelpIntent":
        return _handle_help_request(event, context)
    elif request_type == "IntentRequest" and intent_name in (
        "AMAZON.CancelIntent",
        "AMAZON.StopIntent",
    ):
        return _handle_stop_request(event, context)
    elif request_type == "SessionEndedRequest":
        return _handle_session_ended_request(event, context)
    else:
        raise RuntimeError(f"Cannot handle {request_type}")


def _handle_help_request(event: Dict, context: Any) -> Dict:
    return _build_response(GameEngine.help_prompt(), should_session_end=False)


def _handle_stop_request(event: Dict, context: Any) -> Dict:
    return _build_response(session_close_prompt, should_session_end=True)


def _handle_session_ended_request(event: Dict, context: Any) -> Dict:
    reason = event["request"]["reason"]
    out = (
        f"AN ERROR OCCURED. {session_close_prompt}"
        if reason == "ERROR"
        else session_close_prompt
    )
    return _build_response(out, should_session_end=True)


def _handle_launch_request(event: Dict, context: Any) -> Dict:
    bucket_name = os.environ["SAVES_S3_BUCKET"]

    user_id = event["session"]["user"]["userId"]

    s3_bucket_saves = S3BucketSavesGateway(bucket_name)
    context = Context(saves=s3_bucket_saves)

    out = last_output(context, player_id=user_id)

    return _build_response(out, should_session_end=False)


def _handle_command_intent_request(event: Dict, context: Any) -> Dict:
    bucket_name = os.environ["SAVES_S3_BUCKET"]

    user_id = event["session"]["user"]["userId"]

    command = _pluck_command(event)

    s3_bucket_saves = S3BucketSavesGateway(bucket_name)
    context = Context(saves=s3_bucket_saves)

    try:
        out = do_command(context, command, player_id=user_id)
    except CommandPolicyViolationError as e:
        out = str(e)

    return _build_response(out, should_session_end=False)


def _build_response(response_text: str, *, should_session_end: bool) -> Dict:
    return {
        "version": "1.0",
        "response": {
            "outputSpeech": {"text": response_text, "type": "PlainText"},
            "shouldEndSession": should_session_end,
        },
    }


def _pluck_command(event: Dict) -> str:
    slots = event["request"]["intent"]["slots"]

    command_a: str = slots["commandA"]["value"]
    command_b: Optional[str] = slots.get("commandB", {}).get("value", None)

    return f"{command_a} {command_b}" if command_b else command_a
