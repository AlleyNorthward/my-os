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

    names = {
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

    def __init__(self, width, value=0, name=None):
        self._width = int(width)
        mask = (1 << self._width) - 1
        self._value = int(value) & mask
        self.name = name or "REG"
        self._assert_is_generic_register(self.name)

    def _assert_is_generic_register(self, name):
        if name not in GenericRegister.names:
            raise TypeError("寄存器名填写错误!")

    @property
    def width(self):
        return self._width

    def read(self):
        return self._value

    def write(self, bit, value):
        if not (0 <= bit < self._width):
            raise ValueError("位超出了实际范围!")
        if value not in (0, 1):
            raise ValueError("单一位的值必须为0或1!")
        mask = 1 << bit
        if value:
            self._value |= mask
        else:
            self._value &= ~mask

    def __getitem__(self, bit):
        if isinstance(bit, slice):
            start = bit.start or 0
            stop = bit.stop
            size = stop - start
            return (self._value >> start) & ((1 << size) - 1)
        else:
            return (self._value >> bit) & 1

    def __repr__(self):
        return f"<{self.name}:{self._width}-bit 0x{self._value:0{self._width//4}X}>"

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

class EAX(GenericRegister):
    AL = BitField(0, 8)
    AH = BitField(8, 8)
    AX = BitField(0, 16)

    def __init__(self, value=0):
        super().__init__(32, value, name="EAX")

class EBX(GenericRegister):
    BL = BitField(0, 8)
    BH = BitField(8, 8)
    BX = BitField(0, 16)

    def __init__(self, value = 0):
        super().__init__(32, value, name = "EBX")

class ECX(GenericRegister):
    CL = BitField(0, 8)
    CH = BitField(8, 8)
    CX = BitField(0, 16)

    def __init__(self, value = 0):
        super().__init__(32, value, name = "ECX")

class EDX(GenericRegister):
    DL = BitField(0, 8)
    DH = BitField(8, 8)
    DX = BitField(0, 16)

    def __init__(self, value = 0):
        super().__init__(32, value, name = "EDX")

class EBP(GenericRegister):
    BP = BitField(0, 16)

    def __init__(self, value):
        super().__init__(32, value, name = "EBP")

class ESI(GenericRegister):
    SI = BitField(0, 16)

    def __init__(self, value):
        super().__init__(32, value, name = "ESI")

class EDI(GenericRegister):
    DI = BitField(0, 16)

    def __init__(self, value):
        super().__init__(32, value, name = "EDI")

if __name__ == "__main__":
    eax = EAX()
    eax.write(5, 1)
    eax[3:7] = 1
    print(hex(eax[3:7]))












