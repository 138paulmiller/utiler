#/usr/env python
# Python3
'''
utiler
	Tile Generator Utility
	Useful for importing heightmaps/textures for the UE4 Tile Landscape Importer

See help 
	utiler.py -h 

Note:
	Default Tile Coordinates has Top-Left as origin 
	     +x
	 .----->
	+|
	y|
	 V
	For  all generated tiles Tiles{x}_{y}

github.com/138paulmiller


'''

import sys,math
from PIL import Image

# unreal suggeted landscape tile texture sizes
#	"big": [8129, 8129 ],	
#	"med": [4033, 4033 ],	
#	"small": [2017, 2017 ]


# use Object.__dict__ to dynamically set vals
class Object: pass

class UsageError(Exception):
    def __init__(self, message):
        super().__init__(message)


settings = Object() 
settings.offset = [0, 0]
settings.subdivisions= 1
settings.format_str = "Tile_x{x}_y{y}.png"
settings.flip_y = False # flip horizontal
settings.file_in = None


def set_flip(args):
	settings.flip_y = True	
	return 1

def set_dimen( args):
	option = args[0]
	dimen = int(args[1])
	settings.dimen = dimen,dimen	
	return 2

def set_format( args):
	option = args[0]
	settings.format_str = args[1]
	return 2

def set_subdiv( args):
	option = args[0]
	settings.subdivisions = int(args[1])
	return 2
	
	

def set_offset( args):
	option = args[0]
	if option == '-x':
		i = 0
	elif option == '-y':
		i = 0
	settings.offset[i] = int(args[1])
	return 2

def show_usage(args):
	raise UsageError("Usage")
	
options = {
	'-d' : (set_dimen  , "-d int\n\tSet dimension of output Tile [d, d] }" ), 
	'-f' : (set_format , "-s string \n\tformatted input string. Substututes {x} and {y}. Example Tile_{x}_{y}.png" ), 
	'-x' : (set_offset , "-x int\n\tOsset for {x} argument passed into format" ), 
	'-y' : (set_offset , "-y int\n\tSame as -x, except offsets {y} " ), 
	'-s' : (set_subdiv , "-s int\n\tHow much levels of subdivision " ), 
	'-v' : (set_flip 	,"-v\n\tFlips coordinates such that output tile coordinate system Bottom-Left is origin  " ), 
	'-h' : (show_usage 	,"-h\n\hPrint this menu " ), 

}
	


def parse_args():

	# slice initial arg
	argv = sys.argv[1:]
	argc = len(argv)
	argi = 0
	if argc < 1:
		print("Usage")
		for option in options.keys():
			raise  UsageError("Missing Image File")
		
	settings.file_in = argv[0]

	argi+=1
	while argi < argc:
		option = argv[argi]
		if option in  options.keys():
			argi+=options[option][0](argv[argi:])
		else:
			raise  UsageError(f"Option {option} not found")
		
# 

def execute():

	offset = settings.offset
	src_img = Image.open(settings.file_in)
	#[0... x)
	img_length  = min(src_img.size)
	# resize texture into nearest power of two [0 ... x^2)
	img_length = int(math.pow(2, math.ceil(math.log(img_length)/math.log(2))));
	print(f"New dimens: {img_length},{img_length}")
	src_img = src_img.resize((img_length,img_length) )
	tile_len = int(math.pow(2, settings.subdivisions))
	# splits texture into 
	img_stepx = int(img_length / math.pow(2, settings.subdivisions))
	img_stepy = img_stepx

	tilex = settings.offset[0] 
	tiley = settings.offset[1] 
	endx =  tilex + tile_len 
	endy =  tiley + tile_len  

	if settings.flip_y:
		pixely = img_length;
		img_stepy *= -1
		
	while tiley < endy:
		tilex = settings.offset[0] 
		pixelx = 0;		
		while tilex < endx:
			file_out = settings.format_str.format(x=tilex, y=tiley)	
			new_img = src_img.copy()
			# minx, miny, maxx, maxy in Top-left coord
			if not settings.flip_y:
				region = pixelx, pixely, pixelx+img_stepx, pixely+img_stepy
			else: # so if flipping horiz, swith miny and maxy
				region = pixelx, pixely+img_stepy, pixelx+img_stepx, pixely
			print(f"Creating {file_out} : \nRegion {region}")
			#crop is laxy (may or may not modify orig)
			new_img = new_img.crop(region)
			new_img.resize(settings.dimen)
			new_img.save(file_out)

			tilex+=1
			pixelx+=img_stepx
		tiley+=1
		pixely+=img_stepy

if __name__ == '__main__':
	try:
		parse_args()
		execute()
	except UsageError as e:
		print(e.what()) 
		print('''
			util.py image [option ...]
		''')
		print (f"{option} : options[option][1]")
		sys.exit(1)
