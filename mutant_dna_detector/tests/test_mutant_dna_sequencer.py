import warnings

from numpy import VisibleDeprecationWarning
from odoo.exceptions import ValidationError, UserError
from odoo.tests import TransactionCase, tagged
from odoo.tools import mute_logger
from psycopg2 import IntegrityError

warnings.filterwarnings("ignore", category=VisibleDeprecationWarning)


@tagged("dna_sequencer")
class TestDnaSequencer(TransactionCase):
    def setUp(self):
        super().setUp()
        self.dna_10_x_5_no_mutant_sample = self.browse_ref("mutant_dna_detector.dna_10_x_5_no_mutant_sample")

    def test_01_no_duplicates(self):
        """Check that cannot be store twice the DNA sequence."""
        with self.assertRaisesRegex(IntegrityError, "unique constraint"), mute_logger("odoo.sql_db"):
            self.dna_10_x_5_no_mutant_sample.copy()

    def test_02_validate_dna_sequence(self):
        """1.- Use the sample data to check if the sequence is valid.
        2.- Create a DNA sequence with different characters that not corresponds to dna sequence.
        3.- Assert that the model raises a ValidationError.
        """
        self.assertTrue(self.env["dna.sequencer"]._validate_dna_sequence(self.dna_10_x_5_no_mutant_sample.dna))
        dna_invalid = "ACTCAC,AC23XP"
        with self.assertRaisesRegex(ValidationError, "DNA provided is corrupt,"):
            self.env["dna.sequencer"]._validate_dna_sequence(dna_invalid)

    def test_03_find_mutant_sequence(self):
        """1.- Check if the sequence has the same character 4 times, it's a mutant sequence.
        2.- Check if the sequence has the same character 6 times but it's comma divided, it's a human sequence.
        3.- Check if the sequence has the same character 4 times, doesn't care were it's found (but not comma divided),
            it's a mutant sequence.
        """
        mutant_sequence_test01 = "AAAA"
        self.assertTrue(self.env["dna.sequencer"]._find_mutant_sequence(mutant_sequence_test01))

        mutant_sequence_test02 = "AAA,AAA"
        self.assertFalse(self.env["dna.sequencer"]._find_mutant_sequence(mutant_sequence_test02))

        mutant_sequence_test01 = "AAAC,ACAA,AGGG,GGGG"
        self.assertTrue(self.env["dna.sequencer"]._find_mutant_sequence(mutant_sequence_test01))

    def test_04_get_dna_sequence_from_matrix(self):
        """1.- Obtain the DNA matrix of a demo data.
        2.- Check that the method `_get_dna_sequence_from_matrix` returns the same sequence as the DNA of the demo.
        3.- Transpose the DNA matrix sequence and check that the sequence it's not the same as the Original sequence.
        4.- Check that the sequence corresponds to the transpose dna sequence.
        """
        matrix = self.dna_10_x_5_no_mutant_sample._get_dna_matrix()

        dna = self.env["dna.sequencer"]._get_dna_sequence_from_matrix(matrix)
        self.assertEqual(dna, self.dna_10_x_5_no_mutant_sample.dna)

        transpose_dna_sequence = self.env["dna.sequencer"]._get_dna_sequence_from_matrix(matrix.T)
        self.assertNotEqual(self.dna_10_x_5_no_mutant_sample.dna, transpose_dna_sequence)
        # Now the sequence is 5 x 10
        self.assertEqual(transpose_dna_sequence, "ACTGC,CTAGC,GAACC,GGTAA,AATAC,AGCCG,CCCTG,TAATT,GATGA,ACTGA")

    def test_05_diagonal_matrix(self):
        """Test that the diagonal matrix obtained corresponds to the all the diagonals of the original matrix with
        more than 3 elements, similar as the following representation.
            Original Matrix   | Diagonal 1   | Diagonal 2   | Diagonal Matrix
        [A C G G A A C T G A] | [A]          | [A]          | [G A A G]
        [C T A G A G C A A C] | [C C]        | [G C]        | [C G A G A]
        [T A A T T C C A T T] | [T T G]      | [T A T]      | [C C T A A]
        [G G C A A C T T G G] | [G A A G]    | [C A T G]    | [C A T G C]
        [C C C A C G G T A A] | [C G A G A]  | [A C A G A]  | [A A C C T]
                              | [C C T A A]  | [A G C T A]  | [C C C A G]
                              | [C A T G C]  | [G A C T T]  | [G T A A A]
                              | [A A C C T]  | [G G T C G]  | [G T T C]
                              | [C C C A G]  | [C A T A G]  | [C A T G]
                              | [G T A A A]  | [A T A A C]  | [A C A G A]
                              | [G T T C]    | [C A C A]    | [A G C T A]
                              | [T G T]      | [T G C]      | [G A C T T]
                              | [A G]        | [G C]        | [G G T C G]
                              | [A]          | [C]          | [C A T A G]
                                                            | [A T A A C]
                                                            | [C A C A]
        """
        matrix = self.dna_10_x_5_no_mutant_sample._get_dna_matrix()
        diagonal_matrix = self.env["dna.sequencer"]._get_diagonal_matrix(matrix)
        diagonal_dna_sequence = self.env["dna.sequencer"]._get_dna_sequence_from_matrix(diagonal_matrix)
        self.assertEqual(
            diagonal_dna_sequence,
            "GAAG,CGAGA,CCTAA,CATGC,AACCT,CCCAG,GTAAA,GTTC,CATG,ACAGA,AGCTA,GACTT,GGTCG,CATAG,ATAAC,CACA",
        )

    def test_06_no_muntant_sample(self):
        """It creates a new DNA sequencer and asserts that the sequencer is not a mutant."""
        dna = "AAACCC,TTTGGG,AAACCC,TTTGGG,AAACCC"
        sequencer = self.env["dna.sequencer"].create({"dna": dna})
        self.assertFalse(sequencer.is_mutant)

    def test_07_mutant_sample(self):
        """It creates a new DNA sequencer and asserts that the sequencer is a mutant."""
        dna = "ACGGAACTGA,CTAGAGCAAC,TAATTCCATT,GGCAACTTGG,CCCACAAAAA"
        sequencer = self.env["dna.sequencer"].create({"dna": dna})
        self.assertTrue(sequencer.is_mutant)

    def test_08_invalid_sequence(self):
        dna = "AC,TTT,ACT"
        with self.assertRaisesRegex(UserError, "DNA provided is corrupt,"):
            is_mutant = self.env["dna.sequencer"].create({"dna": dna}).is_mutant

    def test_09_no_sequence(self):
        dna = ",,,"
        sequencer = self.env["dna.sequencer"].create({"dna": dna})
        self.assertFalse(sequencer.is_mutant)
