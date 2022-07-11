# Mutant DNA sequencer

Odoo Python Module to verify if a DNA sequence is from Mutant or Human

## Author

* Francisco Javier Luna Vázquez \<<frahik@gmail.com>\>

## Installation

### Requirements

You need to have the following:

* [Odoo Community](https://www.odoo.com/documentation/15.0/administration/install/install.html)
* Python 3.8 or later
* [Numpy](https://pypi.org/project/numpy/) == `1.23.1`

### Run on local

```bash
./odoo-bin -i mutant_dna_detector --addons-path <directories>
```

* `--addons-path <directories>`: comma-separated list of directories in which modules are stored. These directories are scanned for modules. More information at: [Odoo Cli](https://www.odoo.com/documentation/15.0/developer/cli.html#cmdoption-odoo-bin-addons-path)



### Run the tests

```bash
./odoo-bin -i mutant_dna_detector --test-enable --test-tags dna_sequencer --stop-after-init
```

## API

### Mutant

Use the mutant url to check if a DNA sequence is from a Human or Mutant.

| POST | `/mutant` |
|------|-----------|

`Sample Request`:

```bash
curl -i \
    -H "Content-Type: application/json" \
    -X POST -d '{"dna":["ATGCGA","CAGTGC","TTATGT","AGAAGG","CCCCTA","TCACTG"]}' \
    http://localhost:8069/mutant
```

#### Body:

* **dna** `list of strings` (`required`): The server stores the DNA sequence to determine if it is from a human or mutant

Sample Response:
```bash
{
    "jsonrpc": "2.0",
    "id": null,
    "result": ""
}
```

#### Response:

A successful request returns a JSON response body

* **jsonrpc** `string`: The version of the jsonrpc api
* **id** `int`: Null key.
* **result**: The Response of the server, the possible values are:
    + `""` empty string if the DNA provided is from a human
    + `400 Bad Request: The browser (or proxy) sent a request that this server could not understand.` If the DNA provided doesn't correspond to a DNA possible values (`A`, `C`, `T`, `G`)
    + `403 Forbidden: You don't have the permission to access the requested resource. It is either read-protected or not readable by the server.` if the DNA provided is from a mutant.

### Stats

Use the stats url to check the number of dna queries performed,

| GET | `/stats` |
|------|-----------|

`Sample Request`:

```bash
curl -i \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -X GET -d {}
    http://localhost:8069/stats
```

#### Body:

* Require a empty json `-d {}`

Sample Response:
```bash
{
    "jsonrpc": "2.0",
    "id": null,
    "result": {
        "count_mutant_dna": 17,
        "count_human_dna": 7,
        "ratio": 2.4285714285714284
    }
}
```

#### Response:

A successful request returns a JSON response body

* **jsonrpc** `string`: The version of the jsonrpc api
* **id** `int`: Null key.
* **result**:
    + **count_mutant_dna** `int`: The amount of processed DNA that corresponds to mutants
    + **count_human_dna** `int`: The amount of processed DNA that corresponds to humans
    + **ratio** `float`: The ratio indicates how many times one DNA mutant it's found by one of a DNA human.

## Licenses

This repository is licensed under LGPL-3.0.
