class CallStaticInit:

    def some_func(self):
        print('from some func:', self.attr)

    my_attr: str = 'my attr'

    def __init__(self, *args, **kwargs):
        print('__init__')
        new_class = type(*args)
        new_class.my_attrr: str = 'my str'

        new_class.my_func1 = self.some_func
        self.meta = new_class
        # return new_class

    def __call__(self, *args, **kwargs):
        print('__call__')
        return self.meta

    # def __new__(cls, *args, **kwargs):
    #     new_class = type(*args)
    #     new_class.my_attrr: str = 'my str'
    #
    #     new_class.my_func = cls.some_func
    #
    #     return new_class


def call_static_init(cls):
    if getattr(cls, '__static_init__', None):
        cls.__static_init__()
    return cls


# @CallStaticInit
class BaseSchema(metaclass=CallStaticInit):

    attr: int = 10

    @classmethod
    def __static_init__(cls):
        print('BaseSchema static init')


# aa = CallStaticInit()

bs = BaseSchema()
print(bs.my_attrr)
bs.my_func()

print(BaseSchema.__dict__)


#
# class MySchema(BaseSchema):
#
#     @classmethod
#     def __static_init__(cls):
#         print('MySchema static init')
