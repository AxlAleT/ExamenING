class DatabaseRouter:
    """
    A router to control all database operations on models
    """
    
    # Models that should use the olapdb (data warehouse)
    olap_models = {
        'DimCustomer', 'DimRestaurant', 'DimDate', 'DimLocation', 
        'DimTimeslot', 'DimDeliveryPerson', 'FactOrders'
    }
    
    # ETL models that should also use olapdb
    etl_models = {
        'ETLJob', 'DataUpload'
    }
    
    def db_for_read(self, model, **hints):
        """Suggest the database to read from."""
        if model._meta.object_name in self.olap_models or model._meta.object_name in self.etl_models:
            return 'olapdb'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Suggest the database to write to."""
        if model._meta.object_name in self.olap_models or model._meta.object_name in self.etl_models:
            return 'olapdb'
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations if models are in the same database."""
        db_set = {'default', 'olapdb'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that certain models' migrations go to the right database."""
        if db == 'olapdb':
            # Allow data warehouse models and ETL models in olapdb
            return model_name and model_name.lower() in [
                'dimcustomer', 'dimrestaurant', 'dimdate', 'dimlocation',
                'dimtimeslot', 'dimdeliveryperson', 'factorders',
                'etljob', 'dataupload'
            ]
        elif db == 'default':
            # Only allow OLTP models in default database (exclude warehouse and ETL models)
            return model_name and model_name.lower() not in [
                'dimcustomer', 'dimrestaurant', 'dimdate', 'dimlocation',
                'dimtimeslot', 'dimdeliveryperson', 'factorders',
                'etljob', 'dataupload'
            ]
        return False
