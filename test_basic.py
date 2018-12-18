# unit tests for pyocfl

# standard library
from distutils.dir_util import copy_tree
import os
import pdb
import pytest
import shutil
import uuid

# pyocfl
from pyocfl.pyocfl import *



############################
# Defaults
############################
TESTS_DIR = os.path.join('test_data', 'test_%s' % uuid.uuid4().hex)
TEARDOWN = True



############################
# Setup Module
############################
def setup_module(session):
	print('SETUP...')

	# create tests directory
	print('Creating tests temp directory: %s' % TESTS_DIR)
	os.makedirs(TESTS_DIR)

	# copy raw directories to convert to OCFL Objects
	fixtures_dir = os.path.join(TESTS_DIR,'fixtures')
	os.makedirs(fixtures_dir)
	copy_tree('test_data/fixtures', fixtures_dir)

	# copy existing StorageRoots (sr) for use during testing
	for sr in ['sr1','sr_reconcile']:
		target_dir = os.path.join(TESTS_DIR,sr)
		os.makedirs(target_dir)
		copy_tree(os.path.join('test_data/fixtures',sr), target_dir)



###########################
# Teardown Module
###########################
def teardown_module(session):
	if TEARDOWN:
		print('TEARDOWN...')

		# remove tests directory
		print('Removing directory: %s' % TESTS_DIR)
		shutil.rmtree(TESTS_DIR)



############################
# Tests
############################
class TestOCFLStorageRootCreateLoad(object):

	'''
	Class to test OCFL Storage Root Creation and Loading
	'''

	def test_create_named_sr(self):

		'''
		Test creation of named storage root
		'''

		named_sr = '%s/new_named_storage' % TESTS_DIR

		# init and create
		sr = OCFLStorageRoot(named_sr)
		sr.new()

		# debug
		print('created OCFL Storage Root at %s' % sr.path)

		# assertions
		assert type(sr) == OCFLStorageRoot
		assert sr.path == named_sr
		assert os.path.exists(named_sr)
		assert os.path.isdir(named_sr)
		assert sr.verify_dec()


	def test_create_unnamed_sr(self):

		'''
		Test creation of unnamed storage root,
		expect Exception
		'''

		# init and create
		sr = OCFLStorageRoot()
		with pytest.raises(Exception):
			sr.new()


	def test_load_storage_root_sr1(self):

		'''
		Test loading of pre-made StorageRoot
		'''

		storage_location = '%s/sr1' % TESTS_DIR

		# load storage root
		sr = OCFLStorageRoot(storage_location)

		# assertions
		assert type(sr) == OCFLStorageRoot
		assert sr.path == storage_location
		assert sr.verify_dec()



class TestOCFLObject(object):

	'''
	Class for tests related to OCFL Objects
	'''

	def test_load_nonobj_dir(self):

		# load raw directory to OCFLObject and assert not yet obj
		obj = OCFLObject(os.path.join(TESTS_DIR, 'fixtures/raw_objs/raw_obj1'))
		assert os.path.exists(obj.full_path)
		assert obj.is_ocfl_object() == False


	def test_create_obj(self):

		# load raw directory to OCFLObject and convert
		obj = OCFLObject(os.path.join(TESTS_DIR, 'fixtures/raw_objs/raw_obj1'))

		# create with dec readme and v1 message
		obj.new(
			dec_readme='This is text that will be saved for ocfl_object declaration',
			v1_msg='This message will accompany the v1 version'
		)

		# assert converted to OCFL object
		assert os.path.exists(os.path.join(obj.full_path,'0=ocfl_object_1.0'))
		assert obj.is_ocfl_object() != False
		assert obj.is_ocfl_object()['name'] == 'ocfl_object'


	def test_add_new_obj_to_sr1(self):

		'''
		Test moving of loose OCFLObject to OCFLStorageRoot sr1
		'''

		# load OCFLObject
		obj = OCFLObject(os.path.join(TESTS_DIR, 'fixtures/raw_objs/raw_obj1'))

		# load storage root
		storage_location = '%s/sr1' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# add newly created object
		sr.add_object(obj, 'ocfl_obj1')


	def test_get_obj(self):

		'''
		Test retrieval of object with id only
		'''

		# load storage root
		storage_location = '%s/sr1' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get object
		obj = sr.get_object('ocfl_obj1')

		# assert
		assert obj.is_ocfl_object() != False


	def test_get_obj(self):

		'''
		Test retrieval of object with id only
		'''

		# load storage root
		storage_location = '%s/sr1' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get object
		obj = sr.get_object('ocfl_obj1')

		# assert
		assert obj.is_ocfl_object() != False


	def test_version_details(self):

		'''
		Test version numbers from disk
		'''

		# load storage root
		storage_location = '%s/sr1' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get object
		obj = sr.get_object('ocfl_obj1')

		# check reading of versions from filesystem
		assert obj.get_fs_version_numbers() == [1]

		# check reading of versions from inventory.json
		assert obj.object_inventory.get_version_numbers() == [1]

		# retrieve v1 entry from inventory as int and string
		assert type(obj.object_inventory.get_version_entry(1)) == dict
		assert type(obj.object_inventory.get_version_entry('v1')) == dict


	def test_file_manifest_generation(self):

		'''
		Method to check generation of file manifests from object pre-reconciliation
		'''

		# load reconcile storage root
		storage_location = '%s/sr_reconcile' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get version, but not reconciled object
		obj = sr.get_object('c101f4143b954a4891cc15c15e3ab9b7')

		# check generation of manifests for versions
		assert obj.calc_file_digests([os.path.join(obj.full_path,'v1'),os.path.join(obj.full_path,'v2'),os.path.join(obj.full_path,'v3')]) == {
			'1476bc4456cea62a4ead66b06cdc2344': ['v3/content/foo.xml'],
			'2421f6711a05b350f9cf7d293125f3f3': ['v3/inventory.json'],
			'320422e5c8ad1a4158bc123dec1ce6c0': ['v3/inventory.json.md5'],
			'6f0f992e5d5371f71b1a0614f7b685ea': ['v1/inventory.json.md5'],
			'83928609777e5c2ec3e8de30e138365a': ['v2/inventory.json'],
			'911268b5c64077bbcf4bca1262c2ec9b': ['v3/content/penny.txt'],
			'a389442c959be88eafe7d923d3e2bfdc': ['v1/content/to_be_gone.txt'],
			'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt',
			'v2/content/level100/level200/bar.txt'],
			'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml',
			'v2/content/foo.xml'],
			'ef1d253df340aa7a99896c79c42622fe': ['v2/inventory.json.md5'],
			'fdecf6597c0577ad1daea432e0d4a230': ['v1/inventory.json']
		}


	def test_forward_delta_reconciliation(self):

		'''
		Method to check outcome of forward-delta reconciliation of files
		'''

		# load reconcile storage root
		storage_location = '%s/sr_reconcile' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get version, but not reconciled object
		obj = sr.get_object('c101f4143b954a4891cc15c15e3ab9b7')

		# prepare version paths
		v_paths = [os.path.join(obj.full_path,'v1'),os.path.join(obj.full_path,'v2'),os.path.join(obj.full_path,'v3')]

		# save manifest pre reconciliation
		pre_recon = obj.calc_file_digests(v_paths)

		# run update, which triggers reconciliation
		obj.update()

		# get post reconciliation
		post_recon = obj.calc_file_digests(v_paths)

		# assert different
		assert pre_recon != post_recon

		# assert post looks as expected
		assert post_recon == {'1476bc4456cea62a4ead66b06cdc2344': ['v3/content/foo.xml'],
			'2421f6711a05b350f9cf7d293125f3f3': ['v3/inventory.json'],
			'320422e5c8ad1a4158bc123dec1ce6c0': ['v3/inventory.json.md5'],
			'6f0f992e5d5371f71b1a0614f7b685ea': ['v1/inventory.json.md5'],
			'83928609777e5c2ec3e8de30e138365a': ['v2/inventory.json'],
			'911268b5c64077bbcf4bca1262c2ec9b': ['v3/content/penny.txt'],
			'a389442c959be88eafe7d923d3e2bfdc': ['v1/content/to_be_gone.txt'],
			'c4b8393f8fdb92998370f404e8f7cbfe': ['v1/content/level1/level2/bar.txt'],
			'cacaa052d4f1ebf6dd0f2cd99ad698d0': ['v1/content/foo.xml'],
			'ef1d253df340aa7a99896c79c42622fe': ['v2/inventory.json.md5'],
			'fdecf6597c0577ad1daea432e0d4a230': ['v1/inventory.json']
		}


	def test_version_checkout(self):

		'''
		Check version outputs
		'''

		# load reconcile storage root
		storage_location = '%s/sr_reconcile' % TESTS_DIR
		sr = OCFLStorageRoot(storage_location)

		# get version, but not reconciled object
		obj = sr.get_object('c101f4143b954a4891cc15c15e3ab9b7')

		# make dir for checkouts
		obj_checkouts = '%s/checkouts/%s' % (TESTS_DIR,obj.id)
		os.makedirs(obj_checkouts)

		# checkout v1
		obj.checkout('%s/v1' % (obj_checkouts), version=1)
		assert glob.glob('%s/v1/**/*' % obj_checkouts, recursive=True) == [
			'%s/checkouts/%s/v1/to_be_gone.txt' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v1/foo.xml' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v1/level1' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v1/level1/level2' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v1/level1/level2/bar.txt' % (TESTS_DIR, obj.id)
		]

		# checkout v2
		obj.checkout('%s/v2' % (obj_checkouts), version=2)
		assert glob.glob('%s/v2/**/*' % obj_checkouts, recursive=True) == [
			'%s/checkouts/%s/v2/level100' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v2/foo.xml' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v2/level100/level200' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v2/level100/level200/bar.txt' % (TESTS_DIR, obj.id)
		]

		# checkout v3
		obj.checkout('%s/v3' % (obj_checkouts), version=3)
		assert glob.glob('%s/v3/**/*' % obj_checkouts, recursive=True) == [
			'%s/checkouts/%s/v3/foo.xml' % (TESTS_DIR, obj.id),
			'%s/checkouts/%s/v3/penny.txt' % (TESTS_DIR, obj.id)
		]


































