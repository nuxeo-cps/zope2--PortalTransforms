from  Products.PortalTransforms.interfaces import ichain, itransform
from UserList import UserList

class chain(UserList):
    """A chain of transforms used to transform data"""

    __implements__ = (ichain, itransform)

    def __init__(self, name='',*args):
        UserList.__init__(self, *args)
        self.__name__ = name
        if args:
            self._update()

    def name(self):
        return self.__name__

    def registerTransform(self, transform):
        self.append(transform)

    def unregisterTransform(self, name):
        for i in range(len(self)):
            tr = self[i]
            if tr.name() == name:
                self.pop(i)
                break
        else:
            raise Exception('No transform named %s registered' % name)

    def convert(self, orig, data, **kwargs):
        for transform in self:
            data = transform.convert(orig, data, **kwargs)
            orig = data.getData()
        md = data.getMetadata()
        md['mimetype'] = self.output
        return data

    def __setitem__(self, key, value):
        UserList.__setitem__(self, key, value)
        self._update()

    def append(self, value):
        UserList.append(self, value)
        self._update()

    def insert(self, *args):
        UserList.insert(*args)
        self._update()

    def remove(self, *args):
        UserList.remove(*args)
        self._update()

    def pop(self, *args):
        UserList.pop(*args)
        self._update()

    def _update(self):
        self.inputs = self[0].inputs
        self.output = self[-1].output
        for i in range(len(self)):
            if hasattr(self[-i-1], 'output_encoding'):
                self.output_encoding = self[-i-1].output_encoding
                break
        else:
            try:
                del self.output_encoding
            except:
                pass
