from abc import ABC, abstractmethod

class Register(ABC):

    @property
    @abstractmethod
    def width(self):
        pass

    @abstractmethod
    def read(self):
        pass

    @abstractmethod
    def write(self, bit, value):
        pass

class GenericRegister(Register):

    all = {
        "EAX",
        "EBX",
        "ECX",
        "EDX",
        "EBP",
        "ESI",
        "EDI",
        "ESP",
        "REG"
    }

    def __init__(self, width, value = 0, name = None):
        self._width = int(width)
        mask = (1 << self._width) - 1
        self._value = int(value) & mask
        self.name = name or "REG"
        GenericRegister._assert_is_generic_register(self.name)

    @classmethod
    def _assert_is_generic_register(cls, name):
        if name not in cls.all:
            raise TypeError("通用寄存器中没有该寄存器!")

    def _assert_bit(self, bit):
        if not (0 <= bit < self._width):
            raise ValueError("位超出了实际范围!")
    
    def _assert_value(self, value):
        if value not in (0, 1):
            raise ValueError("位值必须为0或1!")

    @property
    def width(self):
        return self._width
    
    def read(self, read_method = None):
        if read_method is None:
            return self._value
        return read_method(self._value)

    def write(self, bit, value):
        self._assert_bit(bit)
        self._assert_value(value)

        mask = 1 << bit

        if value:
            self._value |= mask
        else:
            self._value &= ~mask

    def __getitem__(self, bit):
        if isinstance(bit, slice):
            start = bit.start or 0
            stop = bit.stop
            if stop is None:
                stop = self._width
            size = stop - start
            return bin((self._value >> start) & ((1 << size) - 1))
        else:
            self._assert_bit(bit)
            return bin((self._value >> bit) & 1)

    def __setitem__(self, bit, value):
        if isinstance(bit, slice):
            start = bit.start or 0
            stop = bit.stop
            value_len = len(bin(value)) - 2
            if stop is None:
                stop = value_len + start
            if start > self._width or start + value_len > self._width:
                raise TypeError("超出阈值!")
            size = stop - start
            if start < 0 or size <= 0 or start + size >= self._width:
                raise TypeError("超出阈值!")
            maxv = (1 << size) - 1

            if not(0 <= value <= maxv):
                raise TypeError("value超出了切片范围!")

            mask = ((1 << size) - 1) << start
            self._value = (self._value & ~mask) | ((value << start) & mask)
        else:
            self.write(bit, value)

class BitField:
    def __init__(self, start, size=1):
        assert start >= 0 and size >= 1
        self.start = start
        self.size = size
        self.mask = ((1 << size) - 1) << start

    def __set_name__(self, owner, name):
        self.name = name  

    def __get__(self, instance, owner):
        if instance is None:
            return self
        val = (instance._value & self.mask) >> self.start
        return val

    def __set__(self, instance, value):
        maxv = (1 << self.size) - 1
        if not (0 <= value <= maxv):
            raise ValueError(f"value {value} out of range for {self.size} bits")
        instance._value = (instance._value & ~self.mask) | ((value << self.start) & self.mask)

if __name__ == "__main__":
    eax = GenericRegister(32, 0, "EAX")
    eax.write(3, 1)
    # eax[3:7] = 0b1111
    eax[6:12] = 0b1111
    eax[13:15] = 0b10
    print(eax.read(bin))
    print(eax[:])















