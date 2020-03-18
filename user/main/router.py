class MainRouter(object):

    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'box_users':
            return 'replica'
        return None

    def db_for_write(self,model, **hints):
        if model._meta.app_label == 'box_users':
            return 'default'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """ Allow relations if a model in the auth app is involved. """
        if obj1._meta.app_label == 'box_users' or  obj2._meta.app_label == 'box_users':
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label == 'box_users':
            return db == 'default'
        return None
