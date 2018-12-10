# unit tests for pyocfl

# standard library
from distutils.dir_util import copy_tree
import os
import pdb
import pytest
import shutil
import uuid

# pyocfl
from pyocfl import *



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
	for sr in ['sr1']:
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

























