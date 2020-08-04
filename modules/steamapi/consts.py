#--depends-on commands
#--depends-on config
#--depends-on permissions
#--require-config steam-api-key

import time, math, pprint
from steam import webapi, steamid
from steam.steamid import steam64_from_url, SteamID
from steam.webapi import WebAPI
from src import EventManager, ModuleManager, utils, IRCChannel
from src.core_modules import commands
from src.core_modules.commands import outs
from . import api as SteamAPI
from . import user as SteamUser
from . import utils as SteamUtils

NO_STEAMID = 69
SUCCESS = 1
ERROR_CODES = {
    1: "Success.",
    2: "Generic failure.",
    3: "Your Steam client doesn't have a connection to the back-end.",
    5: "Password/ticket is invalid.",
    6: "The user is logged in elsewhere.",
    7: "Protocol version is incorrect.",
    8: "A parameter is incorrect.",
    9: "File was not found.",
    10: "Called method is busy - action not taken.",
    11: "Called object was in an invalid state.",
    12: "The name was invalid.",
    13: "The email was invalid.",
    14: "The name is not unique.",
    15: "Access is denied.",
    16: "Operation timed out.",
    17: "The user is VAC2 banned.",
    18: "Account not found.",
    19: "The Steam ID was invalid.",
    20: "The requested service is currently unavailable.",
    21: "The user is not logged on.",
    22: "Request is pending, it may be in process or waiting on third party.",
    23: "Encryption or Decryption failed.",
    24: "Insufficient privilege.",
    25: "Too much of a good thing.",
    26: "Access has been revoked (used for revoked guest passes.)",
    27: "License/Guest pass the user is trying to access is expired.",
    28: "Guest pass has already been redeemed by account, cannot be used again.",
    29: "The request is a duplicate and the action has already occurred in the past, ignored this time.",
    30: "All the games in this guest pass redemption request are already owned by the user.",
    31: "IP address not found.",
    32: "Failed to write change to the data store.",
    33: "Failed to acquire access lock for this operation.",
    34: "The logon session has been replaced.",
    35: "Failed to connect.",
    36: "The authentication handshake has failed.",
    37: "There has been a generic IO failure.",
    38: "The remote server has disconnected.",
    39: "Failed to find the shopping cart requested.",
    40: "A user blocked the action.",
    41: "The target is ignoring sender.",
    42: "Nothing matching the request found.",
    43: "The account is disabled.",
    44: "This service is not accepting content changes right now.",
    45: "Account doesn't have value, so this feature isn't available.",
    46: "Allowed to take this action, but only because requester is admin.",
    47: "A Version mismatch in content transmitted within the Steam protocol.",
    48: "The current CM can't service the user making a request, user should try another.",
    49: "You are already logged in elsewhere, this cached credential login has failed.",
    50: "The user is logged in elsewhere. (Use k_EResultLoggedInElsewhere instead!)",
    51: "Long running operation has suspended/paused. (eg. content download.)",
    52: "Operation has been canceled, typically by user. (eg. a content download.)",
    53: "Operation canceled because data is ill formed or unrecoverable.",
    54: "Operation canceled - not enough disk space.",
    55: "The remote or IPC call has failed.",
    56: "Password could not be verified as it's unset server side.",
    57: "External account (PSN, Facebook...) is not linked to a Steam account.",
    58: "PSN ticket was invalid.",
    59:
        "External account (PSN, Facebook...) is already linked to some other account, must explicitly request to replace/delete the link first.",
    60: "The sync cannot resume due to a conflict between the local and remote files.",
    61: "The requested new password is not allowed.",
    62: "New value is the same as the old one. This is used for secret question and answer.",
    63: "Account login denied due to 2nd factor authentication failure.",
    64: "The requested new password is not legal.",
    65: "Account login denied due to auth code invalid.",
    66: "Account login denied due to 2nd factor auth failure - and no mail has been sent.",
    67: "The users hardware does not support Intel's Identity Protection Technology (IPT).",
    68: "Intel's Identity Protection Technology (IPT) has failed to initialize.",
    69: "Operation failed due to parental control restrictions for current user.",
    70: "Facebook query returned an error.",
    71: "Account login denied due to an expired auth code.",
    72: "The login failed due to an IP restriction.",
    73:
        "The current users account is currently locked for use. This is likely due to a hijacking and pending ownership verification.",
    74: "The logon failed because the accounts email is not verified.",
    75: "There is no URL matching the provided values.",
    76: "Bad Response due to a Parse failure, missing field, etc.",
    77: "The user cannot complete the action until they re-enter their password.",
    78: "The value entered is outside the acceptable range.",
    79: "Something happened that we didn't expect to ever happen.",
    80: "The requested service has been configured to be unavailable.",
    81: "The files submitted to the CEG server are not valid.",
    82: "The device being used is not allowed to perform this action.",
    83: "The action could not be complete because it is region restricted.",
    84: "Temporary rate limit exceeded, try again later, different from k_EResultLimitExceeded which may be permanent.",
    85: "Need two-factor code to login.",
    86: "The thing we're trying to access has been deleted.",
    87: "Login attempt failed, try to throttle response to possible attacker.",
    88: "Two factor authentication (Steam Guard) code is incorrect.",
    89: "The activation code for two-factor authentication (Steam Guard) didn't match.",
    90: "The current account has been associated with multiple partners.",
    91: "The data has not been modified.",
    92: "The account does not have a mobile device associated with it.",
    93: "The time presented is out of range or tolerance.",
    94: "SMS code failure - no match, none pending, etc.",
    95: "Too many accounts access this resource.",
    96: "Too many changes to this account.",
    97: "Too many changes to this phone.",
    98: "Cannot refund to payment method, must use wallet.",
    99: "Cannot send an email.",
    100: "Can't perform operation until payment has settled.",
    101: "The user needs to provide a valid captcha.",
    102: "A game server login token owned by this token's owner has been banned.",
    103:
        "Game server owner is denied for some other reason such as account locked, community ban, vac ban, missing phone, etc.",
    104: "The type of thing we were requested to act on is invalid.",
    105: "The IP address has been banned from taking this action.",
    106: "This Game Server Login Token (GSLT) has expired from disuse; it can be reset for use.",
    107: "user doesn't have enough wallet funds to complete the action",
    108: "There are too many of this thing pending already"
}

USER_STATES = {
    0: "Offline",
    1: "Online",
    2: "Busy",
    3: "Away",
    4: "Snooze",
    5: "Looking to trade",
    6: "Looking to play"
}


def error_code(code):
    return ERROR_CODES[code]


def user_state(code):
    return USER_STATES[code]