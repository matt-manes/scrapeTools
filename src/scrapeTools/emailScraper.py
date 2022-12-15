from string import printable
from urllib.parse import unquote


def validate(email: str) -> bool:
    """Checks string to see if it's likely an email address.

    Returns True or False.

    Some emails violating some of these rules
    may technically be valid, but are practically
    never seen in use out in the wild."""
    if email.count("@") != 1 or email.count(".") == 0:
        return False
    atdex = email.find("@")
    lastDot = email.rfind(".")
    local, domain = email.split("@")
    # RULES:
    #'@' comes before the last '.'
    # local part is 64 characters or less
    # domain part doesn't contain any '_'
    # at least 1 character in local is alphabetical
    # 1st character is not '@' or '.'
    # last character is not '@' or '.'
    # character after '@' is not '.'
    # doesn't start with 'www.'
    # local is two or more characters
    # domain is more than 3 characters
    # domain doesn't consist of only numbers
    # local doesn't consist of only numbers
    # no consecutive '.' in email
    # email doesn't contain a listed file ext
    if all(
        [
            atdex < lastDot,
            len(local) <= 64,
            domain.count("_") == 0,
            any(ch.isalpha() for ch in local),
            email[0] not in ["@", "."],
            email[-1] not in ["@", "."],
            email[email.find("@") + 1] != ".",
            not email.startswith("www."),
            len(local) >= 2,
            len(domain) > 3,
            not all(ch.isnumeric() for ch in domain.replace(".", "")),
            not all(ch.isnumeric() for ch in local.replace(".", "")),
            all(email[i - 1] != "." for i, ch in enumerate(email) if ch == "."),
            all(
                ext not in domain
                for ext in [
                    ".png",
                    ".jpg",
                    ".js",
                    ".html",
                    ".svg",
                    ".jpeg",
                    ".mp4",
                    ".mpeg",
                    ".css",
                    ".pdf",
                    ".wav",
                    ".docx",
                    ".txt",
                    ".rtf",
                    ".gif",
                    ".webp",
                    ".x.x",
                ]
            ),
        ]
    ):
        return True
    else:
        return False


def findLastValidCharacterOffset(text: str) -> int:
    """Iterates through a string to find the index of the last valid character,
    assuming that string either starts or ends with '@'.

    If the string doesn't start or end with '@', an Exception is raised.

    Returns the number of valid characters between '@' and first invalid character.
    e.g. '@abcde%' will return 5 and '#123@' will return 3.

    If no invalid characters are found, the function will return
    'len(text)-1'."""

    """ Technically some of these characters are valid in an email string,
    but the ratio of how often they're used to how often they produce
    false positives makes them worth disregarding. """
    invalidCharacters = " <>[]{},\"':;\\/#$%^&*()=+`?|\n\t\r"
    if text[-1] == "@" and text[0] != "@":
        # reverse the string
        text = text[::-1]
    elif text[0] != "@":
        raise ValueError(
            'First or last character of text arg needs to be "@"\n',
            f"Argument {text} is invalid.",
        )
    i = 1
    while i < len(text):
        if text[i] in invalidCharacters or text[i] not in printable:
            return i - 1
        else:
            i += 1
    return len(text) - 1


def stripUnicode(emails: list[str]) -> list[str]:
    """Removes unicode text that often gets picked
    up at the front of email addresses and returns the list."""
    strippedEmails = []
    for email in emails:
        for text in ["u003e", "u00a0"]:
            if text in email:
                email = email[len(text) + 1 :]
        strippedEmails.append(email)
    return strippedEmails


def scrapeEmails(text: str) -> list[str]:
    """Extracts potential emails from given text
    and returns as a list of strings."""
    if "%" in text:
        # decode percent encoding
        text = unquote(text)
    for ch in ["\n", "\t", "\r"]:
        text = text.replace(ch, " ")
    atCount = text.count("@")
    emails = []
    if atCount > 0:
        lastStopdex = 0
        for i in range(atCount):
            atdex = text.find("@", lastStopdex)
            nextAtdex = text.find("@", atdex + 1)
            try:
                chunk = (
                    text[lastStopdex:nextAtdex]
                    if nextAtdex != -1
                    else text[lastStopdex:]
                )
                chunkAtdex = chunk.find("@")
                startdex = findLastValidCharacterOffset(chunk[: chunkAtdex + 1])
                stopdex = findLastValidCharacterOffset(chunk[chunkAtdex:])
                email = chunk[chunkAtdex - startdex : stopdex + chunkAtdex + 1]
                while email[-1].isnumeric() or not email[-1].isalpha():
                    email = email[:-1]
                if validate(email):
                    emails.append(email.lower())
                """ The extra '+ 1' is to ensure lastStopdex increments
                if 'len(email.split('@')[1])' is 0."""
                lastStopdex = atdex + len(email.split("@")[1]) + 1
            except Exception as e:
                lastStopdex = atdex + 1
        emails = sorted(list(set(stripUnicode(emails))))
    return emails
