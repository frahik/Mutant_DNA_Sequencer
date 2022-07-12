import re

import numpy as np
from odoo import _, api, fields, models
from odoo.exceptions import UserError, ValidationError


class DnaSequencer(models.Model):
    _name = "dna.sequencer"
    _description = "Dna Sequencer"

    _rec_name = "dna"
    dna = fields.Char(required=True)
    is_mutant = fields.Boolean(readonly=True)

    @api.model
    def create(self, vals):
        """If the is_mutant field is not present in the vals dictionary, then check the dna sequence and
        set the is_mutant field to the result of the check.

        :param vals: The values that are being passed to the create method
        :return: The super().create(vals) is returning the created record.
        """
        if "is_mutant" not in vals and vals["dna"]:
            vals["is_mutant"] = self._check_dna_sequence(vals["dna"])
        return super().create(vals)

    def _check_dna_sequence(self, dna_sequence):
        """The method that is used to check if a DNA sequence is mutant or not."""
        self._validate_dna_sequence(dna_sequence)
        # Check Rows
        find_mutant_sequence_on_rows = self._find_mutant_sequence(dna_sequence)
        if find_mutant_sequence_on_rows:
            return True
        dna_sequence_matrix = self._get_dna_matrix(dna_sequence)
        # Validate the returned matrix
        if len(dna_sequence_matrix.shape) != 2:
            raise UserError(_("DNA provided is corrupt, the sequence provided has different column length."))
        # The rows have already been checked, if the columns are less than 4, it is not necessary to check any more
        if dna_sequence_matrix.shape[1] < 4:
            return False
        # Transpose the matrix to now check columns
        find_mutant_sequence_on_columns = self._find_mutant_sequence_on_matrix(dna_sequence_matrix.T)
        if find_mutant_sequence_on_columns:
            return True
        # Transform the diagonals to new matrix, as expected return a triangle, will fill the diagonal with
        # empty values to assure that not will compare less elements than expected.
        diagonals_matrix = self._get_diagonal_matrix(dna_sequence_matrix)
        find_mutant_sequence_on_diagonals = self._find_mutant_sequence_on_matrix(diagonals_matrix)
        if find_mutant_sequence_on_diagonals:
            return True
        return False

    def _validate_dna_sequence(self, dna_sequence):
        """It checks if the DNA sequence contains any characters other than A, C, T, G, and commas

        :param dna_sequence: The DNA sequence to be validated.
        :return: True, if the DNA sequence doesn't contain different characters.
        """
        if re.search(r"[^ACTG,]", dna_sequence):
            raise ValidationError(_("DNA provided is corrupt, the sequence contains an incorrect value"))
        return True

    def _get_dna_matrix(self, dna_sequence):
        """It takes a string of comma separated DNA sequences and returns a numpy array (matrix) of the DNA
        sequences.
        :return: A numpy array of the DNA string split by commas.
        """
        return np.array([list(row) for row in dna_sequence.split(",")])

    def _find_mutant_sequence_on_matrix(self, matrix):
        """It takes a matrix and returns True if it contains a sequence of four or more of the same letter in a row.

        :param matrix: The matrix of DNA sequences
        :return: the result of the function _find_mutant_sequence.
        """
        dna_columns_sequence = self._get_dna_sequence_from_matrix(matrix)
        return self._find_mutant_sequence(dna_columns_sequence)

    def _find_mutant_sequence(self, dna_string_sequence):
        """It takes a string of DNA and returns True if it contains a sequence of four or more of the same
        letter in a row.

        :param dna_string_sequence: The DNA string sequence to be searched
        :return: A boolean value.
        """
        return bool(re.search(r"([ATCG])\1{3}", dna_string_sequence))

    def _get_dna_sequence_from_matrix(self, matrix):
        """It takes a matrix of DNA sequences and returns a string of DNA sequences separated by commas

        :param matrix: a list of lists of characters, representing the DNA sequence
        :return: A string of the DNA sequence.
        """
        return ",".join(["".join(row) for row in matrix])

    def _get_diagonal_matrix(self, matrix):
        """Transform the diagonals of given matrix to a new matrix with the same length of the principal diagonal.
        The diagonal row with less than 4 elements, will be deleted, doesn't have enough information.

        Original   | Diagonal 1    | Diagonal      |  Returned Squared Matrix
        Matrix     |               |               |
        5 x 5      | max length 5  | max length 5  |  5 x 6
        ---------------------------------------------------
        [C T T T C] | [C]           | [C]           | [T T T T  ]    -¬
        [T C T T C] | [T T]         | [T C]         | [C C C T C]      |- First Diagonal
        [T T C C T] | [T C T]       | [T T T]       | [T T C C  ]    _]
        [T C T C T] | [T T T T]     | [T T C T]     | [T T C T  ]    -¬
        [C T C C T] | [C C C T C]   | [C C C C T]   | [C C C C T]      |- Second Diagonal
                    | [T T C C]     | [T T T C]     | [T T T C  ]    -]
                    | [C C T]       | [T C C]       |
                    | [C T]         | [T T]         |
                    | [T]           | [C]           |
        """
        diagonals = [matrix[::-1, :].diagonal(i) for i in range(-matrix.shape[0] + 1, matrix.shape[1])]
        diagonals.extend(matrix.diagonal(i) for i in range(matrix.shape[1] - 1, -matrix.shape[0], -1))
        # Remove invalid diagonal elements with less than 4 sequence elements to compare
        diagonals = [a for a in diagonals if len(a) > 3]
        if not diagonals:
            return np.zeros((2, 2), str)
        # Create a new matrix with the length of the principal diagonal
        max_len_diag = min(matrix.shape[0], matrix.shape[1])
        matrix_vals = []
        for diagonal in diagonals:
            missing_values = max_len_diag - len(diagonal)
            # if the diagonal has less elements than the principal diagonal, include a empty string elements.
            matrix_vals.append(np.append(diagonal, np.repeat("", missing_values)))
        return np.array(matrix_vals)

    _sql_constraints = [("dna_sequence_uniq", "unique (dna)", "This DNA already exists on the database")]
