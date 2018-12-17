# pyocfl
Python 3.x client for the [Oxford Common Filesystem Layout (OCFL)](https://ocfl.io/0.1/spec/) specification

## Tests

```
pytest -s -vv
```

## Installation

**Note:** Pre-package installations instructions, assuming clone of repository and running python shell from cloned directory.  Once packaged, will be more along the lines of `from pyocfl import *` from anywhere.

Install dependencies:
```
pip install -r requirements.txt
```

## Use as Python library

Load pyocfl library:
```
from pyocfl import *
```


### Create new OCFL Storage Root

Initialize and create a new [OCFL Storage Root](https://ocfl.io/0.1/spec/#storage-root) instance at `test_data/goober`, with pre-configured [pairtree storage](https://confluence.ucop.edu/display/Curation/PairTree) confirugation:
```
sr = OCFLStorageRoot('test_data/goober', storage='storage_pair_tree')
sr.new()
```

Verify `test_data/goober` is an OCFL Storage Root:
```
In [7]: sr.verify_dec()                                
namaste - directory type ocfl - version 1.0
Out[7]: True
```


### Create new OCFL Object

To test the creation of an [OCFL Object](https://ocfl.io/0.1/spec/#object-spec), copy an example from `test_data/fixtures` to `test_data` that can be used here (FWIW, works in python shell, but recommended from actual OS environment):
```
cp -r test_data/fixtures/raw_objs/raw_obj1 test_data/
```

A tree view of this "raw" directory should look like the following:
```
test_data/raw_obj1
├── foo.xml
└── level1
    └── level2
        └── bar.txt

2 directories, 2 files
```

Now, we can convert that "raw" directory of files into an OCFL Object back in the python environement:
```
# init OCFLObject instancd with path of "raw" directory
obj = OCFLObject('test_data/raw_obj1/')

# verify NOT yet an OCFL Object
obj.is_ocfl_object()

# run .new() method to convert to OCFL Object
obj.new()

# verify now an OCFL Object
obj.is_ocfl_object()
```

A tree view of the directory at `test_data/raw_obj1` should now look like the following:
```
test_data/raw_obj1/
├── 0=ocfl_object_1.0
├── inventory.json
├── inventory.json.md5
└── v1
    ├── content
    │   ├── foo.xml
    │   └── level1
    │       └── level2
    │           └── bar.txt
    ├── inventory.json
    └── inventory.json.md5
```

Before we add the object to our Storage Root instance `sr`, a tree view of the Storage Root at `test_data/goober` should look like:
```
test_data/goober
├── 0=ocfl_1.0
└── 1=storage_pair_tree
```

Now, we can add this object to the storage root using a storage root method, `add_object` and provide an identifier `ocfl_obj1` (or, we could modify the `id` attribute of the object's `inventory.json`):
```
sr.add_object(obj, target_id='ocfl_obj1')
```

After that object has been added, the Storage Root should now look like:
```
test_data/goober/
├── 0=ocfl_1.0
├── 1=storage_pair_tree
└── 51
    └── 78
        └── 15
            └── a5
                └── 04
                    └── 46
                        └── ac
                            └── 68
                                └── 9c
                                    └── 54
                                        └── f4
                                            └── a0
                                                └── 86
                                                    └── 0f
                                                        └── 77
                                                            └── f1
                                                                └── 517815a50446ac689c54f4a0860f77f1
                                                                    ├── 0=ocfl_object_1.0
                                                                    ├── inventory.json
                                                                    ├── inventory.json.md5
                                                                    └── v1
                                                                        ├── content
                                                                        │   ├── foo.xml
                                                                        │   └── level1
                                                                        │       └── level2
                                                                        │           └── bar.txt
                                                                        ├── inventory.json
                                                                        └── inventory.json.md5
```

Notice the pairtree storage of the identifier `517815a50446ac689c54f4a0860f77f1`, which is an md5 hash of the `ocfl_obj1` identifier we gave the object, and is a result of initiating the Storage Root with the storage engine `storage_pair_tree`.  Had we done `storage_simple`, the structure would not contain this pairtree storage, but would be:

```
test_data/goober/
├── 0=ocfl_1.0
├── 1=storage_pair_tree
└── 517815a50446ac689c54f4a0860f77f1
    ├── 0=ocfl_object_1.0
    ├── inventory.json
    ├── inventory.json.md5
    └── v1
        ├── content
        │   ├── foo.xml
        │   └── level1
        │       └── level2
        │           └── bar.txt
        ├── inventory.json
        └── inventory.json.md5
```

Before proceeding, we can view the object's `inventory.json` using methods from the object's `OCFLObjectInventory` instance:
```
In [24]: obj.object_inventory.inventory                             
Out[24]: 
{'digestAlgorithm': 'md5',
 'head': 'v1',
 'id': 'ocfl_obj1',
 'manifest': {'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml']},
 'type': 'Object',
 'versions': {'v1': {'created': '2018-12-17T10:01:55Z',
   'message': None,
   'state': {'c4b8393f8fdb92998370f404e8f7cbfe': ['level1/level2/bar.txt'],
    'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['foo.xml']}}}}
```

### Object Versioning and Checkout

Noting that our example object has a `v1` directory, indicating a `v1` version, let's create a slightly different `v2` version.

From the OS, copy the `v1` directory and add a small text file:
```
# copy v1 to v2
cp -r test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1/v1 test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1/v2

# create a small text file
echo "The little duck, that had been given whiskey, was now on his legs, unsteady legs." > test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1/v2/content/duck.txt
```

Looking a tree of just the OCFL Object directory, we can see 1) the two versions of this object, and 2) the newly created `duck.txt` file:

```
test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1/
├── 0=ocfl_object_1.0
├── inventory.json
├── inventory.json.md5
├── v1
│   ├── content
│   │   ├── foo.xml
│   │   └── level1
│   │       └── level2
│   │           └── bar.txt
│   ├── inventory.json
│   └── inventory.json.md5
└── v2
    ├── content
    │   ├── duck.txt
    │   ├── foo.xml
    │   └── level1
    │       └── level2
    │           └── bar.txt
    ├── inventory.json
    └── inventory.json.md5
```

**Note:** The files from `v1`, `foo.xml` and `level1/level2/bar.txt` are present in both versions.  This will be important later.

Perhaps we also pause to reflect that typing pairtree directory structures by hand is not fun (though tab completion helps and is encouraged).  Thankfully, we can use the origianl identifier of the Object we created to select it.  And, then, reconcile this new `v2` version we just created.

Back from the python shell, let's load the Storage Root and Object if the shell had been closed and/or to demonstrate retrieving pre-made Storage Roots and Objects
```
# get Storage Root
sr = OCFLStorageRoot('test_data/goober')

# using .get_object method, retriev our original object by its identifier 'ocfl_obj1'
obj = sr.get_object('ocfl_obj1')

# verify by id and path
In [27]: obj.id                             
Out[27]: 'ocfl_obj1'

In [28]: obj.path                     
Out[28]: 'test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1'
```

Now, we've created a `v2` instance outside of the OCFL context and we need to update the object's inventory and files.  

```
obj.update()
```

Now, if we look at the tree, we might be surprised to see that some of the files we previously saw in the `v2` directory are gone:

```
test_data/goober/51/78/15/a5/04/46/ac/68/9c/54/f4/a0/86/0f/77/f1/517815a50446ac689c54f4a0860f77f1/
├── 0=ocfl_object_1.0
├── inventory.json
├── inventory.json.md5
├── v1
│   ├── content
│   │   ├── foo.xml
│   │   └── level1
│   │       └── level2
│   │           └── bar.txt
│   ├── inventory.json
│   └── inventory.json.md5
└── v2
    ├── content
    │   └── duck.txt
    ├── inventory.json
    └── inventory.json.md5
```

What's going on here?  OCFL uses forward-delta versioning ([see this nice discussion about forward-delta versioning](https://journal.code4lib.org/articles/8482#3.3)) to avoid duplication of files in later versions, if they are contained in earlier versions.  To make this work, it's critical that the `inventory.json` file outlines precisely which files should be in each version.  We can observe that `foo.xml` and `level1/level2/bar.txt` are both still attributed to `v2` by looking at the object's inventory:

```
In [30]: obj.object_inventory.inventory                         
Out[30]: 
{'digestAlgorithm': 'md5',
 'head': 'v1',
 'id': 'ocfl_obj1',
 'manifest': {'8201094ab6211cfe632e5948e37e3909': ['v2/content/duck.txt'],
  'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt',
   'v2/content/level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml',
   'v2/content/foo.xml']},
 'type': 'Object',
 'versions': {'v1': {'created': '2018-12-17T10:01:55Z',
   'message': None,
   'state': {'c4b8393f8fdb92998370f404e8f7cbfe': ['level1/level2/bar.txt'],
    'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['foo.xml']}},
  'v2': {'created': '2018-12-17T10:28:01Z',
   'message': None,
   'state': {'8201094ab6211cfe632e5948e37e3909': ['duck.txt'],
    'c4b8393f8fdb92998370f404e8f7cbfe': ['level1/level2/bar.txt'],
    'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['foo.xml']}}}}
```

For a more concise view, we can select only that version from the inventory:
```
In [31]: obj.object_inventory.get_version_entry(2)
Out[31]: 
{'created': '2018-12-17T10:28:01Z',
 'message': None,
 'state': {'8201094ab6211cfe632e5948e37e3909': ['duck.txt'],
  'c4b8393f8fdb92998370f404e8f7cbfe': ['level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['foo.xml']}}
```

So, now that those files are gone from `v2`, how could we "actualize" `v2` on the filesystem?  How can we work with the files from `v2` as they should exist?

To do this, we have to "checkout" a particular version which exports the files as they should exist in that version to a new directory:

```
obj.checkout('test_data/v2_test_checkout', version=2)
```

If we look in the `test_data` directory, hopefully we will see the following at `/test_data/v2_test_checkout`, noting the presence of all files from `v2` that we would expect:

```
test_data/v2_test_checkout/
├── duck.txt
├── foo.xml
└── level1
    └── level2
        └── bar.txt

2 directories, 3 files
```



