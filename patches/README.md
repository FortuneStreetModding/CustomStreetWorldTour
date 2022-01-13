This directory contains .yaml patches which define how to patch the main.dol in addition to CSMM's patches.

Each .yaml file must contain a patches key with a list of following key value pairs:

- boomAddress: The boom street virtual address. You can use [Fortune Street Address Calculator](https://fortunestreetmodding.github.io/calculator) if you do not know the boom street virtual address
- format: a valid format string, see [Format Characters](https://docs.python.org/3/library/struct.html#format-characters) for a list of valid values. The format should always start with a ">" to indicate big endian writing
- originalValue: the original value at this location
- patchValue: the value that should be written