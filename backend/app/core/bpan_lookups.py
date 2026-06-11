"""
BPAN Lookup Tables - Official Indian Battery Pack Aadhaar System
Reference: Battery Pack Aadhaar System Guidelines
"""

from enum import Enum

# Country Codes (Table 16 Subset)
COUNTRY_CODES = {
    "MY": "India", "MZ": "India",
    "J": "Japan", "L": "China (Mainland)", "KL": "Korea (South)",
    "PS": "Bangladesh", "NS": "Uzbekistan",
    "X": "Russia", "W": "Germany",
}

# Manufacturer Identifiers (Table 17)
MANUFACTURER_CODES = {f"{i:03d}": f"Company {i}" for i in range(1, 21)}
MANUFACTURER_CODES["008"] = "Company 8"
MANUFACTURER_CODES["009"] = "Hykon India Limited"

# Battery Chemistry (Table 18)
CHEMISTRY_CODES = {
    "A": "Lead Acid",
    "B": "Nickel-Cadmium (Ni-Cd)",
    "C": "Nickel-Metal Hydride (Ni-MH)",
    "D": "Sodium-Ion",
    "E": "LFP",
    "F": "NMC"
}

# Extinguisher Class (Table 19)
EXTINGUISHER_CLASSES = {
    "A": "Class A", "B": "Class B", "C": "Class C",
    "D": "Class D", "E": "Class K"
}

# Manufacturing Year (Table 20) - Base year 2025
YEAR_CODES = {
    "1": 2025, "2": 2026, "3": 2027, "4": 2028, "5": 2029, "6": 2030,
    "7": 2031, "8": 2032, "9": 2033, "A": 2034, "B": 2035, "C": 2036,
    "D": 2037, "E": 2038, "F": 2039, "G": 2040, "H": 2041, "J": 2042,
    "K": 2043, "L": 2044, "M": 2045, "N": 2046, "P": 2047, "Q": 2048, "R": 2049,
    "S": 2050, "T": 2051, "U": 2052, "V": 2053, "W": 2054,
    "X": 2055, "Y": 2056, "Z": 2057
}

# Manufacturing Month (Table 21)
MONTH_CODES = {
    "A": "January", "B": "February", "C": "March", "D": "April",
    "E": "May", "F": "June", "G": "July", "H": "August",
    "J": "September", "K": "October", "L": "November", "M": "December"
}

# Manufacturing Date (Table 22)
DATE_CODES = {
    "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
    "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15, "G": 16, "H": 17,
    "J": 18, "K": 19, "L": 20, "M": 21, "N": 22, "P": 23, "Q": 24, "R": 25,
    "S": 26, "T": 27, "U": 28, "V": 29, "W": 30, "X": 31
}

# Factory Codes (Table 23)
FACTORY_CODES = {}
for i in range(1, 10):
    FACTORY_CODES[str(i)] = f"Factory {i}"
valid_factory_letters = [l for l in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if l not in ("I", "O")]
for i, letter in enumerate(valid_factory_letters):
    FACTORY_CODES[letter] = f"Factory {10 + i}"

# Battery Warranty (Table 24)
WARRANTY_CODES = {}
valid_warranty_letters = [l for l in "ABCDEFGHIJKLMNOPQRSTUV" if l not in ("I", "O")]
for i, letter in enumerate(valid_warranty_letters):
    WARRANTY_CODES[letter] = i + 1

# Cell Type (Table 25)
CELL_TYPE_CODES = {
    "A": "Cylindrical", "B": "Prismatic", "C": "Pouch", "D": "Blade"
}

# Construction Type (Table 27)
PACK_CONSTRUCTION_CODES = {
    "A": "Cell-to-Module-to-Pack (CTMTP)",
    "B": "Cell-to-Pack (CTP)"
}
MODULE_CONSTRUCTION_CODES = {
    "A": "Series",
    "B": "Parallel"
}

# Cooling System (Table 28)
COOLING_SYSTEM_CODES = {
    "A": "Air", "B": "Liquid"
}

# Disassembly Method (Table 29)
DISASSEMBLY_METHODS = {
    "AA": "Standard Manual Disassembly & Full Separation",
    "AB": "Direct Shredding Pre-Treatment",
    "AC": "Repurposing/Second-Life Pathway",
    "AD": "Emergency / Damaged Pack Procedure",
    "AE": "Module-Level Input Disassembly",
    "AF": "AI-Guided SoH Triage",
    "AG": "Electrolyte Extraction & Neutralization",
    "AH": "Robotic Automated Disassembly",
    "AJ": "Cryogenic / Inert-Atmosphere Disassembly",
    "AK": "Direct Cathode Refunctionalization",
    "AL": "Biometallurgical Recycling"
}

# Circularity Method (Table 30)
CIRCULARITY_METHODS = {
    "A": "Material Circularity Indicator (MCI)",
    "B": "Carbon Footprint (PEF Method)",
    "C": "Recycled Content & Recovery Metrics",
    "D": "Design for Circularity Score",
    "E": "Second-Life Utilization Index",
    "F": "Water / Resource Footprint Analysis",
    "G": "Full Life Cycle Assessment (LCA)",
    "H": "PyroMetallurgical Recovery"
}

# Material Enums (Tables 32-38)
ANODE_MATERIALS = {"A": "Graphite", "B": "Silicon", "C": "LTO"}
CATHODE_MATERIALS = {"A": "LFP", "B": "LiCoO2", "C": "LMO", "D": "NMC", "E": "NCA", "F": "LMFP"}
ELECTROLYTE_MATERIALS = {"A": "LiPF6", "B": "LiBF4", "C": "LiClO4", "D": "Solid State Electrolyte"}
SEPARATOR_MATERIALS = {"A": "PE", "B": "PP", "C": "PE/PP Blend", "D": "Glass Fiber", "E": "Ceramic-Coated", "F": "PVDF", "G": "Ion-Exchange"}
CURRENT_COLLECTOR_MATERIALS = {"A": "Aluminium", "B": "Nickel", "C": "Stainless Steel", "D": "Al-Cu Alloy", "E": "Copper"}
CASING_MATERIALS = {"A": "Aluminium", "B": "Steel", "C": "Extruded Al", "D": "Die-Cast Al", "E": "Glass Fiber Comp", "F": "SMC Comp", "G": "Carbon Fibre Comp", "H": "Thermoplastics"}
POTTING_MATERIALS = {"A": "Epoxy Resins", "B": "PU", "C": "Silicone resins", "D": "Acrylics"}

# Material Elements (Table 39)
MATERIAL_ELEMENTS = {
    "Li": "Lithium", "Cb": "Cobalt", "Ni": "Nickel", "Gr": "Graphite",
    "Co": "Copper", "An": "Antimony/Phosphorus", "Ar": "Arsenic",
    "Ba": "Bauxite/Alumina", "Mn": "Manganese", "Ti": "Titanium",
    "Al": "Aluminium", "Fe": "Iron", "Sn": "Tin", "Si": "Silicon"
}

# Carbon Footprint Stages (Table 42)
CARBON_STAGES = {
    "A": "Raw material acquisition stage",
    "B": "Manufacturing stage",
    "C": "Distribution stage",
    "D": "End of Life and Recycling stage"
}

# Server Category (Table 43)
BATTERY_CATEGORIES = {
    "A": "EV L-cat",
    "B": "EV M/N-cat",
    "C": "Industrial >2kWh"
}

# Server Status (Table 44)
BATTERY_STATUS_CODES = {
    "A": "Operational (>80%)",
    "B": "Second Life (60-80%)",
    "C": "End of Life (<60%)"
}

