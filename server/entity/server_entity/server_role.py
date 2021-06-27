import errors


class ServerRole:
    REQUIRED_ATTRIBUTES = {
        'ACTION_MAP',
        'game',
        'close_connection',
        'instance',
        'LOGIN_ACTION',
        'save_to_db'
    }

    def __init__(self, *args, **kwargs):
        self.class_name = self.__class__.__name__.upper()
        self.__check_attributes()

    @staticmethod
    def check_keys(data: dict, keys, aggregate_func=all):
        if not aggregate_func([k in data for k in keys]):
            raise errors.BadCommand(
                'The command\'s payload does not contain all needed keys, '
                'following keys are expected: {}'.format(keys)
            )
        else:
            return True

    def action(self, action, data):
        """ Interprets observer's actions.
                """
        if action not in self.ACTION_MAP:
            raise errors.BadCommand('No such action: {}'.format(action))

        method = self.ACTION_MAP[action]
        return method(self, data)

    def __check_attributes(self, aggregate_func=all):
        if not aggregate_func(
                map(lambda attr: hasattr(self, attr),
                    self.REQUIRED_ATTRIBUTES)
        ):
            raise errors.ResourceNotFound(
                'You need to implement the following attributes: {}'.format(self.REQUIRED_ATTRIBUTES))
