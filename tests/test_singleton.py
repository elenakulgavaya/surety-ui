from surety.ui.singleton import Singleton


def test_singleton_creates_single_instance():
    """Verify that a class using Singleton metaclass creates only one instance."""
    class SingletonClass(metaclass=Singleton):
        def __init__(self):
            self.value = 42

    instance1 = SingletonClass()
    instance2 = SingletonClass()

    assert instance1 is instance2
    assert id(instance1) == id(instance2)


def test_singleton_preserves_state():
    """Verify that singleton instances preserve state across accesses."""
    class StatefulSingleton(metaclass=Singleton):
        def __init__(self):
            self.counter = 0

        def increment(self):
            self.counter += 1

    instance1 = StatefulSingleton()
    instance1.increment()
    instance1.increment()

    instance2 = StatefulSingleton()
    assert instance2.counter == 2


def test_singleton_multiple_classes():
    """Verify that different singleton classes maintain separate instances."""
    class SingletonA(metaclass=Singleton):
        pass

    class SingletonB(metaclass=Singleton):
        pass

    a = SingletonA()
    b = SingletonB()

    assert a is not b
    assert isinstance(a, SingletonA)
    assert isinstance(b, SingletonB)
