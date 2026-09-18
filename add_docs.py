import os
import json

# Create data directory
os.makedirs("data/documents", exist_ok=True)
os.makedirs("data/processed", exist_ok=True)

# Constitutional documents with real content
constitutions = {
    "constitution_india.txt": r"""
CONSTITUTION OF INDIA
(Unofficial educational excerpt)

PREAMBLE
WE, THE PEOPLE OF INDIA, having solemnly resolved to constitute India into a 
SOVEREIGN SOCIALIST SECULAR DEMOCRATIC REPUBLIC and to secure to all its citizens:
JUSTICE, social, economic and political;
LIBERTY of thought, expression, belief, faith and worship;
EQUALITY of status and of opportunity;
and to promote among them all FRATERNITY assuring the dignity of the individual 
and the unity and integrity of the Nation.

PART III: FUNDAMENTAL RIGHTS

Article 12: Definition — The State includes Government and Parliament of India.
Article 13: Laws inconsistent with or in derogation of the fundamental rights shall be void.

Article 14: Equality before law — The State shall not deny to any person equality 
before the law or the equal protection of the laws within the territory of India.

Article 15: Prohibition of discrimination — The State shall not discriminate against 
any citizen on grounds only of religion, race, caste, sex, place of birth or any of them.

Article 19: Protection of certain rights regarding freedom of speech —
(1) All citizens shall have the right:
(a) to freedom of speech and expression;
(b) to assemble peaceably and without arms;
(c) to form associations or unions;
(d) to move freely throughout the territory of India;
(e) to reside and settle in any part of the territory of India;
(f) to practice any profession, or to carry on any occupation, trade or business.

Article 21: Protection of life and personal liberty — No person shall be deprived 
of his life or personal liberty except according to procedure established by law.

