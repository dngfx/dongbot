import uuid
from src import IRCBuffer, IRCLine, utils

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def _from_self(server, source):
    if source:
        return server.is_own_nickname(source.nickname)
    else:
        return False

<<<<<<< HEAD

=======
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
def message(events, event):
    from_self = _from_self(event["server"], event["line"].source)
    if from_self == None:
        return

    direction = "send" if from_self else "received"

    target_str = event["line"].args[0]

    message = None
    if len(event["line"].args) > 1:
        message = event["line"].args[1]

    source = event["line"].source
<<<<<<< HEAD
    if (not event["server"].nickname or not source or source.hostmask == event["server"].name):
=======
    if (not event["server"].nickname
            or not source
            or source.hostmask == event["server"].name):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
        if source:
            event["server"].name = event["line"].source.hostmask
        else:
            source = IRCLine.parse_hostmask(event["server"].name)
        target_str = event["server"].nickname or "*"

    if from_self:
        user = event["server"].get_user(event["server"].nickname)
    else:
<<<<<<< HEAD
        user = event["server"].get_user(source.nickname, username=source.username, hostname=source.hostname)
=======
        user = event["server"].get_user(source.nickname,
            username=source.username,
            hostname=source.hostname)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

    # strip prefix_symbols from the start of target, for when people use
    # e.g. 'PRIVMSG +#channel :hi' which would send a message to only
    # voiced-or-above users
    statusmsg = ""
    for char in target_str:
        if char in event["server"].statusmsg:
            statusmsg += char
        else:
            break
    target = target_str.replace(statusmsg, "", 1)

    is_channel = event["server"].is_channel(target)

    if is_channel:
        if not target in event["server"].channels:
            return
        target_obj = event["server"].channels.get(target)
    else:
        target_obj = event["server"].get_user(target)

<<<<<<< HEAD
    kwargs = {
        "server": event["server"],
        "target": target_obj,
        "target_str": target_str,
        "user": user,
        "tags": event["line"].tags,
        "is_channel": is_channel,
        "from_self": from_self,
        "line": event["line"],
        "statusmsg": statusmsg
    }
=======
    kwargs = {"server": event["server"], "target": target_obj,
        "target_str": target_str, "user": user, "tags": event["line"].tags,
        "is_channel": is_channel, "from_self": from_self, "line": event["line"],
        "statusmsg": statusmsg}
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

    action = False

    if message:
        ctcp_message = utils.irc.parse_ctcp(message)

        if ctcp_message:
<<<<<<< HEAD
            if (not ctcp_message.command == "ACTION" or not event["line"].command == "PRIVMSG"):
=======
            if (not ctcp_message.command == "ACTION" or not
                    event["line"].command == "PRIVMSG"):
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
                if event["line"].command == "PRIVMSG":
                    ctcp_action = "request"
                else:
                    ctcp_action = "response"
<<<<<<< HEAD
                events.on(direction).on("ctcp").on(ctcp_action).call(message=ctcp_message.message, **kwargs)
                events.on(direction).on("ctcp").on(ctcp_action).on(ctcp_message.command).call(
                    message=ctcp_message.message,
=======
                events.on(direction).on("ctcp").on(ctcp_action).call(
                    message=ctcp_message.message, **kwargs)
                events.on(direction).on("ctcp").on(ctcp_action).on(
                    ctcp_message.command).call(message=ctcp_message.message,
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5
                    **kwargs)
                return
            else:
                message = ctcp_message.message
                action = True

    if not message == None:
        kwargs["message"] = message
        kwargs["message_split"] = message.split(" ")
        kwargs["action"] = action

    event_type = event["line"].command.lower()
    if event_type == "privmsg":
        event_type = "message"

    context = "channel" if is_channel else "private"
    hook = events.on(direction).on(event_type).on(context)

    buffer_line = None
    if message:
<<<<<<< HEAD
        buffer_line = IRCBuffer.BufferLine(user.nickname,
                                           message,
                                           action,
                                           event["line"].tags,
                                           from_self,
                                           event["line"].command)
=======
        buffer_line = IRCBuffer.BufferLine(user.nickname, message, action,
            event["line"].tags, from_self, event["line"].command)
>>>>>>> 553eb1a1e901b385368c200de5d5904a0c42eeb5

    buffer_obj = target_obj
    if is_channel:
        hook.call(channel=target_obj, buffer_line=buffer_line, **kwargs)
    else:
        buffer_obj = target_obj
        if not from_self:
            buffer_obj = user

        hook.call(buffer_line=buffer_line, **kwargs)

    if buffer_line:
        buffer_obj.buffer.add(buffer_line)
