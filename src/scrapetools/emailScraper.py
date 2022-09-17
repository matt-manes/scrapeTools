from string import printable
from progbar import progBar
from urllib.parse import unquote

def validate(email:str)->bool:
    """ Checks string to see if it's likely an email address.
    Returns True or False."""
    atdex = email.find('@')
    lastDot = email.rfind('.')
    if all([-1 not in [atdex, lastDot],
            atdex < lastDot,
            email[0] not in ['@','.'],
            email[-1] not in ['@','.'],
            email.count('@') == 1,
            len(email.split('@')[0]) >= 2,
            len(email.split('@')[1]) > 3,
            not all(ch.isnumeric() for ch in email[atdex+1:].replace('.','')),
            all(ext not in email[email.find('@'):] for ext in ['.png','.jpg','.js','.html','.svg',
                                                                '.jpeg','.mp4','.mpeg','.css','.pdf',
                                                                '.wav','.docx','.txt','.rtf','.gif'])]):
        return True    
    else:
        return False

def findLastValidCharacterOffset(text:str)->int:
    """ Iterates through a string to find the index of the last valid character,
    assuming that string either starts or ends with '@'.\n
    If the string doesn't start or end with '@', an Exception is raised.\n
    Returns the number of valid characters between '@' and first invalid character.
    e.g. '@abcde%' will return 5 and '#123@' will return 3.\n
    If no invalid characters are found, the function will return
    'len(text)-1'."""
    
    """ Technically some of these characters are valid in an email string,
    but the ratio of how often they're used to how often they produce
    false positives makes them worth disregarding. """
    invalidCharacters = ' <>[]{},"\':;\\/#$%^&*()=+`?|\n\t\r'
    if text[-1] == '@' and text[0] != '@':
        #reverse the string
        text = text[::-1]
    elif text[0] != '@':
        raise Exception('First or last character of text arg needs to be "@"')
    i = 1
    while i < len(text):
        if text[i] in invalidCharacters or text[i] not in printable:
            return i - 1
        else:
            i += 1
    return len(text)-1

def scrapeEmails(text:str, displayProgressBar:bool=True)->list[str]:
    """ Extracts potential emails from given text\n
    and returns as a list of strings."""
    if '%' in text:
        #decode percent encoding
        text = unquote(text)
    atCount = text.count('@')
    emails = []
    if atCount > 0:
        lastStopdex = 0
        for i in range(atCount):
            if displayProgressBar:
                progBar(i, atCount-1, prefix='Scraping emails...')
            atdex = text.find('@',lastStopdex)
            nextAtdex = text.find('@',atdex+1)
            try:
                chunk = text[lastStopdex:nextAtdex] if nextAtdex != -1 else text[lastStopdex:]
                chunkAtdex = chunk.find('@')
                startdex = findLastValidCharacterOffset(chunk[:chunkAtdex+1])
                stopdex = findLastValidCharacterOffset(chunk[chunkAtdex:])
                email = chunk[chunkAtdex-startdex:stopdex+chunkAtdex+1]
                while email[-1].isnumeric() or not email[-1].isalpha():
                    email = email[:-1]
                if validate(email):
                    emails.append(email.lower())
                """ The extra '+ 1' is to ensure lastStopdex increments
                if 'len(email.split('@')[1])' is 0."""
                lastStopdex = atdex + len(email.split('@')[1]) + 1
            except Exception as e:
                lastStopdex = atdex+1
        emails = sorted(list(set(emails)))
    return emails

