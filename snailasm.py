import sys
import os
import time
import re

start = time.perf_counter()
code_line = 0
binary_line = 0
binary_list = []

def error(message="error!"):
    print(message)
    raise SystemExit()

def to_twos_complement(n, bits=8):
    if n >= 0:
        return n
    return (1 << bits) + n

def is_valid_identifier(name):
    # 1. 이름이 문자나 _로 시작하는지 검사
    if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name):
        return False
    
    # 2. 명령어(r_type/i_type/pseudo/register)랑 충돌하는지 검사
    if name in r_type_map or name in i_type_map or name in pseudo or name in registers:
        return False

    return True


def standard_r(tokens):
    bin_opcode = r_type_map[tokens[0]][0]
    if (len(tokens) != r_type_map[tokens[0]][1] + r_type_map[tokens[0]][2] + r_type_map[tokens[0]][3] + 1):#길이가 다를때
        error(f"line: {code_line}\nIncorrect number of operands for '{tokens[0]}': expected {r_type_map[tokens[0]][1] + r_type_map[tokens[0]][2] + r_type_map[tokens[0]][3]}, got {len(tokens) - 1}")
    
    #if (tokens[0] not in r_type_map):
    #    error()

    print(tokens)

    if (r_type_map[tokens[0]][1] and tokens[1] not in registers):
        error(f"line: {code_line}\nInvalid destination register '{tokens[1]}'. Register names must be between r0 and r7 or a defined symbol.")
    if (r_type_map[tokens[0]][2] and tokens[2] not in registers):
        error(f"line: {code_line}\nInvalid source register '{tokens[2]}'. Register names must be between r0 and r7 or a defined symbol.")
    if (r_type_map[tokens[0]][3] and tokens[3] not in registers):
        error(f"line: {code_line}\nInvalid source register '{tokens[3]}'. Register names must be between r0 and r7 or a defined symbol.")
    
    RD = int(tokens[1][1:]) if r_type_map[tokens[0]][1] else 0
    RS1 = int(tokens[2][1:]) if r_type_map[tokens[0]][2] else 0
    RS2 = int(tokens[3][1:]) if r_type_map[tokens[0]][3] else 0

    return bin_opcode + "" + f"{RD:03b}"[::-1] + "" + f"{RS1:03b}"[::-1] + "" + f"{RS2:03b}"[::-1] + "\n"

def standard_i(tokens):
    bin_opcode = i_type_map[tokens[0]][0]
    if (len(tokens) != i_type_map[tokens[0]][1] + i_type_map[tokens[0]][2] + 1):#길이가 다를때
        error(f"line: {code_line}\nIncorrect number of operands for '{tokens[0]}': expected {i_type_map[tokens[0]][1] + i_type_map[tokens[0]][2] + 1}, got {len(tokens)}")
    
    #if (tokens[0] not in r_type_map):
    #    error()

    R = 0
    IMM = 0
    if (i_type_map[tokens[0]][1] and i_type_map[tokens[0]][2] == 0):
        R = int(tokens[1][1:])
    elif (not i_type_map[tokens[0]][1] and i_type_map[tokens[0]][2] == 1):
        IMM = int(tokens[1])
    else:
        R = int(tokens[1][1:])
        IMM = int(tokens[2])

    if (i_type_map[tokens[0]][1] and R not in range(0, 8)):
        error(f"line: {code_line}\nInvalid register 'R{R}'")
    if (i_type_map[tokens[0]][2] and (IMM > 127 or -128 > IMM)):
        error(f"line: {code_line}\nImmediate value {IMM} out of range (-128 to 128)")
    
    IMM = to_twos_complement(IMM, bits=8)
    return bin_opcode + "" + f"{R:03b}"[::-1] + "" + f"{IMM:08b}"[::-1] + "\n"

def jump(tokens):
    bin_opcode = i_type_map[tokens[0]][0]
    if (len(tokens) != i_type_map[tokens[0]][1] + i_type_map[tokens[0]][2] + 1):#길이가 다를때
        error(f"line: {code_line}\nIncorrect number of operands for '{tokens[0]}': expected {i_type_map[tokens[0]][1] + i_type_map[tokens[0]][2]}, got {len(tokens) - 1}")
    
    R = 0
    IMM = 0
    if (i_type_map[tokens[0]][1] and i_type_map[tokens[0]][2] == 0):
        R = int(tokens[1][1:])
    elif (not i_type_map[tokens[0]][1] and i_type_map[tokens[0]][2] == 1):
        IMM = tokens[1]
    else:
        R = int(tokens[1][1:])
        IMM = tokens[2]

    if (i_type_map[tokens[0]][1] and R not in range(0, 8)):
        error(f"line: {code_line}\nInvalid register R{R}")
    

    
    if IMM.isdigit():
        IMM = int(IMM)
        if (IMM > 128 or -128 > IMM):
            error(f"line: {code_line}\nImmediate value {IMM} out of range (-128 to 128)")
        
        IMM = to_twos_complement(IMM, bits=8)
        return bin_opcode + f"{R:03b}"[::-1] + "" + f"{IMM:08b}"[::-1] + "\n"
    else:
        return bin_opcode + f"{R:03b}"[::-1] + "" + IMM + " " + str(code_line) + "\n"

r_type_map = {
    "add": ("0000000", 1, 1, 1, None),
    "sub": ("0000001", 1, 1, 1, None),
    "inc": ("0000010", 1, 1, 0, None),
    "dec": ("0000011", 1, 1, 0, None),
    "neg": ("0000100", 1, 1, 0, None),
    "mul": ("0000101", 1, 1, 1, None),
    "mulh": ("0000110", 1, 1, 1, None),
    "div": ("0000111", 1, 1, 1, None),
    "mod": ("0001000", 1, 1, 1, None),
    None: ("0001001", 0, 0, 0, None),
    "shl": ("0001010", 1, 1, 0, None),
    "shr": ("0001011", 1, 1, 0, None),
    "shl8": ("0001100", 1, 1, 0, None),
    "shr8": ("0001101", 1, 1, 0, None),
    None: ("0001110", 0, 0, 0, None),
    None: ("0001111", 0, 0, 0, None),
    "and": ("0010000", 1, 1, 1, None),
    "or": ("0010001", 1, 1, 1, None),
    "xor": ("0010010", 1, 1, 1, None),
    "nor": ("0010011", 1, 1, 1, None),
    "nand": ("0010100", 1, 1, 1, None),
    "xnor": ("0010101", 1, 1, 1, None),
    "not": ("0010110", 1, 1, 0, None),
    None: ("0010111", 0, 0, 0, None),
    None: ("0011000", 0, 0, 0, None),
    None: ("0011001", 0, 0, 0, None),
    "mov": ("0011010", 1, 1, 0, None),
    "swap": ("0011011", 1, 1, 0, None),
    "clr": ("0011100", 1, 0, 0, None),
    "pcl": ("0011101", 1, 0, 0, None),
    None: ("0011110", 0, 0, 0, None),
    None: ("0011111", 0, 0, 0, None),
    "stor": ("0100000", 1, 1, 0, None),
    "load": ("0100001", 1, 1, 0, None),
    "stors": ("0100010", 1, 1, 1, None),
    "loads": ("0100011", 1, 1, 1, None),
    "vga": ("0100100", 1, 1, 0, None),
    "psl": ("0100101", 1, 0, 0, None),
    None: ("0100110", 0, 0, 0, None),
    None: ("0100111", 0, 0, 0, None),
    None: ("0101000", 0, 0, 0, None),
    None: ("0101001", 0, 0, 0, None),
    None: ("0101010", 0, 0, 0, None),
    None: ("0101011", 0, 0, 0, None),
    None: ("0101100", 0, 0, 0, None),
    None: ("0101101", 0, 0, 0, None),
    None: ("0101110", 0, 0, 0, None),
    None: ("0101111", 0, 0, 0, None),
    "cmp": ("0110000", 1, 1, 0, None),
    "ret": ("0110001", 0, 0, 0, None),
    "push": ("0110010", 1, 0, 0, None),
    "pop": ("0110011", 1, 0, 0, None),
    "pushlr": ("0110100", 0, 0, 0, None),
    "poplr": ("0110101", 0, 0, 0, None),
    None: ("0110110", 0, 0, 0, None),
    None: ("0110111", 0, 0, 0, None),
    None: ("0111000", 0, 0, 0, None),
    None: ("0111001", 0, 0, 0, None),
    None: ("0111010", 0, 0, 0, None),
    None: ("0111011", 0, 0, 0, None),
    None: ("0111100", 0, 0, 0, None),
    None: ("0111101", 0, 0, 0, None),
    None: ("0111110", 0, 0, 0, None),
    None: ("0111111", 0, 0, 0, None),
}

i_type_map = {
    "jz": ("10000", 1, 1, jump),
    "jnz": ("10001", 1, 1, jump),
    "jmpr": ("10010", 1, 1, None),
    "jeq": ("10011", 0, 1, jump),
    "jne": ("10100", 0, 1, jump),
    "jlt": ("10101", 0, 1, jump),
    "jgt": ("10110", 0, 1, jump),
    "jle": ("10111", 0, 1, jump),
    "jge": ("11000", 0, 1, jump),
    "jmp": ("11001", 0, 1, jump),
    None: ("11010", 0, 0, None),
    "addi": ("11011", 1, 1, None),
    "subi": ("11100", 1, 1, None),
    "li": ("11101", 1, 1, None),
    "call": ("11110", 0, 1, jump),
    "callr": ("11111", 1, 1, None),
}

define_map = {
    
}

jump_map = {

}

pseudo = ("#define", "#macro", "#endmacro")
registers = ("r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7")

def ASM_converter(line):
    tokens = line.strip().lower().replace(",", "").split()
    if not tokens:
        return "void"

    for i, token in enumerate(tokens):#define 치환
        if (token in define_map):
            if (i == 0):
                return define_map[token]
            else:
                tokens[i] = define_map[token]

    if tokens[0] in r_type_map:
        if r_type_map[tokens[0]][4] != None: #특수 핸들러
            handler = r_type_map[tokens[0]][4]
            return handler(tokens)
        else: #표준 핸들러
            return standard_r(tokens)
        
    elif tokens[0] in i_type_map:
        if i_type_map[tokens[0]][3] != None: #특수 핸들러
            handler = i_type_map[tokens[0]][3]
            return handler(tokens)
        else: #표준 핸들러
            return standard_i(tokens)
    elif tokens[0][-1] == ':' and len(tokens) == 1 and not tokens[0][:-1] in define_map:
        if not is_valid_identifier(tokens[0][:-1]):
            error(f"line: {code_line}\nInvalid branch name: {tokens[0][:-1]}")
        jump_map[tokens[0][:-1]] = binary_line
        return "void"
    else:
        error(f"line: {code_line}\nUnknown instruction: {tokens[0]}")
    
# 명령줄에서 입력 파일명 받기
if len(sys.argv) < 2:
    print("사용법: python snailasm.py <input_file>")
    sys.exit(1)

input_path = sys.argv[1]
output_path = os.path.splitext(input_path)[0] + ".hex"

with open(input_path, "r", encoding="utf-8") as f_in, open(output_path, "w") as f_out:
    current_macro = False
    current_macro_keyword = ""
    define_end = False

    lines = f_in.readlines()

    lines = [line.split(';')[0].rstrip() for line in lines]#주석 분리

    for line in lines:#define, macro 분리
        if (not define_end):
            code_line += 1

        try:
            print(str(code_line) + line)
            tokens = line.strip().lower().replace(",", "").split()
            if not tokens:# 빈 줄
                continue
            
            if (tokens[0] not in ("#define", "#macro", "#endmacro", None) and not current_macro):#끝 검사
                define_end = True
                continue

            if (define_end and tokens[0] in ("#define", "#macro", "#endmacro")):
                error(f"line: {code_line}\nInvalid define position: {tokens[1]}")

            if (current_macro):#매크로 수집 진행중일때
                if (tokens[0] == "#endmacro"):
                    current_macro = False
                    current_macro_keyword = None
                else:
                    define_map[current_macro_keyword] = define_map[current_macro_keyword] +  ASM_converter(line)
                
            else:
                if (tokens[0] == "#macro"):#매크로 시작
                    if (len(tokens) != 2):
                        error(f"line: {code_line}\nIncorrect number of tokens for directive '{tokens[0]}': expected 1, got {len(tokens) - 1}.")
                    elif (not is_valid_identifier(tokens[1])):#유효한 메크로 이름이 아닐때
                        error(f"line: {code_line}\nInvalid macro name: {tokens[1]}")
                    elif (tokens[1] in define_map):
                        error(f"line: {code_line}\nAlready defined: {tokens[1]}")
                    else:
                        current_macro = True
                        current_macro_keyword = tokens[1]
                        define_map[current_macro_keyword] = ""
                elif (tokens[0] == "#define"):
                    if (len(tokens) != 3):
                        error(f"line: {code_line}\nIncorrect number of tokens for directive '{tokens[0]}': expected 2, got {len(tokens) - 1}.")
                    elif (not is_valid_identifier(tokens[1])):#유효한 define 이름이 아닐때
                        error(f"line: {code_line}\nInvalid define name: {tokens[1]}")
                    elif (tokens[2] not in registers and not tokens[2].isdigit()): #유효한 define 값이 아닐때
                        error(f"line: {code_line}\nInvalid define value: {tokens[2]}. Register names must be between r0 and r7 or a defined symbol.")
                    elif (tokens[1] in define_map):
                        error(f"line: {code_line}\nAlready defined: {tokens[1]}")
                    else:
                        define_map[tokens[1]] = tokens[2]
                else:
                    error(f"line: {code_line}\nUnknown directive: {tokens[0]}")
        except SystemExit:
            raise
        except:
            error(f"line : {code_line}\nSnailASM encountered an unexpected issue during compilation.")
    
    if (current_macro):
        error(f"line : {code_line}\nSnailASM encountered an unexpected issue during compilation.")

    print(define_map)

    for line in lines[code_line - 1:]:#명령어 변환
        result = ASM_converter(line)
        
        if result != "void":
            binary_line += result.count("\n")
            binary_list.append(result)
        code_line += 1

    for i, line in enumerate(binary_list):#분기 명령어 주소 삽입
        lines = line[8:].strip().split()
        if len(lines) == 2:
            if not lines[0] in jump_map:
                error(f"line: {lines[1]}\nUndefined define: '{lines[0]}'")
            relative = jump_map[lines[0]] - i
            if (relative > 127 or relative < -128):
                error(f"line: {lines[1]}\nBranch target '{lines[0]}' is too far: offset {relative} is out of range (-128 to 127).")
            twos_complement = to_twos_complement(relative)
            f_out.write(line[:8] + f"{twos_complement:08b}"[::-1] + "\n")
        else:
            f_out.write(line)
            

end = time.perf_counter()
elapsed_ms = (end - start) * 1000

print(f"Compilation complete. ({elapsed_ms:.2f} ms)")