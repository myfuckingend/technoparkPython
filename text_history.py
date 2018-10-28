class TextHistory:

    def __init__(self):
        self._text = ''
        self._actions = []
        self._version = 0
        self._pos = len(self._text)

    def checkValueError(self, text, pos, length = None):
        if pos == None:
            pos = len(self._text)
        if type(pos) == int and not pos < 0 and pos <= len(self._text):
            self._pos = pos
            if length and len(self._text[pos:]) < length:
                raise ValueError
            return pos
        raise ValueError

    @property
    def text(self):
        return self._text

    @property
    def version(self):
        return self._version

    def insert(self, text, pos = None):
        pos = self.checkValueError(text, pos)
        action = InsertAction(pos, text, from_version = self._version,
                              to_version = self._version + 1)

        return self.action(action)

    def replace(self, text, pos = None):
        pos = self.checkValueError(text, pos)
        action = ReplaceAction(pos, text, from_version = self._version,
                               to_version = self._version + 1)

        return self.action(action)

    def delete(self, pos, length):
        pos = self.checkValueError(self._text, pos, length)
        action = DeleteAction(pos, length, from_version = self._version,
                              to_version = self._version + 1)

        return self.action(action)

    def action(self, action):
        self._actions.append(action)
        action.checkVersion()
        self._text = action.apply(self._text)
        self._version = action.to_version
        return self._version

    def get_actions(self, from_version = 0, to_version = None):
        if to_version == None:
            to_version = self._version
        if from_version < 0 or from_version > to_version or to_version > self._version:
            raise ValueError
        else:
            new_action = []
            for action in self._actions:
                if not action.from_version < from_version and \
                        not action.from_version >= to_version and to_version != 0:
                    new_action.append(action)
            return new_action


class Action:

    def __init__(self, pos, text, from_version, to_version):
        self.text = text
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def checkVersion(self):
        if self.from_version >= self.to_version:
            raise ValueError

class InsertAction(Action):

    def apply(self, line):
        line = line[:self.pos] + self.text + line[self.pos:]
        return line

class ReplaceAction(Action):

    def apply(self, line):
        line = line[:self.pos] + self.text + line[self.pos + len(self.text):]
        return line

class DeleteAction(Action):

    def __init__(self, pos, length, from_version, to_version):
        self.length = length
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, line):
        line = line[:self.pos] + line[self.pos + self.length:]
        return line
