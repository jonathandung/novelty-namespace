# novelty-namespace

[![#StandWithPalestine](https://raw.githubusercontent.com/TheBSD/StandWithPalestine/main/badges/StandWithPalestine.svg)](https://github.com/TheBSD/StandWithPalestine/blob/main/docs/README.md)

Helps create namespace objects using class declarations, such that it is easier to
attach attributes and functions to an object without leaking state. Any compliant
Python implementation should work, but Python 3.15+ is required.

> [!NOTE]
> As with other novelties that involve heavy metaprogramming, it is difficult to make
> this module type check well. Be prepared to apply a lot of ignore comments.

## Development

If you want to build documentation locally, install the `docs` dependency group and run
`make html` in the `docs` directory.

Run tests with `python -m unittest`.

If coverage is desired, install the `cov` extra and run `coverage run -m unittest`.
