{
    "name": "mutant_dna_detector",
    "summary": """
        Dummy Module used for demonstration purposes, whose function is to implement an API that receives a JSON
        of Strings representing the DNA sequence. """,
    "author": "Francisco Javier Luna Vázquez",
    "category": "Technical",
    "version": "15.0.1.0.1",
    "license": "LGPL-3",
    "depends": ["base"],
    "data": [
        "security/ir.model.access.csv",
        "views/dna_sequencer_views.xml",
    ],
    "external_dependencies": {
        "python": ["numpy"],
    },
    # only loaded in demonstration mode
    "demo": [
        "demo/dna_sequencer.xml",
    ],
}
