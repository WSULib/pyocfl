
from distutils.dir_util import copy_tree
import uuid

from pyocfl import *



def scaffold_demo_data(storage='storage_simple'):

	'''
	Convenience function to scaffold demo dir at ./test_data/test_UNIQUE_ID
	'''

	demo_id = uuid.uuid4().hex
	demo_dir = os.path.join('test_data','test_%s' % demo_id)

	# make demo working dir
	os.makedirs(demo_dir)

	# copy demo fixtures
	os.makedirs(os.path.join(demo_dir,'fixtures'))
	copy_tree('test_data/fixtures', os.path.join(demo_dir,'fixtures'))

	# init NEW simple sr
	sr = OCFLStorageRoot('%s/sr_%s' % (demo_dir, uuid.uuid4().hex),
		storage=storage)
	sr.new(
		dec_readme='This is a test Storage Root',
		storage_readme='Storage type is: %s' % storage
	)

	# load raw directory and convert to OCFL obj
	obj = OCFLObject(os.path.join(demo_dir,'fixtures/raw_objs/raw_obj1'))
	obj.new()

	# add to storage root
	sr.add_object(obj)

	# return
	return (demo_dir, sr, obj)



# get obj
sr = OCFLStorageRoot('test_data/sr_reconcile')
obj = sr.get_object('c101f4143b954a4891cc15c15e3ab9b7')