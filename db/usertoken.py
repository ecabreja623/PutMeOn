"""
This file contains the methods for managing user tokens
"""

import secrets
import datetime


ID = "id"
EXP = "exp"


def blank():
    """
    generates a blank token for creating a user
    """
    return {
        ID: "",
        EXP: "",
    }


def new():
    """
    generates a new token when for when a user is logged in
    """
    return {
        ID: secrets.token_urlsafe(16),
        EXP: (datetime.datetime.utcnow() +
              datetime.timedelta(days=1)).isoformat()
    }


def check(val):
    """
    returns false if token is invalid
    """
    return (datetime.datetime.fromisoformat(val[EXP]) >
            datetime.datetime.utcnow())
