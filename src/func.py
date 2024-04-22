from header import np,plt,cv,os,WM_TYPES

def energyConsumption(img:np.ndarray) -> np.uint32:
    """Compute the energy consumption as number of transitions
    for an image transmitted over a serial line. The image is considered
    to be sent starting from the first pixel of channel 0 in row-major order.\n
    Parameters:
        img: image whose energy conumption needs to be computed
    Returns:
        energyCons: energy consumption of the transmission
    """

    energyCons = np.uint32(0)
    for ch in range(img.shape[2]):
        vectr_img = image2vector(img[:,:,ch])
        vectr_img = vector2bitstr(vectr_img)
        i = 0

        #print(f"First pixel [ch:{ch}]: {tmp_vectr_img[i]}")
        #print(f"First bit [ch:{ch}]: {vectr_img[i]}")

        # The first pixel is checked against the last pixel of the previous channel
        if ch: # Not the first channel sent
            if(vectr_img[i] != last_pixel):
                energyCons += 1 # Transition detected
        
        while i < (len(vectr_img)-1):
            if(vectr_img[i] != vectr_img[i+1]):
                energyCons += 1 # Transition detected
            i += 1

        last_pixel = vectr_img[i] # Update last_pixel
        #print(f"Last bit [ch:{ch}]: {last_pixel}")
        #print(f"En. consumption after channel {ch}: {energyCons}")

    return energyCons

def image2vector(img:np.ndarray) -> np.ndarray:
	return img.flatten() # Flattened in row-major by default

def vector2image(vector:np.ndarray, row:int, col:int) -> np.ndarray:
	return np.reshape(vector, (row, col))

def vector2bitstr(array:np.ndarray|bytearray) -> str:
	""" Convert a sequence of bytes into a string o bits """
	secr = [format(i,"08b") for i in array] 
	secr = ''.join(secr)
	return secr

def imgsPlot(imgs:list,img_titles:list,plot_title:str):
    """ Plot passed images in a (1,len(imgs)) subplot\n 
    Parameters:
        imgs: images to plot
        img_titles: images titles
        plot_title: plot title
    """
    fig, axs = plt.subplots(1,len(imgs))
    fig.suptitle(plot_title)
    for i in range(len(imgs)):
        print(f"{img_titles[i]} shape: {imgs[i].shape}")
        axs[i].imshow(cv.cvtColor(imgs[i],cv.COLOR_BGR2RGB))
        axs[i].set_title(img_titles[i])
        axs[i].axis("off")

def minimumImageDimension(img_dir:str) -> np.uint32:
	"""Select the smallest image (on a single channel) for the given set of images\n
    Paramters:
        img_dir	: the directory containing the images the watermark has to be embedded\
		into (pixels have to encoded unsigned bytes, e.g. uint8)
    Returns:
        minB	: smallest image size in bytes
    """

	# Max number of bytes that can be embedded (uin32 is enough to cover the case of 8k images)
	minB = np.uint32(np.iinfo(np.uint32).max)
	for img in os.listdir(img_dir):
		img_path = img_dir + img
		img = cv.imread(img_path, cv.IMREAD_COLOR)
		imgB = img.shape[0]*img.shape[1]
		if(minB > imgB):
			minB = imgB
	return minB

def sameImg(img1:np.ndarray,img2:np.ndarray) -> bool:
    return np.array_equal(img1,img2,equal_nan=False)

def sameWm(wm1:np.ndarray|str,wm2:np.ndarray|str,mode:str='img') -> bool:
    if mode not in WM_TYPES:
        raise Exception('The watermark has to be either an image or a string')
    elif mode == 'img':
        ret = sameImg(wm1,wm2)
    else:
        ret = (wm1 == wm2)
    return ret