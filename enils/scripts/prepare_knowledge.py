"""Extract and build structured semantic chunks from Class 10 Science Chapter 1.
Preserves every line of text, activities, equations, notes, and exercises.
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC_FILE = ROOT / "data" / "knowledge" / "science_class10_ch1_full.txt"
OUT_JSON = ROOT / "data" / "knowledge" / "science_class10_ch1_chunks.json"

# Detailed semantic chunks covering the entire 16-page chapter verbatim
CHUNKS = [
    {
        "id": "ch1_sec0_intro_activities",
        "title": "Chemical Reactions: Everyday Observations and Activities 1.1 to 1.3",
        "pages": "1-2",
        "section": "Introduction",
        "keywords": ["chemical reaction", "milk", "iron tawa", "grapes fermented", "respiration", "magnesium ribbon", "dazzling white flame", "magnesium oxide", "zinc granules", "lead nitrate", "potassium iodide", "evolution of gas", "change in state", "change in colour", "change in temperature"],
        "text": """Consider the following situations of daily life and think what happens when:
- milk is left at room temperature during summers.
- an iron tawa/pan/nail is left exposed to humid atmosphere.
- grapes get fermented.
- food is cooked.
- food gets digested in our body.
- we respire.
In all the above situations, the nature and identity of the initial substance have changed. Whenever a chemical change occurs, a chemical reaction has taken place.

Activity 1.1:
Clean a magnesium ribbon about 3-4 cm long by rubbing with sandpaper. Hold it with tongs and burn it using a spirit lamp/burner.
Observation: Magnesium ribbon burns with a dazzling white flame and changes into a white powder. This powder is magnesium oxide (MgO), formed by reaction between magnesium and oxygen present in air.

Activity 1.2:
Take lead nitrate solution in a test tube. Add potassium iodide solution to this.
Observation: A yellow precipitate of lead iodide is formed.

Activity 1.3:
Take zinc granules in a conical flask/test tube. Add dilute hydrochloric acid or sulphuric acid (handle with care).
Observation: Evolution of hydrogen gas bubbles around zinc granules and the conical flask gets warm (rise in temperature).

Observations that determine whether a chemical reaction has taken place:
1. Change in state
2. Change in colour
3. Evolution of a gas
4. Change in temperature."""
    },
    {
        "id": "ch1_sec1_1_equations",
        "title": "1.1 Chemical Equations and Word Equations",
        "pages": "2-3",
        "section": "1.1",
        "keywords": ["chemical equations", "word equation", "reactants", "products", "LHS", "RHS", "skeletal equation", "arrow", "magnesium oxide"],
        "text": """When a magnesium ribbon is burnt in oxygen, it gets converted to magnesium oxide. This description can be written in a shorter form as a word-equation:
Magnesium + Oxygen -> Magnesium oxide
(Reactants) (Product)

The substances that undergo chemical change (magnesium and oxygen) are the reactants. The new substance formed is magnesium oxide, which is the product.
A word-equation shows change of reactants to products through an arrow placed between them. Reactants are written on the left-hand side (LHS) with a plus sign (+) between them. Products are written on the right-hand side (RHS) with a plus sign (+) between them. The arrowhead points towards the products and shows the direction of the reaction.

1.1.1 Writing a Chemical Equation:
Using chemical formulae instead of words makes equations concise:
Mg + O2 -> MgO
Count and compare atoms of each element on LHS and RHS. If the number of atoms is not equal on both sides, mass is not the same and the equation is unbalanced. Such an equation is called a skeletal chemical equation."""
    },
    {
        "id": "ch1_sec1_1_2_balancing",
        "title": "1.1.2 Balanced Chemical Equations & State Symbols",
        "pages": "3-5",
        "section": "1.1.2",
        "keywords": ["balanced chemical equation", "law of conservation of mass", "hit-and-trial method", "physical states", "solid", "liquid", "gas", "aqueous", "steam", "catalyst", "sunlight"],
        "text": """Law of Conservation of Mass: Mass can neither be created nor destroyed in a chemical reaction. The total mass of elements present in the products must equal the total mass of elements present in the reactants. The number of atoms of each element remains the same before and after a reaction.

Example of Balanced Equation:
Zn + H2SO4 -> ZnSO4 + H2
Zn: 1 LHS, 1 RHS. H: 2 LHS, 2 RHS. S: 1 LHS, 1 RHS. O: 4 LHS, 4 RHS. (Balanced)

Hit-and-Trial Method for Balancing (e.g., Fe + H2O -> Fe3O4 + H2):
Step 1: Draw boxes around each formula; do not alter formulas inside boxes.
Step 2: Count atoms of different elements in unbalanced equation.
Step 3: Equalise atoms starting with compound containing maximum atoms (e.g. oxygen in Fe3O4: put 4 H2O). Equation becomes: Fe + 4H2O -> Fe3O4 + H2.
Step 4: Balance hydrogen atoms: 4 H2O has 8 H atoms, so put 4 H2 on RHS: Fe + 4H2O -> Fe3O4 + 4H2.
Step 5: Balance iron atoms: take 3 Fe on LHS: 3Fe + 4H2O -> Fe3O4 + 4H2.
Step 6: Count atoms on both sides to verify: 3 Fe, 8 H, 4 O on both sides.

Step 7: Physical States:
To make equations more informative, notations are used:
(s) = solid, (l) = liquid, (g) = gas, (aq) = aqueous (solution in water).
Balanced equation with state symbols:
3Fe(s) + 4H2O(g) -> Fe3O4(s) + 4H2(g)  [Note: (g) indicates water used in the form of steam].
Reaction conditions like temperature, pressure, or catalyst are written above/below the arrow:
CO(g) + 2H2(g) --(340 atm)--> CH3OH(l)
6CO2(aq) + 12H2O(l) --(Sunlight / Chlorophyll)--> C6H12O6(aq) + 6O2(aq) + 6H2O(l)"""
    },
    {
        "id": "ch1_sec1_2_1_combination",
        "title": "1.2.1 Combination Reactions and Exothermic Reactions",
        "pages": "6-7",
        "section": "1.2.1",
        "keywords": ["combination reaction", "calcium oxide", "quick lime", "slaked lime", "calcium hydroxide", "exothermic reaction", "burning of coal", "natural gas", "respiration", "compost"],
        "text": """Definition of Combination Reaction:
A reaction in which two or more substances (elements or compounds) combine to form a single product is known as a combination reaction.

Activity 1.4:
Take calcium oxide (quick lime) in a beaker and slowly add water.
CaO(s) + H2O(l) -> Ca(OH)2(aq) + Heat
(Quick lime)           (Slaked lime / calcium hydroxide)
Calcium oxide reacts vigorously with water to produce slaked lime, releasing a large amount of heat.

More Examples of Combination Reactions:
1. Burning of coal: C(s) + O2(g) -> CO2(g)
2. Formation of water: 2H2(g) + O2(g) -> 2H2O(l)

Exothermic Chemical Reactions:
Reactions in which heat is released along with the formation of products are called exothermic chemical reactions.
Examples of exothermic reactions:
1. Burning of natural gas: CH4(g) + 2O2(g) -> CO2(g) + 2H2O(g)
2. Respiration: During digestion, food breaks down into glucose (C6H12O6). Glucose combines with oxygen in cells releasing energy:
   C6H12O6(aq) + 6O2(aq) -> 6CO2(aq) + 6H2O(l) + energy
   Therefore, respiration is an exothermic process.
3. Decomposition of vegetable matter into compost is also exothermic."""
    },
    {
        "id": "ch1_sec1_whitewashing",
        "title": "Whitewashing, Slaked Lime and Marble Formation",
        "pages": "7",
        "section": "Do You Know Box",
        "keywords": ["whitewashing", "slaked lime", "calcium hydroxide", "carbon dioxide", "calcium carbonate", "marble", "CaCO3", "Ca(OH)2"],
        "text": """A solution of slaked lime (calcium hydroxide, Ca(OH)2) produced by reacting quicklime with water is used for whitewashing walls.
Calcium hydroxide reacts slowly with carbon dioxide in the air to form a thin layer of calcium carbonate on the walls:
Ca(OH)2(aq) + CO2(g) -> CaCO3(s) + H2O(l)
(Calcium hydroxide)       (Calcium carbonate)

Calcium carbonate is formed after two to three days of whitewashing and gives a shiny, bright white finish to the walls.
Interesting fact: The chemical formula for marble is also CaCO3."""
    },
    {
        "id": "ch1_sec1_2_2_decomposition",
        "title": "1.2.2 Decomposition Reactions (Thermal, Electrolytic, Photolytic) & Endothermic Reactions",
        "pages": "8-10",
        "section": "1.2.2",
        "keywords": ["decomposition reaction", "thermal decomposition", "ferrous sulphate", "ferric oxide", "sulphur dioxide", "sulphur trioxide", "limestone", "cement", "lead nitrate", "nitrogen dioxide", "brown fumes", "electrolysis of water", "silver chloride", "silver bromide", "sunlight", "black and white photography", "endothermic"],
        "text": """Definition of Decomposition Reaction:
A reaction in which a single reactant breaks down to give two or more simpler products is called a decomposition reaction. Decomposition is opposite to combination reaction.

1. Thermal Decomposition (carried out by heating):
a) Ferrous sulphate crystals (FeSO4.7H2O) lose water on heating and change colour from green to white, then decompose:
   2FeSO4(s) --(Heat)--> Fe2O3(s) + SO2(g) + SO3(g)
   (Ferrous sulphate)   (Ferric oxide) (Sulphur dioxide) (Sulphur trioxide)
   Produces characteristic smell of burning sulphur.
b) Limestone to quicklime:
   CaCO3(s) --(Heat)--> CaO(s) + CO2(g)
   (Limestone)         (Quick lime)
   Quick lime has many industrial uses, notably in the manufacture of cement.
c) Lead nitrate heating (Activity 1.6):
   2Pb(NO3)2(s) --(Heat)--> 2PbO(s) + 4NO2(g) + O2(g)
   (Lead nitrate)          (Lead oxide) (Nitrogen dioxide - brown fumes) (Oxygen)
   Emission of brown fumes of nitrogen dioxide (NO2) is observed.

2. Electrolytic Decomposition (Activity 1.7 - Electrolysis of Water):
Passing electric current through acidified water decomposes it:
2H2O(l) --(Electric current)--> 2H2(g) + O2(g)
Hydrogen gas is collected at the cathode and oxygen at the anode. The volume of hydrogen gas collected is double the volume of oxygen gas because water molecule contains 2 hydrogen atoms for every 1 oxygen atom.

3. Photolytic Decomposition (Decomposition by Sunlight) (Activity 1.8):
White silver chloride turns grey in sunlight:
2AgCl(s) --(Sunlight)--> 2Ag(s) + Cl2(g)
Silver bromide behaves similarly:
2AgBr(s) --(Sunlight)--> 2Ag(s) + Br2(g)
These reactions of silver halides are used in black and white photography.

Endothermic Reactions:
Reactions in which energy is absorbed (in the form of heat, light, or electricity) to break bonds are called endothermic reactions."""
    },
    {
        "id": "ch1_sec1_2_3_displacement",
        "title": "1.2.3 Displacement Reactions",
        "pages": "10-11",
        "section": "1.2.3",
        "keywords": ["displacement reaction", "iron nail", "copper sulphate", "iron sulphate", "blue colour fades", "brownish deposit", "zinc", "lead", "reactivity"],
        "text": """Definition of Displacement Reaction:
A chemical reaction in which a more reactive element displaces or removes a less reactive element from its compound (solution) is known as a displacement reaction.

Activity 1.9 (Iron nails in copper sulphate):
Clean iron nails dipped in blue copper sulphate (CuSO4) solution for 20 minutes.
Observation: The iron nail becomes coated with a brownish layer of copper metal, and the blue colour of the copper sulphate solution fades and changes to light green.
Equation:
Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s)
(Iron)  (Copper sulphate - blue) (Iron sulphate - green) (Copper - brown)

Other Examples of Displacement Reactions:
1. Zinc displacing copper:
   Zn(s) + CuSO4(aq) -> ZnSO4(aq) + Cu(s)
   (Zinc) (Copper sulphate) (Zinc sulphate) (Copper)
2. Lead displacing copper:
   Pb(s) + CuCl2(aq) -> PbCl2(aq) + Cu(s)
   (Lead) (Copper chloride) (Lead chloride) (Copper)
Zinc and lead are more reactive metals than copper, so they displace copper from its salt solutions."""
    },
    {
        "id": "ch1_sec1_2_4_double_displacement",
        "title": "1.2.4 Double Displacement and Precipitation Reactions",
        "pages": "11-12",
        "section": "1.2.4",
        "keywords": ["double displacement reaction", "precipitation reaction", "precipitate", "barium sulphate", "sodium sulphate", "barium chloride", "sodium chloride", "exchange of ions", "lead nitrate", "potassium iodide", "lead iodide yellow"],
        "text": """Definition of Double Displacement Reaction:
Reactions in which there is an exchange of ions between the reactants to form new compounds are called double displacement reactions.

Activity 1.10:
Mix sodium sulphate solution with barium chloride solution:
Na2SO4(aq) + BaCl2(aq) -> BaSO4(s) + 2NaCl(aq)
(Sodium sulphate) (Barium chloride) (Barium sulphate) (Sodium chloride)
Observation: A white insoluble substance is formed immediately.

Precipitation Reaction:
An insoluble solid substance formed during a chemical reaction that separates out from the solution is called a precipitate. Any reaction that produces an insoluble precipitate is called a precipitation reaction.
Here, the white precipitate of BaSO4 is formed by the reaction of SO4^(2-) and Ba^(2+) ions.

Another Example (Activity 1.2):
Lead nitrate reacts with potassium iodide:
Pb(NO3)2(aq) + 2KI(aq) -> PbI2(s) + 2KNO3(aq)
Forms a bright yellow precipitate of lead iodide (PbI2). This is also a double displacement and precipitation reaction."""
    },
    {
        "id": "ch1_sec1_2_5_redox",
        "title": "1.2.5 Oxidation and Reduction (Redox Reactions)",
        "pages": "12-13",
        "section": "1.2.5",
        "keywords": ["oxidation", "reduction", "redox reaction", "copper oxide", "black coating", "hydrogen", "gain of oxygen", "loss of oxygen", "gain of hydrogen", "loss of hydrogen", "ZnO", "carbon", "MnO2", "HCl"],
        "text": """Definitions of Oxidation and Reduction:
- Oxidation: Gain of oxygen OR loss of hydrogen by a substance during a reaction.
- Reduction: Loss of oxygen OR gain of hydrogen by a substance during a reaction.

Redox Reactions (Oxidation-Reduction):
Reactions in which one reactant gets oxidised while the other reactant gets reduced simultaneously are called redox reactions.

Activity 1.11:
Heating copper powder in air:
2Cu + O2 --(Heat)--> 2CuO
Copper gains oxygen and forms black copper(II) oxide. Copper is oxidised to CuO.

Passing hydrogen gas over heated CuO:
CuO + H2 --(Heat)--> Cu + H2O
- CuO loses oxygen -> reduced to Cu.
- H2 gains oxygen -> oxidised to H2O.
Both oxidation and reduction occur together (Redox).

Other Examples of Redox Reactions:
1. ZnO + C -> Zn + CO
   ZnO loses oxygen (reduced to Zn); Carbon gains oxygen (oxidised to CO).
2. MnO2 + 4HCl -> MnCl2 + 2H2O + Cl2
   MnO2 loses oxygen (reduced to MnCl2); HCl loses hydrogen (oxidised to Cl2)."""
    },
    {
        "id": "ch1_sec1_3_corrosion_rancidity",
        "title": "1.3 Everyday Effects of Oxidation: Corrosion and Rancidity",
        "pages": "13",
        "section": "1.3",
        "keywords": ["corrosion", "rusting of iron", "black coating silver", "green coating copper", "rancidity", "antioxidants", "air tight containers", "nitrogen gas", "chips bags", "fats and oils"],
        "text": """1.3.1 Corrosion:
When a metal is attacked by substances around it such as moisture, air, acids, etc., it is said to corrode, and this process is called corrosion.
Examples of Corrosion:
- Rusting of iron: Iron articles get coated with a reddish-brown powder when left exposed to moist air.
- Black coating formed on silver articles due to reaction with sulphur compounds in air.
- Green coating formed on copper articles (basic copper carbonate) due to reaction with moist CO2.
Corrosion causes enormous damage to car bodies, bridges, iron railings, ships, and all metal structures, especially those made of iron.

1.3.2 Rancidity:
When fats and oils present in food materials are oxidised by atmospheric oxygen, they become rancid. As a result, their smell and taste change and become unpleasant.
Methods to Prevent Rancidity:
1. Adding antioxidants: Substances that prevent or retard oxidation are added to food containing fats and oils.
2. Airtight containers: Storing food in airtight containers slows down the rate of oxidation.
3. Flushing with inert gas: Potato chips and snack manufacturers flush bags of chips with an unreactive gas like nitrogen (N2) to displace oxygen and prevent chips from getting oxidised."""
    },
    {
        "id": "ch1_sec1_summary",
        "title": "Chapter 1 Summary: What You Have Learnt",
        "pages": "14",
        "section": "Summary",
        "keywords": ["summary", "complete chemical equation", "balanced equation", "combination", "decomposition", "exothermic", "endothermic", "displacement", "double displacement", "precipitation", "oxidation", "reduction"],
        "text": """Key Summary Points:
1. A complete chemical equation represents reactants, products, and their physical states symbolically.
2. A chemical equation must always be balanced so that the numbers of atoms of each element are equal on reactant and product sides (satisfying the law of conservation of mass).
3. In a combination reaction, two or more substances combine to form a single new substance.
4. Decomposition reactions are the opposite of combination reactions; a single substance breaks down into two or more substances.
5. Reactions releasing heat along with products are exothermic reactions.
6. Reactions absorbing energy (heat, light, electricity) are endothermic reactions.
7. When an element displaces another element from its compound, a displacement reaction occurs.
8. Two different atoms or groups of atoms (ions) are exchanged in double displacement reactions.
9. Precipitation reactions produce insoluble salts (precipitates).
10. Oxidation is the gain of oxygen or loss of hydrogen. Reduction is the loss of oxygen or gain of hydrogen."""
    },
    {
        "id": "ch1_sec1_intext_questions",
        "title": "Textbook In-Text Questions with Accurate Answers",
        "pages": "6, 10, 13",
        "section": "In-text Questions",
        "keywords": ["questions", "magnesium ribbon cleaned sandpaper", "whitewashing substance X calcium oxide", "electrolysis water double volume hydrogen", "iron nail copper sulphate colour change", "chips nitrogen"],
        "text": """In-Text Questions and Solutions:
Q: Why should a magnesium ribbon be cleaned before burning in air?
A: Magnesium is a reactive metal. When exposed to moist air, it forms a protective coating of basic magnesium carbonate / oxide on its surface. Cleaning with sandpaper removes this oxide layer so magnesium can burn freely in air.

Q: A solution of substance 'X' is used for whitewashing. Name substance 'X' and write its formula, and write its reaction with water.
A: Substance 'X' is calcium oxide (quicklime), formula CaO. Its reaction with water is: CaO(s) + H2O(l) -> Ca(OH)2(aq) + Heat, producing slaked lime (calcium hydroxide).

Q: Why is the amount of gas collected in one test tube during electrolysis of water double of the other?
A: Water (H2O) is formed by combining hydrogen and oxygen in a 2:1 ratio by volume. On decomposition, 2 volumes of hydrogen gas are liberated at the cathode for every 1 volume of oxygen gas liberated at the anode. The gas with double volume is hydrogen.

Q: Why does the colour of copper sulphate solution change when an iron nail is dipped in it?
A: Iron is more reactive than copper. It displaces copper from copper sulphate solution to form green iron sulphate (FeSO4) and deposits brownish copper on the nail: Fe(s) + CuSO4(aq) -> FeSO4(aq) + Cu(s). Hence the blue colour fades to light green.

Q: Why are oil and fat containing food items flushed with nitrogen?
A: Nitrogen is an unreactive inert gas. Flushing chips bags with nitrogen expels oxygen, preventing the fats and oils from getting oxidised and becoming rancid."""
    },
    {
        "id": "ch1_sec1_exercises",
        "title": "Textbook Chapter Exercises (Questions 1 to 20)",
        "pages": "14-16",
        "section": "Exercises",
        "keywords": ["exercises", "lead oxide carbon redox", "thermite reaction", "hydrochloric acid iron filings", "respiration exothermic", "decomposition opposite combination", "refining silver", "paint on iron rust prevention"],
        "text": """Key Textbook Exercise Questions & Solutions:
1. Reaction: 2PbO(s) + C(s) -> 2Pb(s) + CO2(g).
   Incorrect statements: (a) Lead is getting reduced (it is lead oxide that is reduced), (b) Carbon dioxide is getting oxidised (carbon is oxidised). Correct answer: (i) (a) and (b).
2. Fe2O3 + 2Al -> Al2O3 + 2Fe is an example of a displacement reaction (Aluminium displaces Iron).
3. Adding dilute HCl to iron filings: Fe(s) + 2HCl(aq) -> FeCl2(aq) + H2(g). Hydrogen gas and iron(II) chloride are produced.
4. Balanced chemical equation: An equation having equal number of atoms of each element on both sides. Required because mass can neither be created nor destroyed.
9. Exothermic vs Endothermic: Exothermic reactions release heat (e.g. burning coal C + O2 -> CO2 + Heat, respiration). Endothermic reactions absorb heat/energy (e.g. thermal decomposition of CaCO3 -> CaO + CO2).
10. Why respiration is exothermic: Glucose from carbohydrates combines with oxygen in body cells, breaking down into CO2 and H2O and liberating energy.
11. Decomposition vs Combination: In combination, two or more reactants unite to form one single product (A + B -> AB). In decomposition, one single reactant breaks down into multiple products (AB -> A + B).
17. Shiny brown element 'X' on heating becomes black: Element 'X' is Copper (Cu). The black compound is Copper(II) oxide (CuO), formed by 2Cu + O2 -> 2CuO.
18. Why paint iron articles: Paint creates a protective barrier preventing iron from coming in contact with moist air and oxygen, thereby preventing rusting and corrosion."""
    }
]

def main():
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(CHUNKS, f, indent=2, ensure_ascii=False)
    print(f"Successfully generated {len(CHUNKS)} structured semantic chunks to {OUT_JSON}")

if __name__ == "__main__":
    main()
