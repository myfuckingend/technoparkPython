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
            self.new_action = []
            act = None
            for action in self._actions:
                if not action.from_version < from_version and not action.to_version > to_version:
                    act = self.optimize(act, action)
                elif action.to_version > to_version:
                    break
            if act != None:
                self.new_action.append(act)
            return self.new_action

    def optimize(self, act, action):
        if isinstance(action, DeleteAction) and isinstance(act, DeleteAction):
            if action.pos in range(act.pos, act.length + 1):
                act.length = act.length + action.length
                act.pos = min(act.pos, action.pos)
            else:
                self.action_to_return.append(act)
                act = action
                return act
        elif isinstance(action, InsertAction) and isinstance(act, InsertAction):
            if action.pos in range(act.pos, act.pos + len(act.text) + 1):
                act.text = act.text[:action.pos] + action.text + act.text[action.pos:]
            else:
                self.new_action.append(act)
                act = action
                return act
        elif isinstance(action, ReplaceAction):
            if act != None:
                self.new_action.append(act)
            self.new_action.append(action)
            act = None
            return act
        else:
            if act != None:
                self.new_action.append(act)
            act = action

        return act

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

    def __repr__(self):
        return "InsertAction(pos = {!r}, text = {!r}, " \
               "v1 = {!r}, v2 = {!r})".format(self.pos, self.text,
                self.from_version, self.to_version)

class ReplaceAction(Action):

    def apply(self, line):
        line = line[:self.pos] + self.text + line[self.pos + len(self.text):]
        return line

    def __repr__(self):
        return "ReplaceAction(pos = {!r}, text = {!r}, " \
               "v1 = {!r}, v2 = {!r})".format(self.pos, self.text,
                self.from_version, self.to_version)

class DeleteAction(Action):

    def __init__(self, pos, length, from_version, to_version):
        self.length = length
        self.pos = pos
        self.from_version = from_version
        self.to_version = to_version

    def apply(self, line):
        line = line[:self.pos] + line[self.pos + self.length:]
        return line

    def __repr__(self):
        return "DeleteAction(pos = {!r}, length = {!r}, " \
               "v1 = {!r}, v2 = {!r})".format(self.pos, self.length,
                                              self.from_version,
                                              self.to_version)
