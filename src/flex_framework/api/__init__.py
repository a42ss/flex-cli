from inspect import isclass


def get_class_path(class_reference):
    if isclass(class_reference):
        return class_reference.__module__ + "." + class_reference.__qualname__
    raise Exception("Invalid python class provided for: " + str(class_reference))
