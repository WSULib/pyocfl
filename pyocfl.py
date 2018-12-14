# pyocfl

# python 3.x standard library modules
import datetime
from distutils.dir_util import copy_tree
import glob
import hashlib
import json
import logging
import os
import pdb
import re
import shutil
import time
import uuid

# 3rd party libraries
import namaste
from pypairtree import pairtree


# setup logger
logging.basicConfig(level=logging.DEBUG)
# parso shims
logging.getLogger('parso.python.diff').disabled = True
logging.getLogger('parso.cache').disabled = True
logger = logging.getLogger(__name__)



# defaults
# storage root
DEFAULT_STORAGE_ROOT_CONFORMANCE = 'ocfl'
DEFAULT_STORAGE_ROOT_VERSION = '1.0'
DEFAULT_STORAGE_ROOT_STORAGE = 'storage_pair_tree' # ['storage_simple','storage_pair_tree']
DEFAULT_STORAGE_ROOT_STORAGE_ID_ALGO = 'md5' # ['md5','sha256','sha512']
# objects
DEFAULT_OBJECT_CONFORMANCE = 'ocfl_object'
DEFAULT_OBJECT_VERSION = '1.0'
DEFAULT_FILE_DIGEST_ALGO = 'md5' # ['md5','sha256','sha512']


class InvalidOCFLObject(Exception):

	pass


class OCFLStorageRoot(object):

	'''
	Class for OCFL Storage Root
	'''

	def __init__(
		self,
		path=None,
		conformance=DEFAULT_STORAGE_ROOT_CONFORMANCE,
		version=DEFAULT_STORAGE_ROOT_VERSION,
		storage=DEFAULT_STORAGE_ROOT_STORAGE,
		storage_id_algo=DEFAULT_STORAGE_ROOT_STORAGE_ID_ALGO,
		auto_load=True):

		self.path = path
		self.conformance = conformance
		self.version = version
		self.storage = storage
		self.storage_id_algo = storage_id_algo

		# clean path
		if self.path != None:
			self.path = self.path.rstrip('/')

		# load pre-existing
		if auto_load and self.path != None and os.path.exists(self.path):
			self.load()


	def __str__(self):
		return 'OCFLStorageRoot: %s, %s_%s' % (self.path, self.conformance, self.version)


	def load(self):

		'''
		Method to load pre-existing StorageRoot

		Args:
			None

		Returns:
			None: reads information from filesystem and sets to self
		'''

		# get storage type
		storage_nam = namaste._get_namaste(self.path, 1)
		if storage_nam != None:
			self.storage = storage_nam[0].split('=')[-1]

		# verify namaste
		self.verify_dec()


	def new(
		self,
		path=None,
		conformance=DEFAULT_STORAGE_ROOT_CONFORMANCE,
		version=DEFAULT_STORAGE_ROOT_VERSION,
		storage=DEFAULT_STORAGE_ROOT_STORAGE,
		storage_id_algo=DEFAULT_STORAGE_ROOT_STORAGE_ID_ALGO,
		dec_readme=None,
		storage_readme=None):

		'''
		Method to create new storage root

		Args:
			path (str): path of storage root to create
			conformance (str): Namaste conformance, ['ocfl']
			version (str): Conformance version, ['1.0']
			storage (str): Storage organization of StorageRoot ['storage_simple','simple_pair_tree']
			storage_id_algo (str): String of hashlib algorithm function, ['md5','sha256','sha512',etc.]
			dec_readme (str): Text to include in the readme of the conformance file, 0= file
			storage_readme (str): Text to include indicated in 1= file
		'''

		# overwrite path if provided
		if path != None:
			self.path = path

		# update instance path
		if self.path == None:
			raise Exception('when creating new StorageRoot, path must be set')

		# check if path exists and is directory
		if os.path.exists(self.path):
			if not os.path.isdir(self.path):
				raise Exception('%s exists and is not a directory')

		# if does not exist, create
		else:
			logger.debug('%s does not exist, creating' % self.path)
			self._create_storage_root(self.path, dec_readme=dec_readme, storage_readme=storage_readme)


	def _create_storage_root(self, path, dec_readme=None, storage_readme=None):

		'''
		Method to create storage location

		Returns:
			None: creates fs directory for new StorageRoot
		'''

		# create path
		os.makedirs(path)

		# write StorageRoot declaration file
		open('%s/0=%s_%s' % (path, self.conformance, self.version), 'w').close()

		# write as optional text file
		if dec_readme is not None:
			with open('%s/%s_%s.txt' % (path, self.conformance, self.version), 'w') as f:
				f.write(dec_readme)

		# write StorageRoot storage file
		open('%s/1=%s' % (path, self.storage), 'w').close()

		# write as optional text file
		if storage_readme is not None:
			with open('%s/%s.txt' % (path, self.storage), 'w') as f:
				f.write(storage_readme)


	def verify_dec(self):

		'''
		Method to verify NAMASTE
		'''

		# retrieve namaste information
		nam_d = namaste.get_types(self.path)

		# compare conformance
		if nam_d.get(self.conformance, False):
			d = nam_d.get(self.conformance)
			nam_d_dec = '%s_%s.%s' % (d['name'],d['major'],d['minor'])

			# compare versions
			return '%s_%s' % (self.conformance,self.version) == nam_d_dec

		else:
			return False


	def add_object(self, ocfl_obj, target_id=None):

		'''
		Method to add OCFLObject to OCFLStorageRoot
			- confirms ocfl_obj is valid ocfl_obj

		NOTE: possibility of post_add hook?

		Args:
			ocfl_obj (pyocfl.OCFLObject): Object instance
			target_id (str): new target id, overwriting what is found in ocfl_obj.id
		'''

		# verify valid ocfl_object
		if not ocfl_obj.is_ocfl_object():
			raise InvalidOCFLObject

		# if new id passed, use
		if target_id != None:

			# set in obj inventory
			ocfl_obj.object_inventory.inventory['id'] = target_id

		# prepare storage id and path
		storage_id = self._calc_storage_id(ocfl_obj.id)
		storage_path = self._calc_storage_path(storage_id)

		# create dir
		os.makedirs(os.path.join(self.path, storage_path))

		# copy material
		copy_tree(ocfl_obj.full_path, os.path.join(self.path, storage_path))

		# finish up
		ocfl_obj.storage_root = self
		ocfl_obj.path = storage_path

		# update
		ocfl_obj.update()


	def get_object(self, obj_input, id_type='id'):

		'''
		Method to calculate path, load and return OCFLObject instance
		'''

		# if id_type is 'id', calc fs path
		if id_type == 'id':

			# prepare storage id and path
			storage_id = self._calc_storage_id(obj_input)
			obj_path = self._calc_storage_path(storage_id)

		# else, set path to provided input
		else:
			obj_path = obj_input

		# create full path
		obj_full_path = os.path.join(self.path, obj_path)

		# check if path exists
		if os.path.exists(obj_full_path) and os.path.isdir(obj_full_path):

			# init OCFLObject and return
			search_obj = OCFLObject(obj_full_path)

			# verify valid ocfl_object
			if not search_obj.is_ocfl_object():
				raise InvalidOCFLObject
			else:
				return search_obj

		else:
			return None


	def move_object(self, ocfl_obj, target_id):

		'''
		Method to move object

		Args:
			ocfl_obj (pyocfl.OCFLObject): Object instance
			target_id (str): new target id
		'''

		# use self.get_object to check if target_it exists
		search_obj = self.get_object(target_id)

		# if content found, raise exception
		if search_obj != None:
			raise Exception('Content found at: %s' % search_obj.path)

		# else, continue
		else:

			# prepare storage id and path
			storage_id = self._calc_storage_id(target_id)
			storage_path = self._calc_storage_path(storage_id)

			# move object
			shutil.move(os.path.join(self.path, self._calc_storage_path(self._calc_storage_id(ocfl_obj.id))), os.path.join(self.path, storage_path))

			# udpate object
			ocfl_obj.path = storage_path
			ocfl_obj.object_inventory.inventory['id'] = target_id

		# update
		ocfl_obj.update()


	def _calc_storage_id(self, obj_id):

		'''
		Method to calculate storage_id from obj_id
		'''

		digest_func = getattr(hashlib, self.storage_id_algo)
		storage_id = digest_func(obj_id.encode('utf-8')).hexdigest()
		logger.debug('digest algo: %s' % digest_func)
		logger.debug('storage_id: %s' % storage_id)

		return storage_id


	def _calc_storage_path(self, storage_id):

		'''
		Method to return relative path of object given storage_id
		'''

		# use appropriate storage engine for Storage Root
		if self.storage == 'storage_simple':

			# return
			return storage_id


		elif self.storage == 'storage_pair_tree':

			# use pypairtree library to generate structure
			return os.path.join(pairtree.toPairTreePath(storage_id), storage_id)

		else:
			raise Exception('"%s" is not a recognized storage engine' % self.storage)



class OCFLObject(object):

	'''
	Class for OCFL Object

	Minmal Example (https://ocfl.io/0.1/spec/#example-minimal-object)
	[object root]
	├── 0=ocfl_object_1.0
	├── inventory.json
	├── inventory.json.sha512
	└── v1
		├── inventory.json
		├── inventory.json.sha512
		└── content
			└── file.txt
	'''

	def __init__(
		self,
		path=None,
		storage_root=None,
		auto_load=True,
		conformance=DEFAULT_OBJECT_CONFORMANCE,
		version=DEFAULT_OBJECT_VERSION,
		file_digest_algo=DEFAULT_FILE_DIGEST_ALGO):

		'''
		Args:
			path (str): path relative to Storage Root
			storage_root (OCFLStorageRoot): instance of Storage Root
				- if storage_root == None, assume self.path is full_path from cwd
			file_digest_algo (str): hashing algorithim, ['md5','sha256','sha512']
		'''

		self.conformance = conformance
		self.version = version

		# update instance path
		if path == None:
			logger.debug('path not provided, creating unique directory')
			self.path = '%s' % (uuid.uuid4().hex)
		else:
			self.path = path

		# set algo
		self.file_digest_algo = file_digest_algo

		# if storage_root is provided
		self.storage_root = storage_root

		# if storage_root is present and auto_load
		if self.full_path != None and auto_load:
			self.parse_object()


	@property
	def id(self):

		'''
		Return id from inventory
		'''

		return self.object_inventory.inventory['id']


	@property
	def full_path(self):

		'''
		Property to return full path based on StorageRoot (if present) and path
		'''

		if self.storage_root != None:
			return os.path.join(self.storage_root.path, self.path)
		else:
			return self.path


	def is_ocfl_object(self):

		'''
		Method to determine if self.path is OCFL Object

		Returns:
			dict / False: Namaste directory type if single present, else False
		'''

		# attempt to read and parse namaste tags
		nam_d = namaste.get_types(self.full_path)

		# single type
		if len(nam_d) == 1:
			nam_d_dec = nam_d[list(nam_d.keys())[0]]
			if nam_d_dec['name'] == 'ocfl_object':
				return nam_d_dec
			else:
				# logger.debug('namaste directory type %s is not ocfl_object' % nam_d_dec)
				return False

		elif len(nam_d) > 1:
			# logger.debug('more than one namaste directory type found for %s' % self.path)
			return False

		elif len(nam_d) == 0:
			# logger.debug('no namaste directory types found for %s' % self.path)
			return False


	def parse_object(self):

		'''
		Method to parse
		'''

		if not (os.path.exists(self.full_path) and os.path.isdir(self.full_path)):
			return None

		# read namaste directory type
		self.nam_d_dec = self.is_ocfl_object()
		if not self.nam_d_dec:
			return None

		# parse inventory
		self._parse_object_inventory()


	def _parse_object_inventory(self):

		'''
		Method to parse path of inventory
		'''

		with open('%s/inventory.json' % self.full_path,'r') as f:
			self.object_inventory = OCFLObjectInventory(inventory=f.read())


	def _list_files(self, path, files_only=False):

		'''
		Method to return generator of recursive files/directories
		'''

		for root, folders, files in os.walk(path):
			if files_only:
				for filename in files:
					yield os.path.join(root, filename)
			else:
				for filename in folders + files:
					yield os.path.join(root, filename)


	def new(self, dec_readme=None, v1_msg=None):

		'''
		Method to create OCFL Object from self.path
		'''

		# confirm not already an OCFL object
		if self.is_ocfl_object():
			raise Exception('%s appears to already be an OCFL object, aborting' % self.path)

		# create temporary v1 dir name
		v1t = uuid.uuid4().hex
		v1t_full = os.path.join(self.full_path, v1t)

		# create v1 directory
		os.makedirs('%s/content' % v1t_full)

		# move current contents to v1 dir, skipping v1t
		for f in os.listdir(self.full_path):
			if f != v1t:
				shutil.move(os.path.join(self.full_path,f), os.path.join(v1t_full,'content'))

		# rename temp v1
		os.rename(v1t_full, os.path.join(self.full_path,'v1'))

		# init inventory and create new
		self.object_inventory = OCFLObjectInventory()
		self.object_inventory.new(**{
				'digestAlgorithm':self.file_digest_algo
			})

		# set v1 message
		self.object_inventory.inventory['versions']['v1']['message'] = v1_msg

		# write Object declaration file
		open('%s/0=%s_%s' % (self.full_path, self.conformance, self.version), 'w').close()

		# write as optional text file
		if dec_readme is not None:
			with open('%s/%s_%s.txt' % (self.full_path, self.conformance, self.version), 'w') as f:
				f.write(dec_readme)

		# finally, run update
		self.update()


	def _calc_file_digest(self, filepath, file_digest_algo=DEFAULT_FILE_DIGEST_ALGO):

		'''
		Method to generate digests for filepath
		'''

		# get file_digest_algo function
		digest_func = getattr(hashlib, file_digest_algo)

		# if file_digest_algo exists, use
		if digest_func != None:

			# init
			digest = digest_func()

			# read file in chunks
			with open(filepath, 'rb') as f:
				for chunk in iter(lambda: f.read(128 * digest.block_size), b''):
					digest.update(chunk)
			return digest.hexdigest()

		else:
			raise Exception('algorithm "%s" is not part of hashlib library' % file_digest_algo)


	def generate_file_manifest(self, path_list, version_state=False):

		'''
		Method to generate digest of files

		Args:
			path_list (list): List of paths to walk and generate digests
			version_state (bool): If True, will remove version paths, resulting in relative manifest
		'''

		# init dictionary to return
		digest_d = {}

		# loop through provided paths
		for path in path_list:

			# strip path
			path = path.rstrip('/')

			# get list of files
			files = self._list_files(path, files_only=True)

			# loop through
			for f in files:

				# calc digest
				digest = self._calc_file_digest(f, file_digest_algo=self.file_digest_algo)

				# if for version, make path relative
				if version_state:
					f = f.replace('%s/' % path, '')
				else:
					f = f.replace('%s/' % self.full_path.rstrip('/'), '')

				# DEBUG
				logger.debug('%s : %s' % (f, digest))

				# add to dictioanry
				if digest not in digest_d:
					digest_d[digest] = [f]
				else:
					digest_d[digest].append(f)

		# return
		return digest_d


	def update(self):

		'''
		Method to update object
			- reconcile versions
				- remove files if not forward-delta
			- udpate inventory meta-digests

		TODO: MUCH of this can be refactored into methods, and replace much from new()
		'''

		# debug
		stime = time.time()

		# write inventories
		self.write_inventories()

		# reconcile deltas
		self.reconcile_deltas()

		# debug
		logger.debug('updated elapsed: %s' % (time.time()-stime))


	def write_inventories(self):


		'''
		Method to wrap the calculation of file digests and writing of inventories
		'''

		# get versions from fs
		fs_versions = self.get_fs_versions()

		# calc object manifest
		self.object_inventory.update_object_manifest(self.generate_file_manifest([ os.path.join(self.full_path,'v%s/content' % v) for v in fs_versions ]))

		# set version state
		for v in fs_versions:
			self.object_inventory.update_version_state(
				'v%s' % v, self.generate_file_manifest([os.path.join(self.full_path,'v%s/content' % v)], version_state=True)
			)

		# write inventory
		with open(os.path.join(self.full_path,'inventory.json'), 'w') as f:
			f.write(json.dumps(self.object_inventory.inventory, sort_keys=True, indent=4))

		# write object inventory digest
		inventory_digest = self._calc_file_digest(os.path.join(self.full_path,'inventory.json'), file_digest_algo=self.file_digest_algo)
		with open(os.path.join(self.full_path,'inventory.json.%s' % self.file_digest_algo), 'w') as f:
			f.write(inventory_digest)

		# write version manifests
		for k,v in self.object_inventory.inventory['versions'].items():

			# create path
			v_inv_path = os.path.join(self.full_path, k, 'inventory.json')

			# write to fs
			with open(v_inv_path, 'w') as f:
				f.write(json.dumps(v, sort_keys=True, indent=4))

			# get and write digest
			v_inventory_digest = self._calc_file_digest(v_inv_path, file_digest_algo=self.file_digest_algo)
			with open('%s.%s' % (v_inv_path, self.file_digest_algo), 'w') as f:
				f.write(v_inventory_digest)


	def reconcile_deltas(self):

		'''
		Method to reconcile forward deltas
			- REQUIRED: inventory.json is current

		Approach:
			- begin with v2, work forwards
		'''

		# get versions from inventory
		v_nums = self.object_inventory.get_version_numbers()

		# if versioned
		if len(v_nums) > 1:

			# pop v1
			v_nums.remove(1)
			logger.debug('baseline set at v1')

			# loop through versions
			for i,v_num in enumerate(v_nums):

				logger.debug('reconcialing v%s' % v_num)

				# get version
				v_dict = self.object_inventory.get_version_entry(v_num)
				logger.debug(v_dict)

				# loop through files in state and check if version ancestor
				for digest,filepath in v_dict['state'].items():

					logger.debug('checking version ancestors for digest: %s' % digest)

					# loop through ancestors
					ancestor_v_nums = list(range(1,v_num))
					# reverse
					ancestor_v_nums.reverse()
					# loop through
					for ancestor_v_num in ancestor_v_nums:

						# get ancestor v_dict
						ancestor_v_dict = self.object_inventory.get_version_entry(ancestor_v_num)

						# check if digest present
						if digest in ancestor_v_dict['state']:
							logger.debug('digest found in v%s' % ancestor_v_num)

							# remove file
							self._remove_files_from_version(v_num, filepath)

							# break loop
							break

		else:
			logger.debug('object contains only single version, skipping forward delta reconciliation')


	def _remove_files_from_version(self, version, filepaths):

		'''
		Method to remove file from version

		Args:
			version (int): version number
			filepaths (list): list of filepaths to remove, often single entry
		'''

		for filepath in filepaths:

			# remove file
			v_filepath = os.path.join(self.full_path, 'v%d/content' % version, filepath)
			logger.debug('REMOVING FILE FROM v%s: %s' % (version, v_filepath))
			os.remove(v_filepath)

			# TODO: remove empty directories


	def get_fs_versions(self):

		'''
		Method to read versions as present on disk (fs)
		'''

		# get version dirs
		v_dirs = glob.glob('%s/v*' % self.full_path)

		# regex to grab version numbers for dirs
		v_num_regex = re.compile(r'.+?/v([0-9]+$)')

		# comprehend and return
		return [ int(re.match(v_num_regex, v_dir).group(1)) for v_dir in v_dirs ]



class OCFLObjectInventory(object):

	'''
	Class for OCFL Object Inventory
	'''

	def __init__(
		self,
		inventory=None):

		# parse passed inventory
		if inventory != None:
			if type(inventory) == str:
				self.inventory = json.loads(inventory)
			elif type(inventory) == dict:
				self.inventory = inventory
			else:
				raise Exception('JSON or python dictionary required when passed as inventory')


	def new(self,**kwargs):

		'''
		Method to create JSON object inventory
		'''

		# OCFL Object inventory scaffold
		self.inventory = {
			'digestAlgorithm':DEFAULT_FILE_DIGEST_ALGO,
			'head':'v1',
			'id':uuid.uuid4().hex,
			'manifest':{},
			'type':'Object',
			'versions':{
				'v1':{
					'created':'{:%Y-%m-%dT%H:%M:%SZ}'.format(datetime.datetime.now()),
					'message':None,
					'state':{}
				}
			}
		}

		# update with kwargs
		self.inventory.update(kwargs)

		# return
		return self.inventory


	def update_object_manifest(self, digest_d):

		'''
		Method to update object manfiest with passed dictionary of digests
		'''

		self.inventory['manifest'] = digest_d


	def update_version_state(self, version, digest_d):

		'''
		Method to update version state with passed dictionary of digests
		'''

		if version in self.inventory['versions']:
			self.inventory['versions'][version]['state'] = digest_d

		else:
			self.inventory['versions'][version] = {
				'created':'{:%Y-%m-%dT%H:%M:%SZ}'.format(datetime.datetime.now()),
				'message':None,
				'state':digest_d
			}


	def get_version_numbers(self):

		'''
		Convenience method to return version numbersd
		'''

		return [ int(v.split('v')[-1]) for v in self.inventory['versions'].keys() ]



	def get_version_entry(self, version):

		'''
		Convenience function to return version entry
		'''

		# handle int or strings
		if type(version) == int:
			v_key = 'v%s' % version
		elif type(version) == str:
			v_key = version

		if v_key in self.inventory['versions']:
			return self.inventory['versions'][v_key]
		else:
			return None



































