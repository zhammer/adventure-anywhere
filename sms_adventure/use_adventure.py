from sms_adventure.definitions import Context
from sms_adventure.exceptions import CommandPolicyViolationError
from sms_adventure import policies
from sms_adventure import special_sms_functionality


def do_sms_command(context: Context, command_text: str, from_sms_number: str) -> str:
    command_text = special_sms_functionality.strip_sms_bypass_prefix(command_text)

    command_invalid_reason = policies.command.invalid_reason(command_text)
    if command_invalid_reason:
        raise CommandPolicyViolationError(command_invalid_reason)

    last_save = context.saves.fetch_save(from_sms_number)

    if special_sms_functionality.is_restart_command(command_text):
        start_text = context.game.start()
        response_text = special_sms_functionality.add_after_start_message(start_text)

    elif last_save:
        context.game.resume(last_save)
        response_text = context.game.do_command(command_text)

    else:
        start_text = context.game.start()
        response_text = special_sms_functionality.add_after_start_message(start_text)

    new_save = context.game.save()
    context.saves.update_save(from_sms_number, new_save)

    return response_text
