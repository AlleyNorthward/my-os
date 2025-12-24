TOOL_PREFIX = x86_64-elf-

# GCC编译参数
CFLAGS = -g -c -O0 -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc
QEMU = qemu-system-i386
PORT = 1234

SRC = src/os.c src/bootloader_part.S
HEADERS = src/os.h

BUILD_DIR = build

BOOT_O = $(BUILD_DIR)/bootloader_part.o
OS_O = $(BUILD_DIR)/os.o
OS_ELF = $(BUILD_DIR)/os.elf
OS_BIN = $(BUILD_DIR)/os.bin
DIS_TXT = $(BUILD_DIR)/os_dis.txt
ELF_TXT =$(BUILD_DIR)/os_elf.txt

all:$(BUILD_DIR) $(OS_BIN)

$(BUILD_DIR):
	mkdir -p $(BUILD_DIR)

$(BOOT_O): src/bootloader_part.S
	$(TOOL_PREFIX)gcc $(CFLAGS) $< -o $@

$(OS_O): src/os.c $(HEADERS)
	$(TOOL_PREFIX)gcc $(CFLAGS) $< -o $@

$(OS_ELF): $(BOOT_O) $(OS_O)
	$(TOOL_PREFIX)ld -m elf_i386 -Ttext=0x7c00 $^ -o $@

$(OS_BIN): $(OS_ELF)
	$(TOOL_PREFIX)objcopy -O binary $< $@
	$(TOOL_PREFIX)objdump -x -d -S $< > $(DIS_TXT)
	$(TOOL_PREFIX)readelf -a $< > $(ELF_TXT)
	dd if=$@ of=./image/disk.img conv=notrunc

.PHONY: all clean run debug qemu

clean:
	rm -rf $(BUILD_DIR)

run:
	start $(QEMU) -m 128M -s -S -drive file=./image/disk.img,index=0,media=disk,format=raw

debug:
	$(TOOL_PREFIX)gdb $(OS_ELF) \
		-ex "enable pretty-printing" \
		-ex "set disassembly-flavor intel" \
		-ex "set architecture i8086" \
		-ex "target remote 127.0.0.1:1234" \
		-ex "until *0x7c00"

qemu:
	start $(QEMU) -fda $(OS_ELF) -monitor stdio -S -display sdl
