try:
    from termcolor import cprint
except ImportError:
    def cprint(text, *args, **kwargs):
        print text


def tprint(text):
    cprint(text, 'green', attrs=['bold'])


def fprint(text):
    cprint(text, 'red', attrs=['bold'])


def iprint(text):
    cprint(text, 'blue', attrs=['bold'])


def wprint(text):
    cprint(text, 'yellow', attrs=['bold'])
