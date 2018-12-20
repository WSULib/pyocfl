# pyocfl
Python 3.x client for the [Oxford Common Filesystem Layout (OCFL)](https://ocfl.io/0.1/spec/) specification

## Tests

```
pytest -s -vv
```

## Installation

> **Note:** These instructions are pre-deployment to PyPI

Clone repository and change into directory:

```
git clone https://github.com/wsulib/pyocfl
cd pyocfl
```

Install pyocfl as module:

```
pip install -e .
```

Install additional dependencies:
```
pip install -r requirements.txt
```


## Use as Python library

Load pyocfl library:
```
from pyocfl.pyocfl import *
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

Back from the python shell, let's load the Storage Root and Object if the shell had been closed and/or to demonstrate retrieving pre-made Storage Roots and Objects:

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

### Listing Objects from Storage Root

Initialize a generator of all objects from a Storage Root:

```
# as OCFLObject instances
objs_gen = sr.get_objects()

In [16]: list(objs_gen)                           
namaste - directory type ocfl_object - version 1.0
namaste - directory type ocfl_object - version 1.0
namaste - directory type ocfl_object - version 1.0
namaste - directory type ocfl_object - version 1.0
namaste - directory type ocfl_object - version 1.0
Out[16]: 
[<pyocfl.OCFLObject at 0x111f4d128>,
 <pyocfl.OCFLObject at 0x111f6abe0>,
 <pyocfl.OCFLObject at 0x1107827f0>,
 <pyocfl.OCFLObject at 0x11079e668>,
 <pyocfl.OCFLObject at 0x1107a3208>]

# as full filesystem paths to objects
objs_gen = sr.get_objects(as_ocfl_objects=False)

In [14]: list(objs_gen)                                      
Out[14]: 
['test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/60/a5/f0/21/cf/42/e8/0c/36/7d/71/ff/29/70/e0/aa/60a5f021cf42e80c367d71ff2970e0aa',
 'test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/fc/f8/09/84/2d/d4/c3/7d/83/48/ca/c5/af/7a/53/63/fcf809842dd4c37d8348cac5af7a5363',
 'test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/1f/ac/3b/ae/b4/29/6e/01/99/61/f1/25/49/44/f5/ab/1fac3baeb4296e019961f1254944f5ab',
 'test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/39/f7/f3/88/10/21/58/10/d5/ed/6c/4f/b4/f9/8c/d2/39f7f38810215810d5ed6c4fb4f98cd2',
 'test_data/test_fe89db792da94587a190b2677984fde0/sr_bac0c73b10654e4bad1a5e7cda3d149e/d5/17/d6/a7/d0/bf/e0/68/f6/17/c0/64/6d/69/8a/d4/d517d6a7d0bfe068f617c0646d698ad4']
```

Unlike `sr.get_object()` which is tailored for each storage engine, for simplicity's sake, [pathlib](https://docs.python.org/3.5/library/pathlib.html) and [glob](https://docs.python.org/3.5/library/glob.html) modules are used to locate and return objects from within a Storage Engine.  However, there exists considerable room for customizing how this retrieval and return might function, particularly when the storage engine is known (e.g. simple, pairtree, etc.).


### Fixity Checking/Setting

OCFL supports storing fixity digests in the `inventory.json` under `fixity`.

#### Object Fixity

To **calculate** and **write** fixity for an object, use the `calc_fixity` method:

```
# pre-loaded OCFL object, obj
obj.calc_fixity()

Out[18]: 
{'md5': {'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml']}}
```

Looking at the `inventory.json` for this file, we see the `fixity` segment has been added:

```
{'digestAlgorithm': 'md5',
 'fixity': {'md5': {'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
   'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml']}},
 'head': 'v1',
 'id': 'raw_obj1',
 'manifest': {'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml']},
 'type': 'Object',
 'versions': {'v1': {'created': '2018-12-17T12:16:28Z',
   'message': None,
   'state': {'c4b8393f8fdb92998370f404e8f7cbfe': ['level1/level2/bar.txt'],
    'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['foo.xml']}}}}
```

Running `calc_fixity` with no arguments:

  1. uses the fixity algorithm configured for the object at `self.fixity_algo`
  2. writes to `inventory.json` and updates all inventory digests

However, we can pass other arguments as well:

```
# use pre-calculated digests from manifest
'''
pro: faster, no digest re-calculation needed
con: limited to algorithm from digestAlgorithm, manifest cannot be stale
'''
obj.calc_fixity()

# provide another algorithm to use
'''
Unlike manifests, fixity digests are saved separately for each algorithm run.
'''
obj.calc_fixity(fixity_algo='sha512')
```

We can see an example of multiple fixity digest algorithms saved:

```
{'md5': {'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
  'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml']},
 'sha512': {'66f05321727c50ab2d95735b552cb87880a30f3f74b8ad8b4f796216fb45455f0a185806fd4e09fd5f02990e11ffad8f7566cd999561baf70686a61a92536f54': ['v1/content/foo.xml'],
  'e970d166302e4c7871bb7d109a6a48419e1878e5b0eb2d4f01fd8ba1273884817bfd549f0b6664e5004852b1bbe7f3cd4a9dc49cee2b76ec988220630338762a': ['v1/content/level1/level2/bar.txt']}}
```

To **check** fixity for an object, use the `check_fixity` method:

```
# a True result indicates previously stored fixity digests are consistent with calculated digests
obj.check_fixity()

Out[24]: True
```

If a file has changed for whatever reason between updates to the `fixity` segment in `inventory.json`, this will be revealed in the output:

```
# content for foo.xml was altered before running
obj.check_fixity()

Out[27]: {'cacaa052d4f1ebf6dd0f2cd99ad698d0': [['v1/content/foo.xml']]}

# same for other algorithms saved
obj.check_fixity(fixity_algo='sha512')

Out[28]: {'66f05321727c50ab2d95735b552cb87880a30f3f74b8ad8b4f796216fb45455f0a185806fd4e09fd5f02990e11ffad8f7566cd999561baf70686a61a92536f54': [['v1/content/foo.xml']]}
```

If we are comfortable with the digests that are calculated by necessity for the manifest, we can use those to set and check fixity:

```
obj.calc_fixity(use_manifest_digest=True)
obj.check_fixity(use_manifest_digest=True)
```


#### Storage Root Fixity

We can do some of this work at the Storage Root level as well.

To **calculate** fixity for all objects in Storage Root:

```
# defaults
sr.calc_fixity()

# pass arguments similar to object context
sr.calc_fixity(fixity_algo='sha512')
```

To **check** fixity for all objects:

```
# defaults
sr.check_fixity()

# pass arguments similar to object context
sr.calc_fixity(fixity_algo='sha512')
```

### Object Storage Verification

It's conceivable that Objects will exist within the confines of a Storage Root, but at a filesystem location that does not match the storage engine for that Storage Root.  This might happen for a variety of reasons:

  1. created in other storage root, moved without going through pyocfl `OCFLStorageRoot.add_object`
  2. storage engine of Storage Root changes "underneath" objects
  3. a "raw" directory is initialized as an Object within a pre-existing Storage Root

Take the following Storage Root, with a single Object with the `id` of `food`:

```
.
├── 0=ocfl_1.0
├── 1=storage_pair_tree
└── 62506be34d574da4a0d158a67253ea99
    ├── 0=ocfl_object_1.0
    ├── inventory.json
    ├── inventory.json.md5
    └── v1
        ├── content
        │   ├── bread.txt
        │   ├── meat.txt
        │   └── water.txt
        ├── inventory.json
        └── inventory.json.md5
```

We can see from the `1=` file that the storage engine for this Storage Root is `storage_pair_tree`.  If we load this Storage Root with pyocfl, we can confirm this:

```
sr = OCFLStorageRoot('/tmp/baskets/')
sr.storage                  
Out[6]: 'storage_pair_tree'
```

However, Object `food` is a single, "simple" directory at the root of the Storage Root, not down the pair tree it should be.

One way to uncover these kind of mis-stored objects would be to iterate through *all* OCFL Objects found under the Storage Root, regardless of proper storage:

```
# objects is shorthand for generator returned by sr.get_objects()
for obj in sr.objects:
  print (obj.id, obj.path, obj.storage_id, obj.storage_path)

Out: food 62506be34d574da4a0d158a67253ea99 62506be34d574da4a0d158a67253ea99 62/50/6b/e3/4d/57/4d/a4/a0/d1/58/a6/72/53/ea/99/62506be34d574da4a0d158a67253ea99
```

An Object's `storage_path` attribute is based on the location and storage engine of its associated Storage Root.  As we can see from the print statement above, this Storage Root would expect an Object with `id` == `food` to be at `62/50/6b/e3/4d/57/4d/a4/a0/d1/58/a6/72/53/ea/99/62506be34d574da4a0d158a67253ea99` relative to the Storage Root (and with `md5` set as the storage algorithm set).

We can more quickly determine this with an Object's built-in `verify_storage` method:

```
obj.verify_storage()
Out[9]: False
```

And, we can "fix" the storage location using the complimentary method, `fix_storage`:

```
obj.fix_storage()
```

Which results in the following directory structure for this example Storage Root, where all objects are at the expected storage location:

```
.
├── 0=ocfl_1.0
├── 1=storage_pair_tree
└── 62
    └── 50
        └── 6b
            └── e3
                └── 4d
                    └── 57
                        └── 4d
                            └── a4
                                └── a0
                                    └── d1
                                        └── 58
                                            └── a6
                                                └── 72
                                                    └── 53
                                                        └── ea
                                                            └── 99
                                                                └── 62506be34d574da4a0d158a67253ea99
                                                                    ├── 0=ocfl_object_1.0
                                                                    ├── inventory.json
                                                                    ├── inventory.json.md5
                                                                    └── v1
                                                                        ├── content
                                                                        │   ├── bread.txt
                                                                        │   ├── meat.txt
                                                                        │   └── water.txt
                                                                        ├── inventory.json
                                                                        └── inventory.json.md5
```

