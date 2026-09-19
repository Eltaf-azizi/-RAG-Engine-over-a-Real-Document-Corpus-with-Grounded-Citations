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

PART V: THE UNION

Article 52: The President of India — There shall be a President of India.
Article 53: Executive power of the Union — The executive power of the Union shall be 
vested in the President and shall be exercised by him either directly or through 
officers subordinate to him.
Article 54: Election of President — The President shall be elected by the members 
of an electoral college consisting of the elected members of both Houses of Parliament 
and the elected members of the Legislative Assemblies of the States.
Article 79: Constitution of Parliament — There shall be a Parliament for the Union 
consisting of the President and two Houses: Council of States and House of the People.
Article 80: Composition of the Council of States — The Council of States shall consist 
of twelve members nominated by the President and representatives of the States.

PART XVIII: EMERGENCY PROVISIONS

Article 352: Proclamation of Emergency — If the President is satisfied that a grave 
emergency exists whereby the security of India is threatened by war, external aggression 
or armed rebellion, he may declare a Proclamation of Emergency.

PART XX: AMENDMENT OF THE CONSTITUTION

Article 368: Power of Parliament to amend the Constitution — Parliament may amend any 
provision of this Constitution by way of addition, variation or repeal in accordance 
with the procedure laid down.
""",
    
    "constitution_usa.txt": r"""
CONSTITUTION OF THE UNITED STATES OF AMERICA
(Official text excerpt)

PREAMBLE
We the People of the United States, in Order to form a more perfect Union, establish 
Justice, insure domestic Tranquility, provide for the common defence, promote the 
general Welfare, and secure the Blessings of Liberty to ourselves and our Posterity, 
do ordain and establish this Constitution for the United States of America.

ARTICLE I: LEGISLATIVE BRANCH

Section 1: All legislative Powers herein granted shall be vested in a Congress of the 
United States, which shall consist of a Senate and House of Representatives.

Section 2: The House of Representatives shall be composed of Members chosen every 
second Year by the People of the several States. No Person shall be a Representative 
who shall not have attained to the Age of twenty five Years.

Section 3: The Senate of the United States shall be composed of two Senators from 
each State, chosen by the Legislature thereof, for six Years; and each Senator shall 
have one Vote.

ARTICLE II: EXECUTIVE BRANCH

Section 1: The executive Power shall be vested in a President of the United States of 
America. He shall hold his Office during the Term of four Years. No Person except a 
natural born Citizen shall be eligible to the Office of President.

Section 2: The President shall be Commander in Chief of the Army and Navy of the 
United States. He shall have Power to grant Reprieves and Pardons for Offences against 
the United States.

Section 4: The President, Vice President and all civil Officers of the United States, 
shall be removed from Office on Impeachment for, and Conviction of, Treason, Bribery, 
or other high Crimes and Misdemeanors.

ARTICLE III: JUDICIAL BRANCH

Section 1: The judicial Power of the United States shall be vested in one supreme Court, 
and in such inferior Courts as the Congress may ordain and establish.

ARTICLE V: AMENDMENT PROCESS

The Congress, whenever two thirds of both Houses shall deem it necessary, shall propose 
Amendments to this Constitution, which shall be valid when ratified by the Legislatures 
of three fourths of the several States.

AMENDMENT I: Congress shall make no law respecting an establishment of religion, or 
prohibiting the free exercise thereof; or abridging the freedom of speech, or of the 
press; or the right of the people peaceably to assemble, and to petition the Government 
for a redress of grievances.

AMENDMENT II: A well regulated Militia, being necessary to the security of a free 
State, the right of the people to keep and bear Arms, shall not be infringed.

AMENDMENT V: No person shall be deprived of life, liberty, or property, without due 
process of law; nor shall private property be taken for public use, without just 
compensation.
""",
    
    "constitution_france.txt": r"""
CONSTITUTION OF FRANCE
(Constitution of October 4, 1958 - Fifth Republic)

PREAMBLE
The French people solemnly proclaim their attachment to the Rights of Man and the 
principles of national sovereignty as defined by the Declaration of 1789, confirmed 
and complemented by the Preamble to the Constitution of 1946.

TITLE I: ON SOVEREIGNTY

Article 1: France shall be an indivisible, secular, democratic and social Republic. 
It shall ensure the equality of all citizens before the law, without distinction of 
origin, race or religion.

TITLE II: THE PRESIDENT OF THE REPUBLIC


CHAPTER 1: FOUNDING PROVISIONS

Section 1: The Republic of South Africa is one, sovereign, democratic state founded 
on the following values: Human dignity, the achievement of equality and the advancement 
of human rights and freedoms.

CHAPTER 2: BILL OF RIGHTS

Section 7: This Bill of Rights is a cornerstone of democracy in South Africa. It 
enshrines the rights of all people in our country.

Section 9: Everyone is equal before the law and has the right to equal protection 
and benefit of the law. The state may not unfairly discriminate on grounds including 
race, gender, sex, religion, or language.

Section 10: Everyone has inherent dignity and the right to have their dignity respected 
and protected.

Section 11: Everyone has the right to life.

Section 16: Everyone has the right to freedom of expression, which includes freedom 
of the press and other media, freedom to receive or impart information or ideas.

CHAPTER 5: THE PRESIDENT AND NATIONAL EXECUTIVE

Section 83: The President is the Head of State and head of the national executive.
Section 86: At its first sitting after its election, the National Assembly must elect 
a woman or a man from among its members to be the President.

CHAPTER 8: COURTS AND ADMINISTRATION OF JUSTICE

Section 165: The judicial authority of the Republic is vested in the courts. The courts 
are independent and subject only to the Constitution and the law.

Section 167: The Constitutional Court consists of the Chief Justice of South Africa, 
the Deputy Chief Justice and nine other judges.

EMERGENCY PROVISIONS

Section 37: A state of emergency may be declared only by an Act of Parliament, and only 
when the life of the nation is threatened by war, invasion, general insurrection, 
disorder, natural disaster or other public emergency.

AMENDMENT PROCEDURE

Section 74: Any bill amending the Constitution must be passed by the National Assembly 
with a supporting vote of at least two thirds of its members.
"""
}

# Write all documents
print("=" * 60)
print("CREATING CONSTITUTIONAL DOCUMENTS")
print("=" * 60)

for filename, content in constitutions.items():
    filepath = os.path.join("data/documents", filename)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content.strip())
    size = os.path.getsize(filepath)
    print(f"✓ {filename} ({size:,} bytes)")

print(f"\n{len(constitutions)} documents created successfully.")
print("Location: data/documents/")
print("\nNext step: python src/ingest.py")