from json import loads


def jsonDecode(data):
    try:
        return loads(data)
    except:
        return dict()
