from header import plt,json,np,os,DATA_KEYS,SIM_RES_PATH

# Number of entries related to energy consumption
# NOTE: the json data structure can be still modified keeping in mind that the code works
#   if the key ordering is {'algorithm1':[],'algorithm2':[],...,'algorithm3':[],'BaseImg':[],'Img':[]}
#   If the json structure cannot be changed without changing the above scheme then the code needs to be modified
ENERGY_DATA = len(DATA_KEYS)-1


def plotSimulationData(fn:str,simTitle:str="Simulation",show:bool=False):
    """ Elaborate energy consumption data and plot the results\n
    Parameters:
        fn: file name data have to be extracted from
        show: if True performs a plot.show(), if False just create a new figure with the given data\n
    Data have to be formatted in JSON with the format specified at the end of \"main.py\""""
    
    #json_data = {
    #    'BR': BRarr_enCons,
    #    'BW': BWarr_enCons,
    #    'IW': IWarr_enCons,
    #    'BaseImg': BaseImgarr_enCons,
    #    'Img': Imgarr
    #}

    with open(fn) as fp:
        simData = json.load(fp)

        ### Energy statistics computation

        # Minimum and maximum power consumption
        maxEnCons = {'energy':[],'img':[]}
        minEnCons = {'energy':[],'img':[]}
        for i in range(ENERGY_DATA):
            listEnCons = simData[DATA_KEYS[i]]
            
            maxEnCons['energy'].append(max(listEnCons))
            minEnCons['energy'].append(min(listEnCons))

            imgIndex = listEnCons.index(maxEnCons['energy'][i])
            maxEnCons['img'].append(simData[DATA_KEYS[-1]][imgIndex]+f"[{imgIndex}]")
            
            imgIndex = listEnCons.index(minEnCons['energy'][i])
            minEnCons['img'].append(simData[DATA_KEYS[-1]][imgIndex]+f"[{imgIndex}]")
                
        # Percentage variation of algorithms energy consumption w.r.t. the base image consumption
        # and average energy consumption
        percVariationsEnCons = []   # List of ENERGY_DATA-1 lists
        maxVar = {'energy':[],'img':[]}
        minVar = {'energy':[],'img':[]}
        avgEnCons = [np.int64(0)]*ENERGY_DATA
        
        baseImgsIndex=ENERGY_DATA-1
        for i in range(ENERGY_DATA-1):
            percVariationsEnCons.append([])
            minVar['energy'].append(0)
            maxVar['energy'].append(0)
            minVar['img'].append("No energy variation")
            maxVar['img'].append("No energy variation")
        
        baseImgsEnCons = simData[DATA_KEYS[baseImgsIndex]]
        for i in range(len(baseImgsEnCons)):
            avgEnCons[baseImgsIndex] += baseImgsEnCons[i] # Accumulate energy consumption for base images
            for algo in range(ENERGY_DATA-1):
                perVar = (simData[DATA_KEYS[algo]][i]-baseImgsEnCons[i])/baseImgsEnCons[i]*100
                # Average consumption (for watermarking algorithms)
                avgEnCons[algo] += np.int64(simData[DATA_KEYS[algo]][i])
                # Minimum and maximum variations
                percVariationsEnCons[algo].append(perVar) # Record % variation w.r.t. base image
                if(perVar < minVar['energy'][algo]): # Min %
                    minVar['energy'][algo] = perVar
                    minVar['img'][algo] = simData[DATA_KEYS[-1]][i]+f"[{i}]"
                if(perVar > maxVar['energy'][algo]): # Max %
                    maxVar['energy'][algo] = perVar
                    maxVar['img'][algo] = simData[DATA_KEYS[-1]][i]+f"[{i}]"
        
        avgEnCons = [round(enCons/len(baseImgsEnCons)) for enCons in avgEnCons]
        # Average energy consumption % variation w.r.t. base images 
        avgEnConsVar = [0]*(len(avgEnCons)-1)
        avgEnConsVar = [round((avgEnCons[i]-avgEnCons[baseImgsIndex])/avgEnCons[baseImgsIndex]*100,4) for i in range(ENERGY_DATA-1)]
        
        # Plot energy consumption
        plt.figure()
        plt.title(f"{simTitle}\nEnergy consumption per image")
        plt.ylabel("Energy consumption [number of transitions on a serial line]")
        plt.xlabel("Images position in simData['img']")
        for i in range(ENERGY_DATA):
            plt.plot(simData[DATA_KEYS[i]],label=DATA_KEYS[i])
        plt.legend(loc="upper right")

        # Print avg energy cons.
        print(f"### {simTitle} ###")
        print(">>> Average energy consumption [#transitions]")
        for i in range(ENERGY_DATA):
            print(f"- {DATA_KEYS[i]} : {avgEnCons[i]}")

        # Plot and print max/min energy cons.
        title = "Minimum and Maximum energy consumption"
        print(f">>> {title} [#transitions]")
        fig, axs = plt.subplots(1,2)
        fig.suptitle(f"{simTitle}\n{title}")
        titles = ['Minium energy cons.',"Maximum energy cons."]
        to_plot = [minEnCons,maxEnCons]
        for i in range(2):
            print(f"# {titles[i]}")
            for j in range(ENERGY_DATA):
                print(f"- {DATA_KEYS[j]} : {to_plot[i]['energy'][j]} [{to_plot[i]['img'][j]}]")
                axs[i].plot(to_plot[i]['img'][j],to_plot[i]['energy'][j],'v',label=DATA_KEYS[j])
            axs[i].set_title(titles[i])
            axs[i].legend()
        
        # Print avg energy cons. variation
        print(">>> Average energy consumption % variation w.r.t. basic images")
        for i in range(ENERGY_DATA-1):
            print(f"- {DATA_KEYS[i]} : {avgEnConsVar[i]} %")

        # Plot energy cons. variation
        plt.figure()
        plt.title(f"{simTitle}\nPercentage variation w.r.t. the base image [negative values mean less energy consumption]")
        plt.ylabel("% variation w.r.t. the base image energy consumption")
        plt.xlabel("Images position in simData['img']")
        for i in range(ENERGY_DATA-1):
            plt.plot(percVariationsEnCons[i],label=DATA_KEYS[i])
        plt.legend()
        
        # Print and plot min/max energy cons. variation
        title = "Maximum positive/negative energy consumption variation w.r.t. the base images"
        print(f">>> {title}")
        fig, axs = plt.subplots(1,2)
        fig.suptitle(f"{simTitle}\n{title}")
        titles = ['Maximum negative variations',"Maximum positive variations"]
        to_plot = [minVar,maxVar]
        for i in range(2):
            print(f"# {titles[i]}")
            for j in range(ENERGY_DATA-1):
                print(f"- {DATA_KEYS[j]} : {to_plot[i]['energy'][j]:.2} % [{to_plot[i]['img'][j]}]")
                axs[i].plot(to_plot[i]['img'][j],to_plot[i]['energy'][j],'v',label=DATA_KEYS[j])
            axs[i].set_title(titles[i])
            axs[i].legend()
        
        if show:
            plt.show()


if __name__ == "__main__":

    print("Select the file you want to analyze:")
    simfiles = os.listdir(SIM_RES_PATH)
    for i in range(len(simfiles)):
        print(f"{i+1}) {simfiles[i]}")
    print("> Press ENTER to exit")
    print("NOTE: Enter multiple indexes to plot multiple files at once (ex. \"1 2\" for selecting file 1 and 2)")
    print("> Select file [write the corresponding index]: ",end="")
    inp = input()
    print("IMPORTANT: Close all the windows to analyze other files")
    while inp != "":
        inp = inp.split()
        try:
            for file in inp:
                file = int(file)-1
                plotSimulationData(SIM_RES_PATH+simfiles[file],simTitle=simfiles[file],show=False)
            plt.show()
        except Exception as e:
            print(e)
            print("ERROR: Input value not valid")
        
        print("> Select file: ",end="")
        inp = input()
        