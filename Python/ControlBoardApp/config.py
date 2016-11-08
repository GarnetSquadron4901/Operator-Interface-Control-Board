

class ConfigFile:
    def __init__(self, filename):
        pass

    def get_nt_server_address(self):
        nt_address = 'localhost'

        print ('Loaded NT server address from config: %s' % nt_address)
        return nt_address

    def set_nt_server_address(self, nt_address):

        print ('Saving NT server address to config: %s' % nt_address)


    def get_cb_type(self):

        cb_type = 'Simulator'

        print ('Loaded control board type from config: %s' % cb_type)

    def set_cb_type(self, cb_type):

        print('Saving control board type to config: %s' % cb_type)


