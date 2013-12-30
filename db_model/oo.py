class RolType(object):
    roles = {'A' : 'Admin User',
             'V' : 'Advanced User',
             'K' : 'Kid User',
             'G' : 'Guest User'}
    
    def getValue(self, key):
        return self.roles.get(key)
    
    def getKeys(self):
        return self.roles.keys()
    
    def getValues(self):
        return self.roles.values()
    
    def dbTypes(self):
        return self.getValues()
    
    def user_admin(self):
        return self.getValue('A')

    def user_adv(self):
        return self.getValue('V')

    def user_kid(self):
        return self.getValue('K')

    def user_guest(self):
        return self.getValue('G')
