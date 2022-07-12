import json

from odoo.exceptions import UserError, ValidationError
from odoo.http import Controller, request, route
from werkzeug.exceptions import Forbidden, BadRequest, UnprocessableEntity


class MutantDnaSequencer(Controller):
    @route("/mutant/", type="json", auth="none", methods=["POST"], csrf=False)
    def dna_sequence_mutant_detector(self):
        """It takes a DNA sequence, checks if it's already in the database, if it is, it returns the
        result, if it isn't, it creates a new record and returns the result.
        """
        dna_data = json.loads(request.httprequest.get_data().decode()).get("dna")
        if not dna_data:
            raise request._json_response(
                result="DNA provided is corrupt, the sequence contains an incorrect value.", error=403
            )
        dna_data_string = ",".join(dna_data).upper()
        dna_sequenced = request.env["dna.sequencer"].search([("dna", "=", dna_data_string)], limit=1)
        if dna_sequenced:
            return self.get_dna_sequence_response(dna_sequenced)
        new_dna_sequence = request.env["dna.sequencer"].sudo().create({"dna": dna_data_string})
        return self.get_dna_sequence_response(new_dna_sequence)

    def get_dna_sequence_response(self, dna_sequenced):
        """If the dna_sequenced is a mutant, return an empty string, if not, return a Forbidden response. If the
        DNA contains foreign characters return a BadRequest.

        :param dna_sequenced: The DNA sequence that was sent to the API
        :return: The response is being returned.
        """
        try:
            if dna_sequenced.is_mutant:
                return {"status": Forbidden()}
        except ValidationError:
            request.env.clear()
            return {"status": BadRequest()}
        except UserError:
            request.env.clear()
            return {"status": UnprocessableEntity()}
        return {"status": "200 OK"}

    @route("/stats/", type="json", auth="none", methods=["GET"], csrf=False)
    def give_stats(self):
        """It returns a dictionary with the number of mutant and human DNA sequences, and the ratio between them."""
        count_mutant_dna = request.env["dna.sequencer"].search_count([("is_mutant", "=", True)])
        count_human_dna = request.env["dna.sequencer"].search_count([("is_mutant", "=", False)])
        ratio = count_human_dna and count_mutant_dna / count_human_dna or 0
        return {"count_mutant_dna": count_mutant_dna, "count_human_dna": count_human_dna, "ratio": ratio}
