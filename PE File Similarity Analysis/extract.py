import pefile
from capstone import *


def get_opcodes(data, address):
    md = Cs(CS_ARCH_X86, CS_MODE_32)
    opcodes = []
    for instr in md.disasm(data, address):
        if instr.mnemonic not in ["nop", "int3"]:
            if instr.mnemonic in ["add", "sub", 'inc']:
                opcodes.append("add")
            else:
                opcodes.append(instr.mnemonic)
    return opcodes


def get_ngrams(executable_path):
    try:
        pe = pefile.PE(executable_path)
    except Exception as e:
        print(f"Error: {e}")
        return None

    list_of_opcodes = []
    for section in pe.sections:
        if section.Characteristics & 0x20000000:
            list_of_opcodes.append(get_opcodes(section.get_data(), section.VirtualAddress))

    ngrams = []
    for opcodes in list_of_opcodes:
        length = len(opcodes)
        if length >= 5:
            for i in range(length - 4):
                ngrams.append(opcodes[i] + ";" + opcodes[i + 1] + ";" + opcodes[i + 2] + ";" + opcodes[i + 3] + ";" +
                              opcodes[i + 4])

    return set(ngrams)


def extract_executable_info(executable_path):
    try:
        pe = pefile.PE(executable_path)

        machine_architecture = pe.FILE_HEADER.Machine
        platform = "x86" if machine_architecture == 0x14c else "x64" if machine_architecture == 0x8664 else "Unknown"

        num_sections = len(pe.sections)

        num_executable_sections = 0

        for section in pe.sections:
            if section.Characteristics & 0x20000000:
                num_executable_sections += 1

        entry_point_rva = pe.OPTIONAL_HEADER.AddressOfEntryPoint
        entry_point_section_number = None
        section_start = None
        section_size = None

        number = 1
        for section in pe.sections:
            if section.contains_rva(entry_point_rva):
                entry_point_section_number = number
                section_start = section.VirtualAddress
                section_size = section.Misc_VirtualSize
                break
            number += 1

        entry_point_pos = (entry_point_rva - section_start) / section_size

        executable_info = {
            'Platform': platform,
            'Number of sections': num_sections,
            'Number of executable sections': num_executable_sections,
            'Entry point section number': entry_point_section_number,
            'Entry point position': entry_point_pos
        }

        return executable_info

    except Exception as e:
        print(f"Error: {e}")
        return None


def jaccard_similarity(set1, set2):
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))
    # print(str(len(set1)) + " " + str(len(set2)) + " " + str(intersection) + " " + str(union))
    return intersection / union if union else 0


if __name__ == "__main__":
    while True:
        command = input("Enter \"compare\" or \"extract\": ")
        if command == "compare":
            file_path1 = input("Enter first path: ")
            file_path2 = input("Enter second path: ")
            ngrams1 = get_ngrams(file_path1)
            ngrams2 = get_ngrams(file_path2)
            print("Jaccard similarity between the two files: ", jaccard_similarity(ngrams1, ngrams2))

        elif command == "extract":
            file_path = input("Enter file path: ")
            info = extract_executable_info(file_path)
            if info:
                print("Executable information:")
                for key, value in info.items():
                    print(f"{key}: {value}")
            else:
                print("Couldn't get executable info.")

        print("\n")
