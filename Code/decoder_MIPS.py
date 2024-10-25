from enum import Enum

# Trabalho de Implementação do decoder de instruções do processador MIPS, com os respectivos métodos que faltam feitos por mim, João Vitor Balduino Lopes

class InstrType(Enum):
    R = 1
    I = 2
    J = 3

# Aqui temos o contrutor da classe Instrução, que guarda e sapara os principais componentes da instrução.
# Como o opcode, que indica a operação da instrução, o tipo, sendo R, I ou J, o nome da instrução, seus campos e seu mnemônico.
class Instruction:
    def __init__(self, bits: str) -> None:
        self.bits = bits   
        self.opcode = int(bits[:6], 2) # Aqui guarda o opcode, ou seja, os 6 primeiros bits da instrução.
        self.type = InstrType.R if self.opcode == 0 else \
                    InstrType.J if self.opcode == 2 or self.opcode == 3 else InstrType.I
        self.fields = self.get_fields(self.bits, self.type) # Aqui guarda os campos da instrução, que são os bits que a compõem.
        self.name = MIPSDecoder.FUNCTIONS.get(int(bits[26:], 2)) if self.type == InstrType.R else \
                    MIPSDecoder.FUNCTIONS.get(self.opcode) if self.type == InstrType.J else MIPSDecoder.OPCODES.get(self.opcode) # Implemente aqui para este atributo receber o nome da instrução. Considere usar MIPSDecoder.OPCODES |  MIPSDecoder.FUNCTIONS
        self.mnemonic = self.get_mnemonic(self.name, self.fields, self.type) # Aqui guarda o mnemonico, a estrutura da instrução.
    
    def __str__(self) -> str:
        return self.mnemonic
    

    # Esse método tem por objetivo receber os bits da instrução e separá-los em seus respectivos campos.
    # Para isso, é necessário saber os bits e o tipo da instrução, que são passados como parâmetros.
    # Em seguida é feita a separação através do slice das posições dos bits, e a conversão de binário para inteiro.
    # Por fim, é retornado um dicionário com os campos da instrução.
    @staticmethod
    def get_fields(bits: str, type: InstrType) -> dict: 
        opcode = int(bits[:6], 2)
        rs = int(bits[6:11], 2)
        rt = int(bits[11:16], 2)
        if type == InstrType.R: 
            # Esta condição retorna os campos para instruções do Tipo R.
            # que contém os campos rd, rt e rs, que são os registradores, além dos campos funct e shamt.
            rd = int(bits[16:21], 2)
            shamt = int(bits[21:26], 2)
            funct = int(bits[26:], 2)
            return {'opcode': opcode, 'rs': rs, 'rt': rt, 'rd': rd, 'shamt': shamt, 'funct': funct}
        elif type == InstrType.I: 
            # Esta condição retorna os campos para instruções do Tipo I,
            # que contém o campo imm, que é o imediato.
            imm = int(bits[16:], 2)
            return {'opcode': opcode, 'rs': rs, 'rt': rt,'imm': imm}
        elif type == InstrType.J: 
            # Esta condição retorna os campos para instruções do Tipo J,
            # que contém o label, ou seja, o campo de destino de 'pulo' que a instrução realiza.
            label = int(bits[6:], 2)
            return {'opcode': opcode, 'label': label}


    # Esse método tem por objetivo receber os campos, o nome e o tipo da instrução e retornar o mnemônico.
    # Dependendo do tipo de instrução que o método receber ele irá fazer uma busca no dicionário que armazena os campos,
    # e irá substituir os campos pelos valores , como os registradores, o imediato como inteiro, assim como o label.
    # Para isso, usa o dicionário de TEMPLATES como fórmula para realizar a substituição dos operandos, pois guarda a estrutura da instrução.
    # Por fim, é retornado o mnemônico.
    @staticmethod
    def get_mnemonic(name: str, fields: dict, type: InstrType) -> str:
        if type == InstrType.J:
            opcode = MIPSDecoder.FUNCTIONS.get(fields.get("opcode"))
            label = fields.get("label")
            mnemonico = f"{opcode} {label}"
        elif type == InstrType.R:
            mnemonico = MIPSDecoder.TEMPLATE_R[name]
            if mnemonico == 'break' or mnemonico == 'syscall':  # Excessões para instruções-R que apenas apresentam o campo function.
                return mnemonico
            for campo, valor in fields.items():  # Este laço 'for' realiza a busca por cada campo e valor no dicionário.
                if campo in ['rs', 'rt', 'rd'] and valor in MIPSDecoder.REGISTERS and valor != 0:  # Verifica se a chave é um registrador e se não está zerado.
                    valor = MIPSDecoder.REGISTERS[valor]  # Aqui é feita a substituição do valor do campo pelo valor correspondente no dicionário de registradores.
                mnemonico = mnemonico.replace(f'{campo}', str(valor))
        elif type == InstrType.I:
            mnemonico = MIPSDecoder.TEMPLATE_I[name]
            for campo, valor in fields.items():
                if campo in ['rs','rt','rd'] and valor in MIPSDecoder.REGISTERS and valor != 0:
                    valor = MIPSDecoder.REGISTERS[valor]
                mnemonico = mnemonico.replace(f'{campo}', str(valor))
        return mnemonico



class MIPSDecoder:
    
    REGISTERS = {
        0: '$zero',
        1: '$at',
        2: '$v0',
        3: '$v1',
        4: '$a0',
        5: '$a1',
        6: '$a2',
        7: '$a3',
        8: '$t0',
        9: '$t1',
        10: '$t2',
        11: '$t3',
        12: '$t4',
        13: '$t5',
        14: '$t6',
        15: '$t7',
        16: '$s0',
        17: '$s1',
        18: '$s2',
        19: '$s3',
        20: '$s4',
        21: '$s5',
        22: '$s6',
        23: '$s7',
        24: '$t8',
        25: '$t9',
        26: '$k0',
        27: '$k1',
        28: '$gp',
        29: '$sp',
        30: '$s8',
        31: '$ra'
    }
    
    OPCODES = {
        0b000000: '[R-Type]',
        # I-Type Instructions
        0b001000: 'addi',	            # addi rt, rs, imm
        0b001001: 'addiu',	            # addiu rt, rs, imm
        0b001100: 'andi',	            # andi rt, rs, imm
        0b000100: 'beq',	            # beq rs, rt, label
        0b000001: 'bgez', # rt = 00001	# bgez rs, label
        0b000111: 'bgtz', # rt = 00000	# bgtz rs, label
        0b000110: 'blez', # rt = 00000	# blez rs, label
        0b000001: 'bltz', # rt = 00000	# bltz rs, label
        0b000101: 'bne',	            # bne rs, rt, label
        0b100000: 'lb',	                # lb rt, imm(rs)
        0b100100: 'lbu',	            # lbu rt, imm(rs)
        0b100001: 'lh',	                # lh rt, imm(rs)
        0b100101: 'lhu',	            # lhu rt, imm(rs)
        0b001111: 'lui',	            # lui rt, imm
        0b100011: 'lw',	                # lw rt, imm(rs)
        0b110001: 'lwc1',	            # lwc1 rt, imm(rs)
        0b001101: 'ori',	            # ori rt, rs, imm
        0b101000: 'sb',	                # sb rt, imm(rs)
        0b001010: 'slti',	            # slti rt, rs, imm
        0b001011: 'sltiu',	            # sltiu rt, rs, imm
        0b101001: 'sh',	                # sh rt, imm(rs)
        0b101011: 'sw',	                # sw rt, imm(rs)
        0b111001: 'swc1',	            # swc1 rt, imm(rs)
        0b001110: 'xori',	            # xori rt, rs, imm
    }

    FUNCTIONS = {
        # R-Type Instructions
        0b000000: None, 
        0b100000: 'add',	            # add rd, rs, rt
        0b100001: 'addu',	            # addu rd, rs, rt
        0b100100: 'and',	            # and rd, rs, rt
        0b001101: 'break',	            # break
        0b011010: 'div',	            # div rs, rt
        0b011011: 'divu',	            # divu rs, rt
        0b001001: 'jalr',	            # jalr rd, rs
        0b001000: 'jr',	                # jr rs
        0b010000: 'mfhi',	            # mfhi rd
        0b010010: 'mflo',	            # mflo rd
        0b010001: 'mthi',	            # mthi rs
        0b010011: 'mtlo',	            # mtlo rs
        0b011000: 'mult',	            # mult rs, rt
        0b011001: 'multu',	            # multu rs, rt
        0b100111: 'nor',	            # nor rd, rs, rt
        0b100101: 'or',	                # or rd, rs, rt
        0b000000: 'sll',	            # sll rd, rt, sa
        0b000100: 'sllv',	            # sllv rd, rt, rs
        0b101010: 'slt',	            # slt rd, rs, rt
        0b101011: 'sltu',	            # sltu rd, rs, rt
        0b000011: 'sra',	            # sra rd, rt, sa
        0b000111: 'srav',	            # srav rd, rt, rs
        0b000010: 'srl',                # srl rd, rt, sa
        0b000110: 'srlv',	            # srlv rd, rt, rs
        0b100010: 'sub',	            # sub rd, rs, rt
        0b100011: 'subu',	            # subu rd, rs, rt
        0b001100: 'syscall',	        # syscall
        0b100110: 'xor',	            # xor rd, rs, rt
        # J-Type Instructions
        0b000010: 'j',                  # j label
        0b000011: 'jal'                 # jal label
    }
    TEMPLATE_R = {
        # Este dicionário guarda a estrutura das instruções do Tipo R,
        # sendo a chave, o nome da instrução, e o valor, a sua estrutura.
        'add': 'rd, rs, rt',
        'addu': 'rd, rs, rt',
        'and': 'rd, rs, rt',
        'break': 'break',
        'div': 'rs, rt',
        'divu': 'rs, rt',
        'jalr': 'rd, rs',
        'jr': 'rs',
        'mfhi': 'rd',
        'mthi': 'rs',
        'mthi': 'rs',
        'mflo': 'rd',
        'mthi': 'rs',
        'mtlo': 'rs',
        'mult': 'rs, rt',
        'multu': 'rs, rt',
        'nor': 'rd, rs, rt',
        'or': 'rd, rs, rt',
        'sll': 'rd, rt, sa',
        'sllv': 'rd, rt, rs',
        'slt': 'rd, rs, rt',
        'sltu': 'rd, rs, rt',
        'sra': 'rd, rt, sa',
        'srav': 'rd, rt, rs',
        'srl': 'rd, rt, sa',
        'srlv': 'rd, rt, rs',
        'sub': 'rd, rs, rt',
        'subu': 'rd, rs, rt',
        'syscall': 'syscall',
        'xor': 'rd, rs, rt'
    }
    TEMPLATE_I = { 
        # Este dicionário guarda as estruturas para cada instrução do Tipo I, 
        # sendo a chave, o nome da instrução, e o valor, a sua estrutura.
        'addi': 'rt, rs, imm',
        'addiu': 'rt, rs, imm', 
        'andi': 'rt, rs, imm',
        'beq': 'rs, rt, imm',
        'bgez': 'rs, imm',
        'bgtz': 'rs, imm',
        'blez': 'rs, imm',
        'bltz': 'rs, imm',
        'bne': 'rs, rt, imm',
        'lb': 'rt, imm(rs)',
        'lbu': 'rt, imm(rs)',
        'lh': 'rt, imm(rs)',
        'lhu': 'rt, imm(rs)',
        'lui': 'rt, imm',
        'lw': 'rt, imm(rs)',
        'lwc1': 'rt, imm(rs)',
        'ori': 'rt, rs, imm',
        'sb': 'rt, imm(rs)',
        'slti': 'rt, rs, imm',
        'sltiu': 'rt, rs, imm',
        'sh': 'rt, imm(rs)',
        'sw': 'rt, imm(rs)',
        'swc1': 'rt, imm(rs)',
        'xori': 'rt, rs, imm',
    }
    def parse_instruction(self, bits: str) -> Instruction:
        return Instruction(bits)
    
    # Esse método tem por objetivo retornar os sinais de controle para cada instrução
    # Sendo eles {ALUSrc, Branch, MemRead, MemToReg, MemWrite, RegDst, RegWrite}

    def decode_instruction(self, instr: str) -> dict:
        signals = {'ALUSrc': 0, 
                'Branch': 0, 
                'MemRead': 0, 
                'MemToReg': 0, 
                'MemWrite': 0, 
                'RegDst': 0, 
                'RegWrite': 0,
                'Jump': 0
                }
        opcode_I = MIPSDecoder.TEMPLATE_I[instr.name]

        if instr.type == InstrType.R: # Condição para os sinais de controle que são alterados para instruções do tipo R.
            opcode_R = MIPSDecoder.TEMPLATE_R[instr.name]
            signals['RegDst'] = 1 if opcode_R.startswith('rd') else 0  # O campo 'rd' é o registrador de destino, então retorna 1 se tiver 'rd' senão 0
            signals['RegWrite'] = 1 if opcode_R.startswith('r') and instr.name not in [   # Retorna 1 se houver escrita no banco de registradores, tirando as excessões
                'break', 'div', 'divu', 'jalr', 'mult', 'multu', 'sycall'] else 0 
            signals['Jump'] = 1 if instr.name.startswith('j') else 0   # Se a instrução for do tipo 'Jump', aciona 1 no sinal de controle

        elif instr.type == InstrType.I:  # Condição para os sinais de controle que são alterados para instruções do tipo I.
            opcode_I = MIPSDecoder.TEMPLATE_I[instr.name]
            signals['Branch'] = 1 if instr.name.startswith('b') else 0  # Se a instrução for do tipo 'Branch', aciona o sinal de controle para 1
            signals['RegDst'] = 'X' if signals['Branch'] == 1 or (instr.name.startswith('s') and instr.name not in ['slt', 'sltu']) else 0  # Instruções Tipo I não apresentam sinal 'RegDst'
            signals['ALUSrc'] = 1 if signals['Branch'] == 0 else 0  # Retorna 1 se a segunda entrada da ULA for um imediato, caso contrário, retorna 0
            signals['MemRead'] = 1 if instr.name.startswith('l') else 0  # Se a instrução for do tipo 'Load', aciona 1 no sinal de controle de leitura da memória
            signals['MemWrite'] = 1 if instr.name.startswith('s') and instr.name not in ['slt', 'sltu'] else 0  # Se a instrução for do tipo 'Store', aciona 1 no sinal de controle de escrita na memória
            signals['MemToReg'] = 1 if instr.name.startswith('l') else \
                'X' if instr.name.startswith('s') or instr.name.startswith('b') else 0  # Se a instrução for do tipo 'Load', aciona 1 no sinalde escrita no BR da dados de origem da memória
            signals['RegWrite'] = 1 if opcode_I.startswith('rt') else 0  # Aciona 1 na escrita no banco de registradores caso tenha 'rt', senão 0

        elif instr.type == InstrType.J:  # Condição para os sinais de controle que são alterados para instruções do tipo J.
            signals['Jump'] = 1  # Apenas é acionado 1 para o sinal de controle 'Jump', o resto dos sinais é zerado
        return signals

    @staticmethod
    def get_register_name(register_index: int) -> str:
        return MIPSDecoder.REGISTERS[register_index]
    
    @staticmethod
    def get_register_index(register_name: str) -> int:
        inv_map = { v: k for k, v in MIPSDecoder.REGISTERS.items() }
        return inv_map[register_name]
    

def parse_int(num_str: str) -> int:
    num_str = num_str.lower()
    base = 2 if num_str.startswith('0b') else 8 if num_str.startswith('0o') else \
           16 if num_str.startswith('0x') else 10
    return int(num_str, base)


def print_output(instr: Instruction, signals: dict) -> None:
    print(f'Instrução: {instr.name} {instr.mnemonic}')
    print(f'- Tipo: {instr.type.name}')
    print(f'- Campos:')
    for field, value in instr.fields.items():
        if field == 'opcode' and instr.opcode != 0:
            print(f'\t{field}: {value} ({MIPSDecoder.OPCODES[value]})')
        elif field == 'funct':
            print(f'\t{field}: {value} ({MIPSDecoder.FUNCTIONS[value]})')
        elif field == 'rs' or field == 'rt' or field == 'rd':
            print(f'\t{field}: {value} ({MIPSDecoder.REGISTERS[value]})')
        else:
            print(f'\t{field}: {value}')
    print(f'- Sinais de controle:')
    for signal, value in signals.items():
        print(f'\t{signal}: {value}')


def main():
    decoder = MIPSDecoder()
    print("--- [Decodificar de instruções MIPS] ---")
    while True:
        print("Digite o [inteiro] da instrução | [''] para sair:", end=' ')
        input_value = input().strip()
        if not input_value:
            break
        instr = decoder.parse_instruction(f'{parse_int(input_value):032b}')
        signals = decoder.decode_instruction(instr)
        print_output(instr, signals)
        

if __name__ == '__main__':
    main()
