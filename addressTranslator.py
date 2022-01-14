class AddressSectionMapper:
    def __init__(self, sections):
        self.sections = sections

    @staticmethod
    def sectionContainsAddress(section, address) -> bool:
        if section["off_beg"] <= address and address <= section["off_end"]:
            return True
        return False
    
    def map(self, address):
        for section in self.sections:
            if AddressSectionMapper.sectionContainsAddress(section, address):
                return address - section["delta"]
        return None
    
    def inverseMap(self, address):
        for section in self.sections:
            mappedAddress = address + section["delta"]
            if AddressSectionMapper.sectionContainsAddress(section, mappedAddress):
                return mappedAddress
        return None

# Fortune Street Virtual to Fortune Street File
fsvirt_to_fsfile = AddressSectionMapper([
{"off_beg": 0x80004000, "off_end": 0x80006720, "delta": 0x80003f00},
{"off_beg": 0x80006720, "off_end": 0x80006c80, "delta": 0x7fbfda40},
{"off_beg": 0x80006c80, "off_end": 0x80007480, "delta": 0x7fbfda40},
{"off_beg": 0x80007480, "off_end": 0x8040d940, "delta": 0x80004c60},
{"off_beg": 0x8040d940, "off_end": 0x8040de80, "delta": 0x80003f00},
{"off_beg": 0x8040de80, "off_end": 0x8040dea0, "delta": 0x80003f00},
{"off_beg": 0x8040dec0, "off_end": 0x8044ea60, "delta": 0x80003f20},
{"off_beg": 0x8044ea60, "off_end": 0x804ac680, "delta": 0x80003f20},
{"off_beg": 0x80814a80, "off_end": 0x808171c0, "delta": 0x8036c320},
{"off_beg": 0x80818da0, "off_end": 0x8081ede0, "delta": 0x8036df00}
])

# Boom Street Virtual to Boom Street File
bsvirt_to_bsfile = AddressSectionMapper([
{"off_beg": 0x80004000, "off_end": 0x80006720, "delta": 0x80003f00},
{"off_beg": 0x80006720, "off_end": 0x80006c80, "delta": 0x7fbfda00},
{"off_beg": 0x80006c80, "off_end": 0x80007480, "delta": 0x7fbfda00},
{"off_beg": 0x80007480, "off_end": 0x8040d980, "delta": 0x80004c60},
{"off_beg": 0x8040d980, "off_end": 0x8040dec0, "delta": 0x80003f00},
{"off_beg": 0x8040dec0, "off_end": 0x8040dee0, "delta": 0x80003f00},
{"off_beg": 0x8040df00, "off_end": 0x8044ec00, "delta": 0x80003f20},
{"off_beg": 0x8044ec00, "off_end": 0x804ac820, "delta": 0x80003f20},
{"off_beg": 0x80814c80, "off_end": 0x808173c0, "delta": 0x8036c380},
{"off_beg": 0x80818fa0, "off_end": 0x8081efe0, "delta": 0x8036df60}
])

# Boom Street Virtual to Fortune Street Virtual
bsvirt_to_fsvirt = AddressSectionMapper([
{"off_beg": 0x80000100, "off_end": 0x8007a283, "delta":   0x0},
{"off_beg": 0x8007a2f4, "off_end": 0x80268717, "delta":  0x54},
{"off_beg": 0x80268720, "off_end": 0x8040d97b, "delta":  0x50},
{"off_beg": 0x8040d980, "off_end": 0x8041027f, "delta":  0x40},
{"off_beg": 0x804105f0, "off_end": 0x8044ebe7, "delta": 0x188},
{"off_beg": 0x8044ec00, "off_end": 0x804ac804, "delta": 0x1A0},
{"off_beg": 0x804ac880, "off_end": 0x8081f013, "delta": 0x200}
])