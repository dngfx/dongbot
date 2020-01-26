from src import EventManager, ModuleManager, utils

# describing command arg specifications, to centralise parsing and validating.
#
# format: <!|?><name>
#   ! = required
#   ? = optional
#
# if "name" contains "~", it will be marked as an "important" spec
# this means that, e.g. "!r~channel" will be:
#   - marked as important
#   - name split to everything after ~
#   - the name, and it's value, will be offered to other preprocessors.
#
# this means, in practice, that "!r~channel" is a:
#   - "revelant" channel (current if in channel, explicit arg otherwise)
#   - will be used to check if a user has permissions
#
# spec types:
#   - "time" - +1w2d3h4m5s format time
#   - "rchannel" - relevant channel. current channel if we're in channel,
#     otherwise an explicit channel name argument
#   - "channel" - an argument of a channel name
#   - "cuser" - a nickname but only if they are in the current channel
#   - "ruser" - revlevant user. either current user if no arguments, otherwise
#     take nickname for user from given args
#   - "user" - an argument of a user's nickname
#   - "ouser" - an argument of a potentially offline user's nickname
#   - "word" - one word from arguments
#   - "string" - collect all remaining args in to a string

class Module(ModuleManager.BaseModule):
    def _spec_value(self, server, channel, user, argument_types, args):
        options = []
        first_error = None
        for argument_type in argument_types:
            value = None
            n = 0
            error = None

            simple_value, simple_count = argument_type.simple(args)
            if not simple_count == -1:
                value = simple_value
                n = simple_count
                error = argument_type.error()
            elif argument_type.type == "rchannel":
                if channel:
                    value = channel
                elif args:
                    n = 1
                    if args[0] in server.channels:
                        value = server.channels.get(args[0])
                    error = "No such channel"
                else:
                    error = "No channel provided"
            elif argument_type.type == "channel" and args:
                if args[0] in server.channels:
                    value = server.channels.get(args[0])
                n = 1
                error = "No such channel"
            elif argument_type.type == "cuser" and args:
                tuser = server.get_user(args[0], create=False)
                if tuser and channel.has_user(tuser):
                    value = tuser
                n = 1
                error = "That user is not in this channel"
            elif argument_type.type == "ruser":
                if args:
                    value = server.get_user(args[0], create=False)
                    n = 1
                else:
                    value = user
                error = "No such user"
            elif argument_type.type == "user":
                if args:
                    value = server.get_user(args[0], create=False)
                    n = 1
                    error = "No such user"
                else:
                    error = "No user provided"
            elif argument_type.type == "ouser" and args:
                if server.has_user_id(args[0]):
                    value = server.get_user(args[0])
                n = 1
                error = "Unknown nickname"

            options.append([argument_type, value, n, error])
        return options

    @utils.hook("preprocess.command")
    @utils.kwarg("priority", EventManager.PRIORITY_HIGH)
    def preprocess(self, event):
        spec_arguments = event["hook"].get_kwarg("spec", None)
        if not spec_arguments == None:
            server = event["server"]
            channel = event["target"] if event["is_channel"] else None
            user = event["user"]
            args = event["args_split"].copy()

            out = []
            kwargs = {"channel": channel}

            for spec_argument in spec_arguments:
                options = self._spec_value(server, kwargs["channel"], user,
                    spec_argument.types, args)

                found = None
                first_error = None
                for argument_type, value, n, error in options:
                    if not value == None:
                        if argument_type.exported:
                            kwargs[argument_type.exported] = value

                        found = True
                        args = args[n:]
                        if len(spec_argument.types) > 1:
                            value = [argument_type.type, value]
                        found = value
                        break
                    elif not error and n > 0:
                        error = "Not enough arguments"

                    if error and not first_error:
                        first_error = error

                if not spec_argument.optional and not found:
                    error = first_error or "Invalid arguments"
                    return utils.consts.PERMISSION_HARD_FAIL, error

                out.append(found)

            kwargs["spec"] = out
            event["kwargs"].update(kwargs)