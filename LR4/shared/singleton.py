class SingletonMeta(type):
    _instances = {}
    
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            try:
                instance = super().__call__(*args, **kwargs)
                cls._instances[cls] = instance
            except TypeError:
                print(f"Attempting to get {cls.__name__} before initialization")
        return cls._instances[cls]
                
        return class_._instance