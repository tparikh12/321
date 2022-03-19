import sys

# print(sys.byteorder)

filename = sys.argv[1]
# filename = 'code1.legv8asm.machine'

opcodes = {
    "ADD":    "10001011000",
    "ADDI":   "1001000100",
    "ADDIS":  "1011000100",
    "ADDS":   "10101011000",
    "AND":    "10001010000",
    "ANDI":   "1001001000",
    "ANDIS":  "1111001000",
    "ANDS":   "1110101000",
    "B":      "000101",
    "B.cond": "01010100",
    "BL":     "100101",
    "BR":     "11010110000",
    "CBNZ":   "10110101",
    "CBZ":    "10110100",
    "DUMP":   "11111111110",
    "EOR":    "11001010000",
    "EORI":   "1101001000",
    "FADDD":  "00011110011",
    "FADDS":  "00011110001",
    "FCMPD":  "00011110011",
    "FCMPS":  "00011110001",
    "FDIVD":  "00011110011",
    "FDIVS":  "00011110001",
    "FMULD":  "00011110011",
    "FMULS":  "00011110001",
    "FSUBD":  "00011110011",
    "FSUBS":  "00011110001",
    "HALT":   "11111111111",
    "LDUR":   "11111000010",
    "LDURB":  "00111000010",
    "LDURD":  "11111100010",
    "LDURH":  "01111000010",
    "LDURS":  "10111100010",
    "LDURSW": "10111000100",
    "LSL":    "11010011011",
    "LSR":    "11010011010",
    "MUL":    "10011011000",
    "ORR":    "10101010000",
    "ORRI":   "1011001000",
    "PRNL":   "11111111100",
    "PRNT":   "11111111101",
    "SDIV":   "10011010110",
    "SMULH":  "10011011010",
    "STUR":   "11111000000",
    "STURB":  "00111000000",
    "STURD":  "11111100000",
    "STURH":  "01111000000",
    "STURS":  "10111100000",
    "STURSW": "10111000000",
    "SUB":    "11001011000",
    "SUBI":   "1101000100",
    "SUBIS":  "1111000100",
    "SUBS":   "11101011000",
    "UDIV":   "10011010110",
    "UMULH":  "10011011110"
}

Bcond = {
    0: "EQ",
    1: "NE",
    2: "HS",
    3: "LO",
    4: "MI",
    5: "PL",
    6: "VS",
    7: "VC",
    8: "HI",
    9: "LS",
    10: "GE",
    11: "LT",
    12: "GT",
    13: "LE"
}

no_labels = 0
label_dic = {}


def getNumber(num: str, isRegister: bool = False):
    if isRegister or num[0] == "0":
        num = int(num, 2)
        if isRegister and num == 31:
            return "ZR"
    else:
        # convert 2's complement
        num2 = ""
        flip = False
        for i in range(len(num) - 1, -1, -1):
            if flip:
                if num[i] == "0": 
                    num2 = "1" + num2
                else: 
                    num2 = "0" + num2
            else:
                if num[i] == "1": 
                    num2 = "1" + num2
                else: 
                    num2 = "0" + num2
            if num[i] == "1": 
                flip = True
        num = -int(num2, 2)
        # num = -int("1".ljust(32, "1"), 2) + num2
    return num


def decodeRInstructions(line):
    Rm = getNumber(line[11:16], True)
    shamt = getNumber(line[16:22])
    Rn = getNumber(line[22:27], True)
    Rd = getNumber(line[27:32], True)

    return Rm, shamt, Rn, Rd


def decodeIInstructions(line):
    I = getNumber(line[10:22])
    Rn = getNumber(line[22:27], True)
    Rd = getNumber(line[27:32], True)

    return I, Rn, Rd


def decodeDInstructions(line):
    dtAddr = getNumber(line[11:20])
    Rn = getNumber(line[22:27], True)
    Rt = getNumber(line[27:32], True)

    return dtAddr, Rn, Rt


def decodeCBInstructions(line):
    addr = getNumber(line[8:27])
    Rt = getNumber(line[27:32], True)

    return addr, Rt


def decodeBInstructions(line):
    # print(line[6:32])
    addr = getNumber(line[6:32])
    # print(addr)

    return addr


def decodeGeneralRInstruction(instruction: str, line: str):
    Rm, _, Rn, Rd = decodeRInstructions(line)
    return f'{instruction} X{Rd},X{Rn},X{Rm}'


def decodeShiftInstruction(instruction: str, line: str):
    _, shamt, Rn, Rd = decodeRInstructions(line)
    return f'{instruction} X{Rd},X{Rn},#{shamt}'


def decodeGeneralIInstruction(instruction: str, line: str):
    I, Rn, Rd = decodeIInstructions(line)
    return f'{instruction} X{Rd},X{Rn},#{I}'


def addLabel(line_no: int):
    global no_labels
    global label_dic

    no_labels += 1

    if line_no not in label_dic:
        label_dic[line_no] = []

    label_dic[line_no].append('label' + str(no_labels))


def decodeGeneralCBInstruction(instruction: str, line: str, line_no: int):
    addr, Rt = decodeCBInstructions(line)
    addLabel(line_no + addr)
    return f'{instruction} X{Rt},label{no_labels}'


def decodeGeneralBInstruction(instruction: str, line: str, line_no: int):
    addr = decodeBInstructions(line)
    addLabel(line_no + addr)
    return f'{instruction} label{no_labels}'


def decodeBCondInstruction(line: str, line_no: int):
    addr, Rt = decodeCBInstructions(line)
    addLabel(line_no + addr)
    return f'B.{Bcond[Rt]} label{no_labels}'


def decode(line: str, line_no: int):
    if line.startswith(opcodes["ADD"]):
        return decodeGeneralRInstruction("ADD", line)
    elif line.startswith(opcodes["ADDI"]):
        return decodeGeneralIInstruction("ADDI", line)

    elif line.startswith(opcodes["AND"]):
        return decodeGeneralRInstruction("AND", line)
    elif line.startswith(opcodes["ANDI"]):
        return decodeGeneralIInstruction("ANDI", line)

    elif line.startswith(opcodes["B.cond"]):
        return decodeBCondInstruction(line, line_no)
    elif line.startswith(opcodes["B"]):
        return decodeGeneralBInstruction("B", line, line_no)

    elif line.startswith(opcodes["BL"]):
        return decodeGeneralBInstruction("BL", line, line_no)

    elif line.startswith(opcodes["BR"]):
        _, _, Rn, _ = decodeRInstructions(line)
        return f'BR X{Rn}'

    elif line.startswith(opcodes["CBNZ"]):
        return decodeGeneralCBInstruction("CBNZ", line, line_no)
    elif line.startswith(opcodes["CBZ"]):
        return decodeGeneralCBInstruction("CBZ", line, line_no)

    elif line.startswith(opcodes["EOR"]):
        return decodeGeneralRInstruction("EOR", line)
    elif line.startswith(opcodes["EORI"]):
        return decodeGeneralIInstruction("EORI", line)

    elif line.startswith(opcodes["LDUR"]):
        dtAddr, Rn, Rt = decodeDInstructions(line)
        return f'LDUR X{Rt},[X{Rn},#{dtAddr}]'

    elif line.startswith(opcodes["LSL"]):
        return decodeShiftInstruction("LSL", line)
    elif line.startswith(opcodes["LSR"]):
        return decodeShiftInstruction("LSR", line)

    elif line.startswith(opcodes["ORR"]):
        return decodeGeneralRInstruction("ORR", line)
    elif line.startswith(opcodes["ORRI"]):
        return decodeGeneralIInstruction("ORRI", line)

    elif line.startswith(opcodes["STUR"]):
        dtAddr, Rn, Rt = decodeDInstructions(line)
        return f'STUR X{Rt},[X{Rn},#{dtAddr}]'

    elif line.startswith(opcodes["SUB"]):
        return decodeGeneralRInstruction("SUB", line)
    elif line.startswith(opcodes["SUBI"]):
        return decodeGeneralIInstruction("SUBI", line)
    elif line.startswith(opcodes["SUBS"]):
        return decodeGeneralRInstruction("SUBS", line)
    elif line.startswith(opcodes["SUBIS"]):
        return decodeGeneralIInstruction("SUBIS", line)

    elif line.startswith(opcodes["MUL"]):
        return decodeGeneralRInstruction("MUL", line)

    elif line.startswith(opcodes["PRNT"]):
        _, _, _, Rd = decodeRInstructions(line)
        return f'PRNT X{Rd}'
    elif line.startswith(opcodes["PRNL"]):
        return "PRNL"
    elif line.startswith(opcodes["DUMP"]):
        return "DUMP"
    elif line.startswith(opcodes["HALT"]):
        return "HALT"
    # else:
    #     print(line)


with open(file=filename, mode='rb') as file:
    line = ""
    lines = []
    byte = 1
    i = 0
    while byte != b'':
        byte = file.read(1)
        line += (bin(int.from_bytes(byte, "big"))[2:]).rjust(8, '0')
        i += 1
        if i % 4 == 0:
            lines.append(line)
            line = ""
# print(lines)

line_no = 0
output_lines = []
for line in lines:
    line_no += 1
    line = line.strip()
    if(len(line) == 0):
        continue
    output_lines.append(decode(line, line_no))
    # if sys.byteorder.lower() == 'little':
    #     byteArray.reverse()

    # print(''.join(byteArray))

output = ''
for i in range(len(output_lines) + 2):
    line_no = i + 1
    if line_no in label_dic:
        if len(label_dic[line_no]) > 1:
            no_labels += 1
            label_dic[line_no].insert(0, f'label{no_labels}')
        output += label_dic[line_no][0] + ":\n"
    if i < len(output_lines):
        output += output_lines[i] + "\n"

# Replace duplicate labels
for key in label_dic:
    if len(label_dic[key]) > 1:
        new_label = label_dic[key][0]
        for label in label_dic[key][1:]:
            output = output.replace(label, new_label)

print(output)
