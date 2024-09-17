# 汇编器
class assembler:
    def __init__(self):
        # 操作码和寄存器字典
        self.opcode_dict = {
            'add': '00000',      'addi': '10000',
            'sub': '00001',      'subi': '10001',
            'mul': '00010',      'muli': '10010',
            'and': '00011',      'andi': '10011',
            'or' : '00100',      'ori' : '10100',
            'xor': '00101',      'xori': '10101',
            'sll': '00110',      'slli': '10110',
            'srl': '00111',      'srli': '10111',
            'beq': '01000',      'lw'  : '11000',
            'blt': '01001',      'sw'  : '11001',

            'csrr': '11010',
            'csrw': '11011',
            'jal' : '11010',
            'jr'  : '11011',
            'li'  : '11001',
            'rc'  : '11111'
        }
        self.reg_dict = {
            's0': 0,
            'a1': 1,
            'a2': 2,
            'a3': 3,
            'a4': 4,
            'a5': 5,
            'ra': 6,
            'sp': 7
        }

        # 生成的机器码和其他辅助变量
        self.machine_code = ""
        self.machine_code_basic = ""
        self.labels = {}
        self.address = 0

    def process_labels(self, instruction):
        # 遍历指令，提取标签和地址
        for line in instruction.strip().split('\n'):
            line = line.strip()
            if line:
                if line.endswith(':'):
                    self.labels[line[:-1]] = self.address
                else:
                    self.address += 1
        self.address = 0  # 重置地址以处理指令

    def process_instructions(self, instruction):
        # 处理指令
        for line in instruction.strip().split('\n'):
            line = line.strip()
            if line:
                components = line.replace(',', '').split()

                # 排除标签行不进行操作码处理
                if not line.endswith(':'):
                    self.address += 1
                    self.process_opcode(components)

    def process_opcode(self, components):
        rd = '000'
        rs = '000'
        imm = '00000'
        Imm = '00000000'

        opcode = components[0]
        if opcode in {'add', 'sub', 'and', 'or', 'xor', 'sll', 'srl'}:
            rd = components[1]
            rs = components[3]
            self.generate_machine_code(opcode, rd, rs, 0)
        elif opcode in {'addi', 'subi', 'andi', 'ori', 'xori', 'slli', 'srli'}:
            rd = components[1]
            rs = 's0'
            imm = -1 * int(components[3]) // 4
            self.generate_machine_code(opcode, rd, rs, imm)
        elif opcode in {'lw', 'sw', 'csrr', 'csrw'}:
            rd = components[1]
            imm, rs = components[2][:-1].split('(')
            imm = -1 * int(imm) // 4
            self.generate_machine_code(opcode, rd, rs, imm)
        elif opcode in {'blt', 'beq'}:
            rd = components[1]
            rs = components[2]
            imm = self.labels[components[3]]
            self.generate_machine_code(opcode, rd, rs, imm)
        elif opcode in {'jr', 'li'}:
            rd = components[1]
            Imm = int(components[2])
            self.generate_machine_code(opcode, rd, None, Imm)
        elif opcode in {'jal'}:
            rd = components[1]
            Imm = self.labels[components[2]]
            self.generate_machine_code(opcode, rd, None, Imm)
        elif opcode == 'rc':
            rd = 's0'
            Imm = '00000000'
            self.generate_machine_code(opcode, rd, None, Imm)

    def generate_machine_code(self, opcode, rd, rs, imm):
        # 生成机器码
        if opcode == 'li':
            Imm = bin(imm)[2:].zfill(8)
            self.machine_code_basic += f"{opcode}\tr{self.reg_dict.get(rd)},  0b{Imm}\n"
            rd = bin(self.reg_dict.get(rd))[2:].zfill(3)
            opcode = self.opcode_dict.get(opcode)
            self.machine_code += Imm + rd + opcode + '\n'
        elif opcode == 'jal':
            Imm = bin(imm)[2:].zfill(8)
            self.machine_code_basic += f"{opcode}\t 0,  0b{Imm}\n"
            opcode = self.opcode_dict.get(opcode)
            self.machine_code += Imm + '000' + opcode + '\n'
        elif opcode == 'jr':
            self.machine_code_basic += f"{opcode}\tr{self.reg_dict.get(rd)},  0, 0b00000\n"
            rd = bin(self.reg_dict.get(rd))[2:].zfill(3)
            opcode = self.opcode_dict.get(opcode)
            self.machine_code += '00000' + '000' + rd + opcode + '\n'
        elif opcode == 'call':
            Imm = bin(imm)[2:].zfill(8)
            self.machine_code_basic += f"li\tr{self.reg_dict.get(rd)},  0b{Imm}\n"
            rd = bin(self.reg_dict.get(rd))[2:].zfill(3)
            opcode = self.opcode_dict.get(opcode)
            self.machine_code += Imm + rd + opcode + '\n'
            # TODO: 这里的机械码生成有问题 应该有两步：储存此时pc到ra，跳转到标签
        else:
            if imm < 0:
                imm = bin(imm & 0b11111)[2:].zfill(5)
            else:
                imm = format(imm, '05b')
            self.machine_code_basic += f"{opcode}\tr{self.reg_dict.get(rd)}, r{self.reg_dict.get(rs)}, 0b{imm}\n"

            rd = bin(self.reg_dict.get(rd))[2:].zfill(3)
            rs = bin(self.reg_dict.get(rs))[2:].zfill(3)
            opcode = self.opcode_dict.get(opcode)
            self.machine_code += imm + rs + rd + opcode + '\n'

    def assemble(self, instruction):
        # 重新从头处理指令，生成机器码
        self.process_labels(instruction)
        self.process_instructions(instruction)
        return self.machine_code

    def getlabel(self):
        return self.labels

    def get_codebasic(self):
        return self.machine_code_basic

# 测试用例
if __name__ == "__main__":
    program_code = """
add:
    addi    sp, sp, -48
    sw      ra, 44(sp)
    sw      s0, 40(sp)
    addi    s0, sp, 48
    sw      a1, -36(s0)
    sw      a2, -40(s0)
    lw      a1, -36(s0)
    lw      a2, -40(s0)
    add     a1, a1, a2
    sw      a1, -20(s0)
    lw      ra, 44(sp)
    lw      s0, 40(sp)
    addi    sp, sp, 48
    jr      ra, 0
main:
    li      a1, 1
    sw      a1, -20(s0)
    li      a1, 2
    sw      a1, -24(s0)
    lw      a1, -20(s0)
    lw      a2, -24(s0)
    jal     ra, add
    """

    Assembler = assembler()
    machine_code = Assembler.assemble(program_code)
    print(machine_code)
    print(Assembler.getlabel())
    print(Assembler.get_codebasic())
