from header import *
from bit_replace import embedBitReplace,extractBitReplace
from func import image2vector,vector2image,energyConsumption,imgsPlot,minimumImageDimension,sameImg,sameWm
from blind_watermark import WaterMark,bw_notes
bw_notes.close() # Suppress BW welcome note
from imwatermark import WatermarkEncoder,WatermarkDecoder

# Data recording variables
Imgarr = []
BaseImgarr_enCons = []
BRarr_enCons = []
BWarr_enCons = []
IWarr_enCons = []

if __name__ == "__main__":
    
    ##### WATERMARK SETUP #####
    # NOTE: even though some of the used wm algorithms have a bigger
    # capacity the wm dimension is defined as the minium one between the
    # maximum dimension allowed by each algorithm. 
    # This is done to keep the comparison fair.
    if WM_SIZE_COMP:
        # The function takes 3.5 seconds for ~100 images but it may be convenient
        # to run it just one time ad annotate the returned size for large datasets
        # Constants can be found in "header.py"
        # Check the size of the smallest image in the selected dataset
        minB = minimumImageDimension(IMGS_PATH)/517.815
        # Bit Replacement: 1 bit in 1 Byte --> minB/8
        # Blind wm: max wm dim is lower than --> [i/(2+4) for i in img_shape] --> img_shape[0]*img_shape[1]
        #   Since both dimensions are divided by 8 --> minB/64 (-1)
        # Invisible wm (dwtDctSvd): max dim --> floor{img_shape[0]*img_shape[1]/517.815}
        #   Even though i couldn't find the reason why this ratio needs to be respected I know
        #   it is independent from the specific watermark used
        
        # NOTE: the minimum image dimension for the 'dwtDctSvd' algorithm of the Invisible Watermark
        # library is 256x256=65536 bytes

        # NOTE: the maximum wm dimension for the Blind Watermark DCT+SVD algorithm currently depends
        # only on the size of the image the wm is embedded into since the block division cannot be changed

        print(f"Maximum watermark size: {floor(minB)} bytes")
        print("NOTE: Remember to store the maximum watermark dimension in WM_BSIZE \"header.py\"")
        print("      Change also WM_DIM in case images are used as watermark")

        if WM_TYPE =='img':
            print("Resizing image...")
            wm_size = floor(minB**0.5)
            # The original watermark is resized only when the maximum size is recomputed
            # In the wm algorithms energy benchmark the resized version is used
            wm = cv.imread(WM_PATH+WM_NAME_FULL,cv.IMREAD_COLOR)
            wm = cv.resize(wm,(wm_size,wm_size))
            resized_wm = f"{WM_NAME}_{wm_size}x{wm_size}.{WM_EXTENSION}"
            cv.imwrite(WM_PATH+resized_wm,wm)
            print(f"Image ready as {resized_wm}")
            # Change WM_DIM macro in header.py 

        exit()
    else:
        minB = WM_BSIZE

    if WM_TYPE not in WM_TYPES:
        raise Exception('The watermark has to be either an image or a string')
    elif WM_TYPE == 'img':
        wm_size = floor(minB**0.5)
        wm = cv.imread(WM_PATH+WM_NAME_RESIZED,cv.IMREAD_GRAYSCALE)
        print(f"Watermark: {WM_NAME_RESIZED}")
        #plt.imshow(wm)
        #plt.show()
        #exit()
    else: # WM_TYPE == 'str'
        wm = WM_STR.replace("\n","")
        wm_size_tmp = len(wm.encode('utf-8'))
        if(wm_size_tmp > WM_BSIZE): # Check watermark length
            print(f"Watermark exceeds maximum capacity [{WM_BSIZE} bytes]\n>Provided: {wm_size_tmp} bytes")
            exit()
        print(f"Watermark: {wm}")

    ##### SIMULATION START #####
    ImgList = os.listdir(IMGS_PATH)
    numImgs = len(ImgList)
    start_time = time.time()
    for numImg,img in enumerate(ImgList):
        #print(img)
        img_path = IMGS_PATH + img
        img_bgr = cv.imread(img_path, cv.IMREAD_COLOR)
        print(f"[{time.time()-start_time:0.5} s] Image: {numImg+1}/{numImgs} [{img}]")
        #print("WM dimensions: {}".format(wm.shape))
        #print("Image dimensions: {}".format(img_bgr.shape))

        #img_rgb = cv.cvtColor(wm,cv.COLOR_BGR2RGB)
        #plt.imshow(img_rgb)
        #plt.show()

        base_enCons = energyConsumption(img_bgr)
        

        Imgarr.append(img)
        BaseImgarr_enCons.append(base_enCons)
        
        ##### BIT REPLACEMENT #####
        
        if BIT_REPLACEMENT:
            
            img_toWm = deepcopy(img_bgr)
            br_wm = deepcopy(wm)
        
            # Embed watermark
            img_toWm[:,:,BRCH], secret_length = embedBitReplace(img_toWm[:,:,BRCH],wm,stype=WM_TYPE,bit=REPLACED_BIT,interval=BYTE_STRIDE)
            
            # Bit Replacement image energy consumption
            BR_enCons = energyConsumption(img_toWm)
            BRarr_enCons.append(BR_enCons)
        
            # Extract watermark
            vctr_wm = extractBitReplace(img_toWm[:,:,BRCH],secret_length,bit=REPLACED_BIT,interval=BYTE_STRIDE)
            
            # Restore wm original shape
            if(WM_TYPE == 'img'):
                br_wm = vector2image(vctr_wm,wm_size,wm_size)
            else:
                vctr_wm = vctr_wm.tobytes().decode('utf-8')

            if DEBUG_BR:
                print(f"Same img: {sameImg(img_bgr,img_toWm)}")
                # Check that the embedded watermark and the extracted one are the same
                issameWm = sameWm(wm,br_wm,mode=WM_TYPE)
                if not issameWm:
                    # Diagnostic
                    if(WM_TYPE == 'img'):
                        tmp_wm = image2vector(wm)
                    else:
                        tmp_wm = wm
                    for i in range(len(wm)): # Only the modified channel is checked
                        if(tmp_wm[i] != vctr_wm[i]):
                            print("Secret bytes are different!")
                            print("> Byte [{}]: [old {}] vs [new {}]".format(i,tmp_wm[i],vctr_wm[i]))
                            break

            #Pylot plot
            if DEBUG_BR:
                titles = ['Original image','Image w/Embedded WM']
                imgs = [img_bgr,img_toWm]
                imgsPlot(imgs,titles,"Images comparison [Bit Repl.]")
                if WM_TYPE == 'img':        
                    titles = ['Original watermark', 'Extracted watermark']
                    imgs = [wm,br_wm]
                    imgsPlot(imgs,titles,"Watermark comparison [Bit Repl.]")
                else:
                    print(f"Original WM: {wm}\nExtracted WM [Bit Repl.]: {br_wm}")

                # Energy consumption
                print(f"Original image energy cons. : {base_enCons}")
                print(f"Watermarked image energy cons. : {BR_enCons}")
                print(f"Energy consumption increase with watermark [Bit Repl.]: {(BR_enCons/base_enCons-1.0):.4}")

    

        ##### DCT and SVD based watermark #####
        if BLIND_WM:
            # Setup
            # 'password_img' and 'password_wm' are used as seeds internally
            bwm = WaterMark(password_img=1,password_wm=1)

            bwm.read_img(img=img_bgr)
            if WM_TYPE == 'img':
                bwm.read_wm(WM_PATH+WM_NAME_RESIZED,mode=WM_TYPE)    # The WM is internally read in grayscale
            else:
                bwm.read_wm(wm,mode=WM_TYPE) 
            # Embed
            #bw_img_path = f"emb/bw/{img}" # Path the images are saved to if specified
            #bw_img = bwm.embed(filename=bw_img_path).astype(np.uint8)
            # The image needs to be converted to uint8 since its pixels are float32 after the embedding
            bw_img = bwm.embed().astype(np.uint8)
            
            #bw_img = cv.imread(bw_img_path,cv.IMREAD_COLOR)
            
            # Compute energy consumption
            BW_enCons = energyConsumption(bw_img)
            BWarr_enCons.append(BW_enCons)
        
            if DEBUG_BW:
                titles = ['Original image','Image w/Embedded WM']
                imgs = [img_bgr,bw_img]
                imgsPlot(imgs,titles,"Images comparison [DCT+SVD (BW)]")

                # Extract
                if WM_TYPE == 'img':
                    #bw_extrwm_path = f"extrWm/bw/{resized_wm}"
                    #bw_wm = bwm.extract(filename=bw_img_path, wm_shape=(wm_size, wm_size), out_wm_name=bw_extrwm_path, mode=WM_TYPE).astype(np.uint8)
                    
                    # NOTE: modified the library as follows at lines 108-109 to avoid writing the extracted wm
                    #       if out_wm_name is not None:
                    #            cv2.imwrite(out_wm_name, wm)
                    bw_wm = bwm.extract(embed_img=bw_img, wm_shape=(wm_size, wm_size), mode=WM_TYPE).astype(np.uint8)

                    #bw_wm = cv.imread(bw_extrwm_path,cv.IMREAD_COLOR)
                    titles = ['Original watermark', 'Extracted watermark']
                    imgs = [wm,bw_wm]
                    imgsPlot(imgs,titles,"Watermark comparison [DCT+SVD (BW)]")
                else:
                    bw_wm = bwm.extract(embed_img=bw_img, wm_shape=len(bwm.wm_bit), mode=WM_TYPE)
                    print(f"Original WM: {wm}\nExtracted WM [DCT+SVD (BW)]: {bw_wm}")
                
                # Check if the wm are the same
                # NOTE: the extracted watermark is usually different because the 
                # extraction lowers its quality
                if not sameWm(wm,bw_wm,mode=WM_TYPE):
                    print("WARNING: original and extracted watermark are different")

                print(f"Original image energy cons. : {base_enCons}")
                print(f"Watermarked image energy cons. : {BW_enCons}")
                print(f"Energy consumption increase with watermark [DCT+SVD (BW)]: {(BW_enCons/base_enCons-1.0):.4}")
                
        
        ##### DWT and DCT based watermark #####
        if INV_WM:
            encoder = WatermarkEncoder()
            if WM_TYPE == 'img':
                # Wm functions of the invisible watermark library do not accept images as wm input
                iw_wm = wm.tobytes()
                # The library can work with array of bytes
            else:
                iw_wm = wm.encode('utf-8')
            
            # NOTE: the dwtDct algorithm has a serious limitation about the watermark length, I was able to
            # embed only 21 bytes
            # wm = "1234567891234567891234"

            # Configs
            # The color space the library works with is YUV
            # The 3 entries specify the scaling of each channel (Y,U,V)
            # If the scaling of a channel is 0, that channel is not used 
            # NOTE: I don't know how the 'dwtDctSvd' algorithm works so I am not able
            # to modify the scale without breaking the encoding/decoding
            # If the scale is modified the maximum watermark size for the Invisible Watermark library
            # computed at the beginning of the script may have to be changed accordingly
            scales = [0,36,0] 
            #print(len(iw_wm))
            
            encoder.set_watermark('bytes', iw_wm)
            iw_img = encoder.encode(img_bgr,'dwtDctSvd',scales=scales)
            #print(iw_vctr_wm)
            #print(len(iw_vctr_wm))
            
            # Compute energy consumption
            IW_enCons = energyConsumption(iw_img)
            IWarr_enCons.append(IW_enCons)

            if DEBUG_IW:
                titles = ['Original image','Image w/Embedded WM']
                imgs = [img_bgr,iw_img]
                imgsPlot(imgs,titles,"Images comparison [DWT+DCT+SVD (IW)]")

                # Extract
                decoder = WatermarkDecoder('bytes',len(iw_wm)*8) # Length expressed in bits
                iw_vctr_wm = bytearray(decoder.decode(iw_img,'dwtDctSvd'))

                if WM_TYPE == 'img':
                    iw_wm = vector2image(iw_vctr_wm,wm_size,wm_size) # Restore image shape
                    
                    titles = ['Original watermark', 'Extracted watermark']
                    imgs = [wm,iw_wm]
                    imgsPlot(imgs,titles,"Watermark comparison [DWT+DCT+SVD (IW)]")
                else:
                    iw_wm = iw_wm.decode('utf-8')
                    print(f"Original WM: {wm}\nExtracted WM [DWT+DCT+SVD (IW)]: {iw_wm}")
                
                # Check if the wm are the same
                if not sameWm(wm,iw_wm,mode=WM_TYPE):
                    print("WARNING: original and extracted watermark are different")

                print(f"Original image energy cons. : {base_enCons}")
                print(f"Watermarked image energy cons. : {IW_enCons}")
                print(f"Energy consumption increase with watermark [DWT+DCT+SVD (IW)]: {(IW_enCons/base_enCons-1.0):.4}")

        if (DEBUG_BR and BIT_REPLACEMENT) or (DEBUG_BW and BLIND_WM) or (DEBUG_IW and INV_WM):
            plt.show()
            exit()
        
    # Data recording
    # NOTE: check plot.py before changing the data structure
    fp = open(SIM_RES_PATH+DATA_FILENAME,"w")
    json_data = {
        DATA_KEYS[0]: BRarr_enCons,
        DATA_KEYS[1]: BWarr_enCons,
        DATA_KEYS[2]: IWarr_enCons,
        DATA_KEYS[3]: BaseImgarr_enCons,
        DATA_KEYS[4]: Imgarr
    }
    json.dump(json_data,fp,cls=NumpyEncoder)
    fp.close()