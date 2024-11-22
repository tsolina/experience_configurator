import experience as exp

class ActorCatia:
    def __init__(self, cat_object: exp.AnyObject = None, link_on_feature: exp.AnyObject = None, path:str="", type_="", err_message=""):
        self.link_on_feature = link_on_feature
        self.path = path
        self.cat_object = cat_object
        self.type_ = type_
        self.err_message = err_message

    def __del__(self):
        """Cleanup resources when the object is deleted."""
        self.link_on_feature = None
        self.cat_object = None
