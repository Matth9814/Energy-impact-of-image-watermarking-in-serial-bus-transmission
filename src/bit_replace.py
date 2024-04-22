from header import np
from func import vector2image,image2vector,vector2bitstr

def embedBitReplace(cover:np.ndarray, secret:np.ndarray|str, stype:str='img', bit:int=0, interval:int=1) -> tuple[np.ndarray,int]:
	u"""Embed secret information into cover image by replacing some bits.\n
	Parameters:
		cover   		: original image (2 dimension np.ndarray)
		secret  		: watermark
		stype			: secret type can be 'img' or 'str' (pixels type has to be uint8)
		bit     		: replaced bit (0-7) inside the modified bytes (It's recommended to use a bit close to the LSB [bit=0])
		interval		: modified bytes stride\n
	Returns:
		stego   		: watermarked image (2 dimension np.ndarray)
		secret_length	: length of the embedded secret in bytes
	"""

	if stype not in ('img','str'):
		raise Exception('Secret has to be either an image or a string')
	elif stype == 'img':
		if(secret.dtype != np.uint8):
			raise TypeError('Secret image pixels have to be encoded as uint8')
		secr = image2vector(secret)
	else: #stype == 'str'
		secr = bytearray(secret,'utf-8')
		
	# Record secret length
	secret_length = len(secr)

	# Turn secret into bit string
	secr = vector2bitstr(secr)
	
	# Image dimensions
	height = cover.shape[0]
	width  = cover.shape[1]
	
	# Check embedded sequence length against the image length
	if height*width < (len(secr)*interval):
		raise Exception("Secret information exceeds the image capacity. Please review the cover image, the secret information or the interval")

	# "interval" is basically a stride
	# If interval=0 then the secret is embedded in consecutive bytes
	# If interval=1 the secret is embedded every 2 bytes (yes, no, yes, no...) 
	
	cover = image2vector(cover)
	
	for i in range(len(secr)):
		# LSB --> bit=0
		# The watermark image bit is inserted in place of the chosen bit
		sindex = i*interval
		if int(secr[i]) == 1:
			cover[sindex] = np.bitwise_or(cover[sindex],(1 << bit))
		else: #0
			cover[sindex] = np.bitwise_and(cover[sindex],~(1 << bit))
		
	stego = vector2image(cover, height, width)

	return stego, secret_length

def extractBitReplace(stego:np.ndarray, secret_length:int, bit:int=0, interval:int=1) -> np.ndarray:
	u"""Extract the secret information embedded in the image.\n
	Parameters:
		stego			: watermarked image (2 dimension np.ndarray)
		secret_length	: length of secret information in bytes
		bit           	: replaced bit (0-7) inside the modified bytes 
		interval	   	: modified bytes stride
	Returns:
		secret        	: extracted secret information as bytearray
	"""

	bit_length = secret_length*8 # bit of the secret
	secret = np.zeros(secret_length,dtype=np.uint8)
	mod_image = image2vector(stego)
	
	tmp_byte = ""
	sindex = 0
	for i in range(bit_length):
		tmp_byte += str((mod_image[i*interval] & (1 << bit)) >> bit)
		if((i+1)%8 == 0 and i != 0):
			secret[sindex] = int(tmp_byte,base=2)
			#print(f"Extracted: {secret[sindex]}")
			sindex += 1
			tmp_byte = ""
			
	return secret
