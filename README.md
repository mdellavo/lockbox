# lockbox

Library and command-line tool to store encrypted secrets

## Usage

```
$ lockbox --help
usage: lockbox [-h] {set,get,gen,dump} ...

positional arguments:
  {set,get,gen,dump}
    set               Add a key to the lockbox
    get               Get a key from the lockbox
    gen               Generate a key and store in lockbox
    dump              Dump plain-text lockbox as JSON

optional arguments:
  -h, --help          show this help message and exit
```

Each subcommand offer's it's own help.  "-" may be used in path for stdin.

## Examples
```sh
$ LOCKBOX_SECRET=test lockbox set test.lockbox foo
v?
$ cat test.lockbox
{
    "foo": "z3HKLkfsHedroHoaA323qQ==|gAAAAABYv2v4vqPokfYoJjJDiP5tw01QCyO4jGpSwDv5KqqoTIqDw3Yq_bkyjaCgP4Vhd6-Ms2L_rieA04fVTecpDUBf7iETlw=="
}
$ LOCKBOX_SECRET=test lockbox get test.lockbox foo
abc123
$ LOCKBOX_SECRET=test lockbox dump test.lockbox
{
    "foo": "abc123"
}
```

## Author

Marc DellaVolpe  (marc.dellavolpe@gmail.com)

## License
    The MIT License (MIT)

    Copyright (c) 2016 Marc DellaVolpe

    Permission is hereby granted, free of charge, to any person obtaining a copy of this
    software and associated documentation files (the "Software"), to deal in the Software
    without restriction, including without limitation the rights to use, copy, modify, merge,
    publish, distribute, sublicense, and/or sell copies of the Software, and to permit
    persons to whom the Software is furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in all copies
    or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
    INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR
    PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE
    FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
    OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
    DEALINGS IN THE SOFTWARE.
