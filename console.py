
from distutils.dir_util import copy_tree
import uuid

from pyocfl import *



def scaffold_demo_data(storage='storage_pair_tree'):

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

	# load raw directories and convert to OCFL objects
	objs = []
	for d in os.listdir(os.path.join(demo_dir,'fixtures/raw_objs')):
		obj = OCFLObject(os.path.join(demo_dir,'fixtures/raw_objs',d))
		obj.new()

		# add to storage root
		sr.add_object(obj,d)

		# append
		objs.append(obj)

	# return
	return (demo_dir, sr, objs)



