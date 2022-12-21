from pydoc import locate


class ClassLoader:
    def locate(self, class_name: str):
        return locate(class_name)
