
import argparse
import logging
import sys
import os

from pyocfl import *

# logging levels
LOGGING_LEVEL = logging.ERROR
logging.getLogger('parso.python.diff').disabled = True
logging.getLogger('parso.cache').disabled = True
logger = logging.getLogger(__name__)
logging.getLogger('pyocfl').setLevel(LOGGING_LEVEL)
logger.setLevel(LOGGING_LEVEL)


def ls(args):

	'''
	OS cmd to support listing of Objects from Storage Root
	'''

	# init OCFLStorageRoot instance
	if args.args == []:
		logger.debug('listing StorageRoot Objects @ .')
		sr = OCFLStorageRoot('.')
	elif len(args.args) == 1:
		target_sr = args.args[0]
		logger.debug('listing StorageRoot Objects @ %s' % target_sr)
		sr = OCFLStorageRoot(target_sr)

	# confirm storage root
	if not sr.verify_dec():
		raise Exception('%s does not appear to be an OCFL Storage Root' % sr.path)

	# stdout
	# if ids flag set, init OCFLObject and return id
	if args.ids:
		for obj in sr.get_objects(as_ocfl_objects=True):
			print(obj.id)
	# default to returning object paths
	else:
		for obj_path in sr.get_objects(as_ocfl_objects=False):
			print(obj_path)


def cd(args):

	'''
	OS cmd to support changing directory to Object
	'''

	# init OCFLStorageRoot instance
	sr = OCFLStorageRoot(args.storage_root)

	# identifier
	obj_id = args.args[0]

	# get path of identifier
	obj = sr.get_object(obj_id)

	# if obj exists, jump to path
	if obj:
		print(obj.full_path)
	# else, raise exception
	else:
		raise Exception('OCFL Object could not be found for identifier: %s' % obj_id)


def mv(args):

	'''
	OS cmd to support moving Objects
	'''

	pass


def tree(args):

	'''
	OS cmd to print tree of Object
	'''

	pass


# command map
cmd_map = {
	'ls':ls,
	'cd':cd,
	'mv':mv,
	'tree':tree
}


def main():

	# init parser
	parser = argparse.ArgumentParser()

	# capture commands and args
	parser.add_argument('cmd', action='store', help='command', choices=cmd_map.keys())
	parser.add_argument('args', nargs='*', help='arguments')

	# capture target storage root
	parser.add_argument('-sr', '--storage_root', action='store', default='.', required=False, help='set storage root, if not ./')

	# ls
	parser.add_argument('--ids', action='store_true', required=False)

	# parse args
	args = parser.parse_args()
	logger.debug(args)

	# execute function
	func = cmd_map.get(args.cmd)
	if func:
		func(args)
	elif not func:
		raise Exception('%s not a valid pyocfl_bin command')

	# close stdout and stderr
	sys.stderr.close()
	sys.stdout.close()


if __name__ == '__main__':
	main()