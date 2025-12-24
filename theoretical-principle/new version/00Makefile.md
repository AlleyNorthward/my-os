&emsp;&emsp;@author 巷北  
&emsp;&emsp;@time 2025.12.15 22:18  

# 简介
这里呢, 简单地介绍一下`Makefile`吧. 有了`cmake`的理解之后, 这部分变得也就不再那么地困难了. 

---

- [老版本](#老版本)
- [新版本](#新版本)

## 老版本

不多`bb`, 下面直接贴代码.  
~~~Makefile
all: src/os.c src/os.h src/bootloader_part.S
	$(TOOL_PREFIX)gcc $(CFLAGS) src/bootloader_part.S
	$(TOOL_PREFIX)gcc $(CFLAGS) src/os.c	
	$(TOOL_PREFIX)ld -m elf_i386 -Ttext=0x7c00 bootloader_part.o os.o -o os.elf
	${TOOL_PREFIX}objcopy -O binary os.elf os.bin
	${TOOL_PREFIX}objdump -x -d -S  os.elf > os_dis.txt	
	${TOOL_PREFIX}readelf -a  os.elf > os_elf.txt	
	dd if=os.bin of=../image/disk.img conv=notrunc

clean:
	rm -f *.elf *.o *.bin *.txt

run:
	start qemu-system-i386 -m 128M -s -S  -drive file=../image/disk.img,index=0,media=disk,format=raw

debug:
	$(TOOL_PREFIX)gdb os.elf \
		-ex "enable pretty-printing" \
		-ex "set disassembly-flavor intel" \
		-ex "set architecture i8086" \
		-ex "target remote 127.0.0.1:1234" \
		-ex "until *0x7c00" \

qemu:
	start qemu-system-i386 -fda os.elf -monitor stdio -S -display sdl
~~~
这部分代码呢, 比较明确, 就是传统的命令行似的编写, 对于新手而言, 确实是十分地友好. 我在有了一定的理解之后呢(各个层面的), 打算不限于此, 期望能够新建一个`build`文件夹, 将所有的编译文件放于此, 这样的话, 不会显得太乱, 能够清晰些, 而且方便管理. 所以向`ai`请教了一下, 期望能够更明确一些. 下面是新版本的`Makefile`脚本代码.

## 新版本

整体代码显示如下, 这里会尽可能详细地分析一下. 

~~~Makefile
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
~~~

写的时候没有高亮显示, 看着也确实是非常地难受. 我们分段分析一下吧.  

~~~Makefile
TOOL_PREFIX = x86_64-elf-

# GCC编译参数
CFLAGS = -g -c -O0 -m32 -fno-pie -fno-stack-protector -nostdlib -nostdinc
QEMU = qemu-system-i386
PORT = 1234
~~~

- `Makefile`脚本跟`cmake`脚本类似, 变量, 路径, 编译等等, 都没做好区分, 相对而言仍还是十分地混乱. 但好在有了一定的经验, 这部分也不是那么地复杂了.
- 由于编译链有很多的编译器, 前缀都是`x86_64-elf-`, 所以直接通过这个变量, 统一命名一下, 显得整齐一些.
- 接下来就是相关的编译参数以及端口(`PORT`)号, 这里呢, 不做解释, 具体地可以去`ai`搜索一下, 看看什么意思.

~~~Makefile
SRC = src/os.c src/bootloader_part.S
HEADERS = src/os.h

BUILD_DIR = build

BOOT_O = $(BUILD_DIR)/bootloader_part.o
OS_O = $(BUILD_DIR)/os.o
OS_ELF = $(BUILD_DIR)/os.elf
OS_BIN = $(BUILD_DIR)/os.bin
DIS_TXT = $(BUILD_DIR)/os_dis.txt
ELF_TXT =$(BUILD_DIR)/os_elf.txt
~~~

- 这些就是待编译的原文件以及头文件了. 后面的是编译生成的附加文件. 那么, `.o`, `.elf`, `.bin`, 文件, 是什么意思呢? 
    - `.o`文件, 指的就是目标文件(`Object File`).
        - 由编译器(`gcc`)把源代码(`.c`或`.S`汇编)编译生成.
        - 每个`.c`或`.S`文件会生成对应的`.o`文件.
        - 特点:
            - **机器码**, 但还不是最终可执行程序
            - 可能包含未解析的符号(函数或变量引用其他`.o`文件中的)
            - 用于链接(`link`)生成最终程序.
            - 比如下面的命令行.
            ~~~powershell
            gcc -c src/os.c -o os.o
            gcc -c src/bootloader_part.S -o bootloader_part.o
            ~~~
            - `-c`表示只编译, 不链接, 生成`.o`文件.
- `.elf`文件, 可执行文件.
    - 通过链接器`ld`, 将所有的`.o`文件链接生成`.elf`文件
    - 特点:
        - **完整程序**, 可以在对应架构上运行.
        - 并且保留调试信息(符号表)
        - `ELF`是`Linux/Unix`系统常用的可执行文件格式.
        ~~~powershell
        ld -m elf_i386 -Ttext=0x7c00 bootloader_part.o os.o -o os.elf
        ~~~
    - `os.elf`就是链接后的可执行文件
    - 可以用:
    ~~~powershell
    objdump -d os.elf
    readelf -a os.elf
    ~~~
    - 查看汇编和`ELF`结构信息.
- `.bin`文件, 是二进制镜像文件, 从`.elf`转换而来, 用`objcopy`:
~~~powershell
objcopy -O binary os.elf os.bin
~~~
- 特点:
    - **纯机器码**, 没有`ELF`头或符号表.
    - 可以直接写入磁盘镜像或烧录到设备(比如启动扇区, 嵌入式板子)
- 也就是说:
    - `.o`是编译结果(中间目标)
    - `.elf`是链接结果(可执行程序+调试信息)
    - `.bin`纯二进制文件(裸机可用)
- 好了, 整体前置准备弄完了, 接下来就是关键的命令了.

~~~Makefile
all:$(BUILD_DIR) $(OS_BIN)
~~~

- 这个`all`命令, 其实就是当我们执行`make`的时候, 执行它.(我感觉`make all`=`make`, 还没有测试) 测试了, `make`会默认执行第一个, 只要`all`在第一个, 就会默认执行它.
- 这里有个关键概念, 就是<mark>驱动以来</mark>概念. 什么意思呢? `all`其实就是我们自定义个的一个`target`, 要完成它的前提, 需要有`$(BUILD_DIR)`和`$(OS_BIN)`. 那么当我们执行`make`的时候(默认执行第一个, 也就是`make all`), 会去查找`$(BUILD)`, 不存在就创建, 存在就接着运行`$(OS_BIN)`. 

~~~Makefile
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
~~~

- 这些其实就是整个的运行链. 每个都可以单独运行(前提是链条完整).
- 我们人工执行的是`all`, 它先看`$(BUILD_DIR)`, 结束后, 又去看`$(OS_BIN)`. 
- 执行`$(OS_BIN)`时, 它依赖于`$(OS_ELF)`, 又会接着执行`$(OS_ELF)`. 后续发现, 它又依赖于`$(BOOT_O) $(OS_O)`, 就会执行对应的文件. 依次累推下去.
- 最后我们会发现, 整个编译链, 跟我们上面的描述的编译链是完全一样的.
- 对于`$<`, 代表的是当前依赖项(第一个依赖. 只有一个, 或者值关心一个时, 可以用), `$@`是生成的目标对象, 也就是`target`. `$^`是代表所有依赖. 其中, 链接阶段必须使用`$^`.

- 整体上来看, 似乎并不困难. 我觉得应该要明确, 解释型语言, 可以直接启动运行. 而编译型语言, 需要先编译, 后启动运行. 启动运行很明确, 我们写好代码之后, 运行可以查看结果. 但是编译呢, 它本身也是一个需要配置(编写)的. 最初学习时, 我们很容易忽视编译的作用, 因为都是单文件运行, 编译没有那么地复杂. 可是随着文件逐渐增加, 各个文件由于彼此的依赖项, 编译也变得复杂了起来. 这个过程, 在我的理解下, 并不是简单地顺次将文件逐个编译下来. 因为存在导包的问题, 如果一个文件引用了另一个文件, 那么我在编译该文件时, 其依赖文件是否需要编译呢? 假如编译了, 等轮到依赖文件时, 是否需要重新编译呢? 等等等等. 所以, 像`Makefile`, `cmake`, 这些东西, 肯定有其存在的必要和意义. 







































