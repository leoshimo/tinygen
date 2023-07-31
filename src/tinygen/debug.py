
def print_message(msg: dict):
    print('*** {role}:\n{content}\n'.format(role = msg['role'].upper(), content = msg['content']))
