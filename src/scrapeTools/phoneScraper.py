import phonenumbers


def getNumConsecutiveNumbers(text: str, reverse: bool = False) -> int:
    """Finds the number of consecutive numeric characters in a string."""
    # limit search to 10 characters
    text[:10]
    if reverse:
        text = text[::-1]
    for i, ch in enumerate(text):
        if not ch.isnumeric():
            return i
    return len(text)


def findBySeparator(text: str, separator: str) -> list[str]:
    """Attempts to detect phone numbers according to these
    patterns by scanning for separators (typically '-.')
    and how many consecutive numbers follow or precede them:

    (xxx)xxx{separator}xxxx

    (xxx) xxx{separator}xxxx

    (xxx){separator}xxx{separator}xxxx

    xxx{separator}xxx{separator}xxxx"""
    count = text.count(separator)
    numbers = []
    if count > 0:
        lastStopdex = 0
        for _ in range(count):
            number = ""
            sepdex = text.find(separator, lastStopdex)
            if sepdex != -1:
                nextSepdex = text.find(separator, sepdex + 1)
                # consecutive numbers preceding sepdex
                startOffset = getNumConsecutiveNumbers(
                    text[lastStopdex:sepdex], reverse=True
                )
                # consecutive numbers between sepdex and nextSepdex
                firstStopOffset = getNumConsecutiveNumbers(
                    text[sepdex + 1 : nextSepdex + 1]
                )
                # consecutive numbers after nextSepdex
                secondStopOffset = getNumConsecutiveNumbers(text[nextSepdex + 1 :])

                if startOffset == 3 and firstStopOffset == 3 and secondStopOffset == 4:
                    # xxx{separator}xxx{separator}xxxx
                    number = text[
                        sepdex - startOffset : nextSepdex + secondStopOffset + 1
                    ]
                elif (
                    startOffset == 0
                    and firstStopOffset == 3
                    and secondStopOffset == 4
                    and text[sepdex - 1] == ")"
                    and text[sepdex - 5] == "("
                ):
                    # (xxx){separator}xxx{separator}xxxx
                    number = text[
                        sepdex - 5 : sepdex + firstStopOffset + secondStopOffset + 2
                    ]
                elif startOffset == 3 and text[sepdex - 4] in [")", " "]:
                    # (xxx)xxx{separator}xxxx or (xxx) xxx{separator}xxxx
                    number = text[sepdex - 8 : sepdex + 5]
                lastStopdex = sepdex + 5
                for ch in [separator, "(", ")", " "]:
                    number = number.replace(ch, "")
                if len(number) == 10 and all(ch.isnumeric() for ch in number):
                    numbers.append(number)
    return numbers


def findByHref(text: str) -> list[str]:
    """Scrapes phone numbers by href attribute."""
    indicator = 'href="'
    count = text.count(indicator)
    prefixes = ["tel:", "callto:"]
    index = 0
    numbers = []
    for _ in range(count):
        index = text.find(indicator, index + 1)
        number = text[index + len(indicator) : text.find('"', index + len(indicator))]
        if any(prefix in number for prefix in prefixes):
            number = "".join(
                [num for num in number[number.find(":") + 1 :] if num.isnumeric()]
            )
            if len(number) == 10:
                numbers.append(number)
    return numbers


def scrapePhoneNumbers(text: str) -> list[str]:
    """Scrape for u.s. phone numbers."""
    numbers = []
    text = text.replace("+1", "")
    for separator in "-.":
        numbers.extend(findBySeparator(text, separator))
    numbers.extend(findByHref(text))
    numbers = [
        number
        for number in numbers
        if phonenumbers.is_valid_number(phonenumbers.parse("+1" + number))
    ]
    numbers = sorted(list(set(numbers)))
    return numbers
